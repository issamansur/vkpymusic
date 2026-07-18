import os
import re
import shutil
import tempfile
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urljoin

import av
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from curl_cffi import requests


@dataclass(frozen=True)
class HlsResource:
    url: str
    byte_range: Optional[tuple[int, int]] = None
    key_url: Optional[str] = None
    iv: Optional[bytes] = None


@dataclass(frozen=True)
class HlsKey:
    url: str
    iv: Optional[bytes] = None


def parse_m3u8(url: str) -> list[HlsResource]:
    """Fetch an m3u8 playlist and return ordered media resources."""
    return _parse_playlist(url, _fetch_playlist(url), set())


def download_m3u8(url: str, output_path: str) -> None:
    """Download m3u8 media resources and write them to a single media file."""
    resources = parse_m3u8(url)
    keys: dict[str, bytes] = {}
    with open(output_path, "wb") as output_file:
        for resource in resources:
            headers = {}
            if resource.byte_range is not None:
                start, end = resource.byte_range
                headers["Range"] = f"bytes={start}-{end}"

            response = requests.get(resource.url, headers=headers, timeout=10)
            response.raise_for_status()
            content = response.content
            if resource.key_url is not None:
                if resource.key_url not in keys:
                    keys[resource.key_url] = _fetch_key(resource.key_url)
                key = keys[resource.key_url]
                content = _decrypt_aes_128(content, key, resource.iv)
            output_file.write(content)


def download_m3u8_as_mp3_pyav(url: str, output_path: str) -> None:
    """Download m3u8 stream and convert to mp3 using PyAV (no ffmpeg CLI required).

    Args:
        url (str): URL of the m3u8 playlist.
        output_path (str): Path to the output mp3 file.
    """
    with tempfile.NamedTemporaryFile(suffix=".media", delete=False) as tmp:
        tmp_path = tmp.name

    transcode_succeeded = False
    try:
        download_m3u8(url, tmp_path)
        _transcode_media_to_mp3(tmp_path, output_path)
        transcode_succeeded = True
    except Exception as e:
        signature = _file_signature(tmp_path)
        raise RuntimeError(
            "Could not transcode assembled m3u8 media. "
            f"Temporary media file kept at '{tmp_path}' "
            f"(size={os.path.getsize(tmp_path)} bytes, signature={signature}). "
            f"Original error: {e}"
        ) from e
    finally:
        if transcode_succeeded and os.path.exists(tmp_path):
            os.remove(tmp_path)


def _transcode_media_to_mp3(input_path: str, output_path: str) -> None:
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp_output_path = tmp.name

    try:
        with av.open(input_path) as inp:
            with av.open(tmp_output_path, "w", format="mp3") as out:
                _encode_audio_frames(_decode_audio_frames(inp), out)
        shutil.move(tmp_output_path, output_path)
    finally:
        if os.path.exists(tmp_output_path):
            os.remove(tmp_output_path)


def _decode_audio_frames(container):
    audio_stream = container.streams.audio[0]
    for packet in container.demux(audio_stream):
        try:
            yield from packet.decode()
        except Exception:
            continue


def _encode_audio_frames(frames, out) -> None:
    out_stream = out.add_stream("libmp3lame", rate=44100)
    for frame in frames:
        frame.pts = None
        for packet in out_stream.encode(frame):
            out.mux(packet)
    for packet in out_stream.encode(None):
        out.mux(packet)


def _file_signature(path: str) -> str:
    if not os.path.exists(path):
        return "missing"
    with open(path, "rb") as media_file:
        return media_file.read(32).hex()


def _fetch_playlist(url: str) -> str:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.text


def _parse_playlist(
    url: str, playlist: str, visited_urls: set[str]
) -> list[HlsResource]:
    if url in visited_urls:
        raise ValueError(f"Recursive m3u8 playlist detected: {url}")
    visited_urls.add(url)

    media_resources: list[HlsResource] = []
    variants: list[tuple[int, str]] = []
    pending_variant_bandwidth: Optional[int] = None
    pending_byte_range: Optional[str] = None
    current_map: Optional[HlsResource] = None
    last_map: Optional[HlsResource] = None
    current_key: Optional[HlsKey] = None
    media_sequence = 0
    byte_range_offsets: dict[str, int] = {}

    for raw_line in playlist.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith("#EXT-X-KEY"):
            attrs = _parse_attrs(line)
            method = attrs.get("METHOD", "NONE").upper()
            if method == "NONE":
                current_key = None
                continue
            if method != "AES-128":
                raise ValueError(f"Unsupported m3u8 encryption method: {method}")
            if attrs.get("KEYFORMAT", "identity") != "identity":
                raise ValueError("Unsupported m3u8 key format")
            key_uri = attrs.get("URI")
            if key_uri is None:
                raise ValueError("m3u8 EXT-X-KEY tag is missing URI")
            current_key = HlsKey(urljoin(url, key_uri), _parse_iv(attrs.get("IV")))
            continue

        if line.startswith("#EXT-X-MEDIA-SEQUENCE"):
            media_sequence = int(line.split(":", 1)[1])
            continue

        if line.startswith("#EXT-X-STREAM-INF"):
            attrs = _parse_attrs(line)
            pending_variant_bandwidth = int(attrs.get("BANDWIDTH", "0"))
            continue

        if line.startswith("#EXT-X-MAP"):
            attrs = _parse_attrs(line)
            map_uri = attrs.get("URI")
            if map_uri is None:
                raise ValueError("m3u8 EXT-X-MAP tag is missing URI")
            map_url = urljoin(url, map_uri)
            key_url = None
            iv = None
            if current_key is not None:
                if current_key.iv is None:
                    raise ValueError("Encrypted m3u8 init maps require an explicit IV")
                key_url = current_key.url
                iv = current_key.iv
            current_map = HlsResource(
                map_url,
                _parse_byte_range(attrs.get("BYTERANGE"), map_url, byte_range_offsets),
                key_url,
                iv,
            )
            continue

        if line.startswith("#EXT-X-BYTERANGE"):
            pending_byte_range = line.split(":", 1)[1]
            continue

        if line.startswith("#"):
            continue

        resource_url = urljoin(url, line)
        if pending_variant_bandwidth is not None:
            variants.append((pending_variant_bandwidth, resource_url))
            pending_variant_bandwidth = None
            continue

        if current_map is not None and current_map != last_map:
            media_resources.append(current_map)
            last_map = current_map

        media_resources.append(
            HlsResource(
                resource_url,
                _parse_byte_range(
                    pending_byte_range, resource_url, byte_range_offsets
                ),
                current_key.url if current_key is not None else None,
                _resource_iv(current_key, media_sequence),
            )
        )
        media_sequence += 1
        pending_byte_range = None

    if variants:
        _, variant_url = max(variants, key=lambda variant: variant[0])
        return _parse_playlist(variant_url, _fetch_playlist(variant_url), visited_urls)

    return media_resources


def _fetch_key(url: str) -> bytes:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.content


def _parse_attrs(line: str) -> dict[str, str]:
    _, value = line.split(":", 1)
    attrs = {}
    for match in re.finditer(r'([A-Z0-9-]+)=("[^"]*"|[^,]*)', value):
        attrs[match.group(1)] = match.group(2).strip('"')
    return attrs


def _parse_byte_range(
    value: Optional[str], url: str, byte_range_offsets: dict[str, int]
) -> Optional[tuple[int, int]]:
    if value is None:
        return None

    length_text, _, offset_text = value.partition("@")
    length = int(length_text)
    offset = int(offset_text) if offset_text else byte_range_offsets.get(url, 0)
    byte_range_offsets[url] = offset + length
    return offset, offset + length - 1


def _parse_iv(value: Optional[str]) -> Optional[bytes]:
    if value is None:
        return None
    value = value.removeprefix("0x").removeprefix("0X")
    return bytes.fromhex(value.zfill(32))


def _resource_iv(key: Optional[HlsKey], media_sequence: int) -> Optional[bytes]:
    if key is None:
        return None
    return key.iv or media_sequence.to_bytes(16, "big")


def _decrypt_aes_128(content: bytes, key: bytes, iv: Optional[bytes]) -> bytes:
    if iv is None:
        raise ValueError("Encrypted m3u8 resource is missing IV")

    decryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
    decrypted = decryptor.update(content) + decryptor.finalize()
    padding_length = decrypted[-1]
    if padding_length < 1 or padding_length > 16:
        return decrypted
    if decrypted[-padding_length:] != bytes([padding_length]) * padding_length:
        raise ValueError("Invalid PKCS7 padding")
    return decrypted[:-padding_length]
