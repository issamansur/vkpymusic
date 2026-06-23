import importlib.util
import pathlib
import sys
import tempfile
import types
import unittest

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


class Response:
    def __init__(self, *, text="", content=b""):
        self.text = text
        self.content = content

    def raise_for_status(self):
        return None


class Frame:
    pts = 123


class Packet:
    def __init__(self, frame=None, decode_error=None):
        self.frame = frame
        self.decode_error = decode_error

    def decode(self):
        if self.decode_error is not None:
            raise self.decode_error
        return [self.frame]


class Stream:
    def encode(self, frame):
        if frame is None:
            return ["flush-packet"]
        return ["frame-packet"]


class InputContainer:
    def __init__(self, path, captured_input):
        self.frames = [Frame()]
        self.streams = types.SimpleNamespace(audio=[object()])
        with open(path, "rb") as input_file:
            captured_input.append(input_file.read())

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def demux(self, stream):
        return iter([Packet(decode_error=ValueError("bad packet")), Packet(self.frames[0])])


class OutputContainer:
    def __init__(self):
        self.stream = Stream()
        self.muxed_packets = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def add_stream(self, codec, rate):
        self.codec = codec
        self.rate = rate
        return self.stream

    def mux(self, packet):
        self.muxed_packets.append(packet)


class M3u8ConverterTest(unittest.TestCase):
    def test_downloads_maps_and_byte_range_segments_before_transcoding(self):
        requests_module = types.SimpleNamespace()
        requests = []
        playlists = {
            "https://example.com/index.m3u8": """
#EXTM3U
#EXT-X-STREAM-INF:BANDWIDTH=128000
low/audio.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=320000
hi/audio.m3u8
""",
            "https://example.com/hi/audio.m3u8": """
#EXTM3U
#EXT-X-MAP:URI="init.mp4",BYTERANGE="4@0"
#EXTINF:10,
#EXT-X-BYTERANGE:5@4
media.mp4
#EXTINF:10,
#EXT-X-BYTERANGE:5
media.mp4
""",
        }
        media = {
            ("https://example.com/hi/init.mp4", "bytes=0-3"): b"init",
            ("https://example.com/hi/media.mp4", "bytes=4-8"): b"part1",
            ("https://example.com/hi/media.mp4", "bytes=9-13"): b"part2",
        }

        def get(url, headers=None, timeout=10):
            requests.append((url, headers or {}, timeout))
            if url in playlists:
                return Response(text=playlists[url])
            return Response(content=media[(url, headers["Range"])])

        requests_module.get = get

        curl_cffi_module = types.ModuleType("curl_cffi")
        curl_cffi_module.requests = requests_module
        sys.modules["curl_cffi"] = curl_cffi_module

        captured_input = []
        output_container = OutputContainer()
        av_module = types.ModuleType("av")

        def open_container(*args, **kwargs):
            if args[0].endswith(".mp3"):
                return output_container
            return InputContainer(args[0], captured_input)

        av_module.open = open_container
        sys.modules["av"] = av_module

        converter = self._load_converter()
        with tempfile.NamedTemporaryFile(suffix=".mp3") as output_file:
            converter.download_m3u8_as_mp3_pyav(
                "https://example.com/index.m3u8", output_file.name
            )

        self.assertEqual(captured_input, [b"initpart1part2"])
        self.assertEqual(
            requests,
            [
                ("https://example.com/index.m3u8", {}, 10),
                ("https://example.com/hi/audio.m3u8", {}, 10),
                (
                    "https://example.com/hi/init.mp4",
                    {"Range": "bytes=0-3"},
                    10,
                ),
                (
                    "https://example.com/hi/media.mp4",
                    {"Range": "bytes=4-8"},
                    10,
                ),
                (
                    "https://example.com/hi/media.mp4",
                    {"Range": "bytes=9-13"},
                    10,
                ),
            ],
        )
        self.assertEqual(output_container.codec, "libmp3lame")
        self.assertEqual(output_container.rate, 44100)
        self.assertEqual(
            output_container.muxed_packets,
            ["frame-packet", "flush-packet"],
        )

    def test_decrypts_aes_128_segments(self):
        requests_module = types.SimpleNamespace()
        key = b"0123456789abcdef"
        encrypted_segment = encrypt_aes_128(b"segment-data", key, (7).to_bytes(16, "big"))
        requests = []
        playlists = {
            "https://example.com/audio.m3u8": """
#EXTM3U
#EXT-X-MEDIA-SEQUENCE:7
#EXT-X-KEY:METHOD=AES-128,URI="key.bin"
#EXTINF:10,
segment.ts
""",
        }
        media = {
            "https://example.com/key.bin": key,
            "https://example.com/segment.ts": encrypted_segment,
        }

        def get(url, headers=None, timeout=10):
            requests.append((url, headers or {}, timeout))
            if url in playlists:
                return Response(text=playlists[url])
            return Response(content=media[url])

        requests_module.get = get

        curl_cffi_module = types.ModuleType("curl_cffi")
        curl_cffi_module.requests = requests_module
        sys.modules["curl_cffi"] = curl_cffi_module

        captured_input = []
        output_container = OutputContainer()
        av_module = types.ModuleType("av")

        def open_container(*args, **kwargs):
            if args[0].endswith(".mp3"):
                return output_container
            return InputContainer(args[0], captured_input)

        av_module.open = open_container
        sys.modules["av"] = av_module

        converter = self._load_converter()
        with tempfile.NamedTemporaryFile(suffix=".mp3") as output_file:
            converter.download_m3u8_as_mp3_pyav(
                "https://example.com/audio.m3u8", output_file.name
            )

        self.assertEqual(captured_input, [b"segment-data"])
        self.assertEqual(
            requests,
            [
                ("https://example.com/audio.m3u8", {}, 10),
                ("https://example.com/segment.ts", {}, 10),
                ("https://example.com/key.bin", {}, 10),
            ],
        )

    def _load_converter(self):
        module_path = (
            pathlib.Path(__file__).resolve().parents[1]
            / "vkpymusic"
            / "utils"
            / "m3u8converter.py"
        )
        spec = importlib.util.spec_from_file_location("m3u8converter", module_path)
        converter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(converter)
        return converter


def encrypt_aes_128(content, key, iv):
    padding_length = 16 - (len(content) % 16)
    padded = content + bytes([padding_length]) * padding_length
    encryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    return encryptor.update(padded) + encryptor.finalize()


if __name__ == "__main__":
    unittest.main()
