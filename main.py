#!/usr/bin/env python3
"""Entrypoint for the 20 November 2026 news front page.

Reads entry.png from this directory, checks it is a well-formed
1024x1024 PNG of at most 1 MiB whose pixel data decodes cleanly,
then writes an exact copy to $MAKEFUN_OUTPUT_DIR/entry.png
(default /output) with mode 0644.

Standard library only. No network access. Deterministic: repeated
runs write identical bytes.
"""
import hashlib
import os
import struct
import sys
import zlib

LIMIT_BYTES = 1048576
SIDE = 1024
SIGNATURE = b"\x89PNG\r\n\x1a\n"


class BadEntry(Exception):
    """Raised when entry.png fails a validation check."""


def iter_chunks(data):
    """Yield (type, body) for every chunk in order.

    Each chunk's CRC is verified against its stored value, the first
    chunk must be a 13-byte IHDR, and nothing may follow IEND.
    Raises BadEntry on any flaw.
    """
    if data[:8] != SIGNATURE:
        raise BadEntry("missing PNG signature")
    if len(data) < 8 + 25:
        raise BadEntry("file too short for an IHDR chunk")
    offset = 8
    first = True
    while offset + 8 <= len(data):
        size, kind = struct.unpack_from(">I4s", data, offset)
        if first:
            if kind != b"IHDR" or size != 13:
                raise BadEntry("first chunk is not a 13-byte IHDR")
            first = False
        stop = offset + 12 + size
        if stop > len(data):
            raise BadEntry("chunk %r is truncated"
                           % kind.decode("ascii", "replace"))
        body = data[offset + 8:offset + 8 + size]
        want, = struct.unpack_from(">I", data, offset + 8 + size)
        got = zlib.crc32(kind + body) & 0xFFFFFFFF
        if want != got:
            raise BadEntry("CRC mismatch in %r chunk"
                           % kind.decode("ascii", "replace"))
        yield kind, body
        if kind == b"IEND":
            if stop != len(data):
                raise BadEntry("bytes follow the IEND chunk")
            return
        offset = stop
    raise BadEntry("no IEND chunk found")


def check_dimensions(data):
    """Check the IHDR size fields; return (width, height)."""
    width, height = struct.unpack_from(">II", data, 16)
    if (width, height) != (SIDE, SIDE):
        raise BadEntry("entry.png is %dx%d, expected 1024x1024"
                       % (width, height))
    bit_depth, color_type = data[24], data[25]
    if (bit_depth, color_type) != (8, 2):
        raise BadEntry("IHDR says bit depth %d, color type %d; "
                       "expected 8-bit RGB" % (bit_depth, color_type))
    return width, height


def validate(data):
    """Check size, dimensions and decodability; return (width, height)."""
    if len(data) > LIMIT_BYTES:
        raise BadEntry("entry.png is %d bytes, over the 1 MiB limit"
                       % len(data))
    width, height = check_dimensions(data)
    payload = bytearray()
    saw_iend = False
    for kind, body in iter_chunks(data):
        if kind == b"IDAT":
            payload += body
        elif kind == b"IEND":
            saw_iend = True
    if not saw_iend:
        raise BadEntry("no IEND chunk found")
    if not payload:
        raise BadEntry("no IDAT chunk found")
    try:
        pixels = zlib.decompress(bytes(payload))
    except zlib.error:
        raise BadEntry("IDAT data does not decompress")
    expect = SIDE * (1 + SIDE * 3)
    if len(pixels) != expect:
        raise BadEntry("decoded to %d bytes, expected %d"
                       % (len(pixels), expect))
    return width, height


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    try:
        with open(source, "rb") as handle:
            data = handle.read()
    except OSError:
        print("error: entry.png not found next to main.py", file=sys.stderr)
        raise SystemExit(1)
    try:
        width, height = validate(data)
    except BadEntry as exc:
        print("error: " + str(exc), file=sys.stderr)
        raise SystemExit(1)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError as exc:
        print("error: cannot create %s: %s" % (out_dir, exc),
              file=sys.stderr)
        raise SystemExit(1)
    target = os.path.join(out_dir, "entry.png")
    with open(target, "wb") as handle:
        handle.write(data)
    # The grader reads the output as an unprivileged user, so the
    # file must be world-readable regardless of the caller's umask.
    os.chmod(target, 0o644)
    written_mode = os.stat(target).st_mode & 0o777
    if written_mode != 0o644:
        print("error: output mode is %03o, expected 0644" % written_mode,
              file=sys.stderr)
        raise SystemExit(1)
    with open(target, "rb") as handle:
        if handle.read() != data:
            print("error: written output differs from entry.png",
                  file=sys.stderr)
            raise SystemExit(1)
    digest = hashlib.sha256(data).hexdigest()
    print("wrote %s (%d bytes, %dx%d, sha256 %s)"
          % (target, len(data), width, height, digest))


if __name__ == "__main__":
    main()
