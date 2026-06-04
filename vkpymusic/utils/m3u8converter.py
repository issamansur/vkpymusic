import os
import tempfile
from urllib.parse import urljoin

import av
from curl_cffi import requests


def parse_m3u8(url: str) -> list[str]:
    """Fetch an m3u8 playlist and return a list of absolute segment URLs.

    Args:
        url (str): URL of the m3u8 playlist.

    Returns:
        list[str]: List of absolute segment URLs.
    """
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    segments = []
    for line in response.text.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            segments.append(urljoin(url, line))

    return segments


def download_m3u8(url: str, output_path: str) -> None:
    """Download all segments from an m3u8 playlist and write them to a file.

    Args:
        url (str): URL of the m3u8 playlist.
        output_path (str): Path to the output file.
    """
    segments = parse_m3u8(url)
    with open(output_path, "wb") as f:
        for segment_url in segments:
            response = requests.get(segment_url, timeout=10)
            response.raise_for_status()
            f.write(response.content)


def download_m3u8_as_mp3_pyav(url: str, output_path: str) -> None:
    """Download m3u8 stream and convert to mp3 using PyAV (no ffmpeg CLI required).

    Args:
        url (str): URL of the m3u8 playlist.
        output_path (str): Path to the output mp3 file.
    """
    with tempfile.NamedTemporaryFile(suffix=".ts", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        download_m3u8(url, tmp_path)
        with av.open(tmp_path) as inp:
            with av.open(output_path, "w", format="mp3") as out:
                out_stream = out.add_stream("libmp3lame", rate=44100)
                for frame in inp.decode(audio=0):
                    frame.pts = None
                    for packet in out_stream.encode(frame):
                        out.mux(packet)
                for packet in out_stream.encode(None):
                    out.mux(packet)
    finally:
        os.remove(tmp_path)
