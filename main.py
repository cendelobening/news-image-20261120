#!/usr/bin/env python3
"""Validate entry.png and deliver it to the output directory.

Reads entry.png from this script's own directory, checks that it is a
well-formed 1024x1024, 8-bit RGB PNG under 1 MiB with valid chunk CRCs
and a decodable image body, then copies it byte-for-byte to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output) with mode 0644.
No network access, no randomness, fully deterministic.
"""

import binascii
import os
import struct
import sys
import zlib

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024
EXPECTED_DEPTH = 8
EXPECTED_COLOUR_TYPE = 2  # truecolour RGB
MAX_FILE_BYTES = 1024 * 1024
DEFAULT_OUTPUT_DIR = "/output"
OUTPUT_NAME = "entry.png"
SOURCE_NAME = "entry.png"


class ImageError(ValueError):
    """Raised when entry.png fails any validation check."""


def _check_crc(tag, payload, stored_crc):
    actual = binascii.crc32(tag + payload) & 0xFFFFFFFF
    if actual != stored_crc:
        raise ImageError("bad CRC on {} chunk".format(tag.decode("ascii")))


def _read_chunks(data):
    """Yield (tag, payload) for every chunk after the PNG signature."""
    if data[:8] != PNG_SIGNATURE:
        raise ImageError("missing PNG signature")
    pos = 8
    while pos < len(data):
        if pos + 8 > len(data):
            raise ImageError("truncated chunk header")
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        tag = data[pos + 4:pos + 8]
        end = pos + 8 + length + 4
        if end > len(data):
            raise ImageError("truncated {} chunk".format(tag.decode("ascii")))
        payload = data[pos + 8:pos + 8 + length]
        stored = struct.unpack(">I", data[pos + 8 + length:end])[0]
        _check_crc(tag, payload, stored)
        yield tag, payload
        pos = end
        if tag == b"IEND":
            break
    if pos != len(data):
        raise ImageError("trailing bytes after IEND")


def validate_png(path):
    """Read and fully validate the PNG; return its raw bytes."""
    with open(path, "rb") as handle:
        data = handle.read()
    if len(data) > MAX_FILE_BYTES:
        raise ImageError("file is {} bytes, over the 1 MiB limit".format(len(data)))
    chunks = list(_read_chunks(data))
    if not chunks or chunks[0][0] != b"IHDR":
        raise ImageError("first chunk is not IHDR")
    header = chunks[0][1]
    if len(header) != 13:
        raise ImageError("IHDR is {} bytes, expected 13".format(len(header)))
    width, height, depth, colour, comp, filt, interlace = struct.unpack(
        ">IIBBBBB", header)
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        raise ImageError("size is {}x{}, expected 1024x1024".format(width, height))
    if depth != EXPECTED_DEPTH or colour != EXPECTED_COLOUR_TYPE:
        raise ImageError("expected 8-bit RGB, got depth {} colour {}".format(
            depth, colour))
    if comp != 0 or filt != 0 or interlace != 0:
        raise ImageError("unexpected compression/filter/interlace flags")
    idat = b"".join(payload for tag, payload in chunks if tag == b"IDAT")
    if not idat:
        raise ImageError("no IDAT data found")
    try:
        raw = zlib.decompress(idat)
    except zlib.error as exc:
        raise ImageError("IDAT does not decompress: {}".format(exc))
    stride = EXPECTED_WIDTH * 3
    expected_raw = EXPECTED_HEIGHT * (stride + 1)
    if len(raw) != expected_raw:
        raise ImageError("decoded image is {} bytes, expected {}".format(
            len(raw), expected_raw))
    for row in range(EXPECTED_HEIGHT):
        if raw[row * (stride + 1)] != 0:
            raise ImageError("scanline {} uses an unsupported filter".format(row))
    return data


def resolve_output_dir():
    """Output directory from the environment, falling back to /output."""
    return os.environ.get("MAKEFUN_OUTPUT_DIR", DEFAULT_OUTPUT_DIR)


def deliver(data, out_dir):
    """Write the validated bytes to the output directory, mode 0644."""
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, OUTPUT_NAME)
    with open(target, "wb") as handle:
        handle.write(data)
    os.chmod(target, 0o644)
    return target


def main(argv):
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, SOURCE_NAME)
    out_dir = resolve_output_dir()
    try:
        data = validate_png(source)
    except (OSError, ImageError) as exc:
        print("error: {}: {}".format(source, exc), file=sys.stderr)
        return 1
    target = deliver(data, out_dir)
    print("wrote {} ({} bytes, mode 0644)".format(target, len(data)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
