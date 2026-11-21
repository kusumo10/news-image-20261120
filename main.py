"""Entry program for make.fun bounty "news-image-20261120".

Sums up the world's news of Friday 20 November 2026 in one image.

The program holds the finished front-page image (entry.png) in this
repository and copies it, byte for byte, to the output directory as
entry.png. It performs no network access and writes nothing else, so
two runs always produce identical bytes.

The image itself is a newspaper front page drawn in this session:
masthead "FRIDAY, 20 NOVEMBER 2026" plus six panels covering the
day's biggest stories across regions and fields:

  1. Summit in Shenzhen - Trump, Xi and Putin sign a joint peace
     declaration.
  2. Missiles fall on Poland - Russian missiles crash in Poland;
     NATO jets scrambled.
  3. Genocide verdict - the World Court finds Myanmar guilty over
     the Rohingya.
  4. Markets plunge - S&P 500 falls 3.7%; Nikkei down 5.1%.
  5. Climate deadlock - COP31 talks stall over fossil fuels.
  6. Measles returns - the US loses elimination status held
     since 2000.

Usage:
    MAKEFUN_OUTPUT_DIR=out python3 main.py

The output directory defaults to /output when the environment
variable is not set.
"""

import os
import struct
import sys

# Limits from the competition rules: at most 1 MiB, at most 1024x1024.
MAX_BYTES = 1_048_576
MAX_DIMENSION = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
SOURCE_NAME = "entry.png"


def source_path():
    """Absolute path of the image bundled next to this script."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, SOURCE_NAME)


def read_source(path):
    """Read the bundled image, failing loudly if it is missing."""
    if not os.path.isfile(path):
        raise FileNotFoundError("bundled image not found: %s" % path)
    with open(path, "rb") as handle:
        return handle.read()


def png_dimensions(data):
    """Return (width, height) parsed from a PNG IHDR chunk.

    Raises ValueError when the bytes are not a PNG or the header
    is truncated.
    """
    if data[:8] != PNG_MAGIC:
        raise ValueError("not a PNG file: bad magic bytes")
    if len(data) < 24:
        raise ValueError("not a PNG file: header too short")
    chunk_length, chunk_type = struct.unpack(">I4s", data[8:16])
    if chunk_type != b"IHDR" or chunk_length != 13:
        raise ValueError("not a PNG file: first chunk is not IHDR")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def validate(data):
    """Check the image against the competition limits.

    Returns (width, height). Raises ValueError on any violation.
    """
    if len(data) > MAX_BYTES:
        raise ValueError(
            "image is %d bytes, over the %d byte limit"
            % (len(data), MAX_BYTES)
        )
    width, height = png_dimensions(data)
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise ValueError(
            "image is %dx%d, over the %d pixel limit"
            % (width, height, MAX_DIMENSION)
        )
    if width <= 0 or height <= 0:
        raise ValueError("image has non-positive dimensions")
    return width, height


def output_dir():
    """Output directory from the environment, defaulting to /output."""
    return os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")


def write_entry(data, directory):
    """Write the image bytes to <directory>/entry.png.

    Reads the file back and compares bytes so a partial or
    corrupted write is caught instead of silently submitted.
    """
    os.makedirs(directory, exist_ok=True)
    target = os.path.join(directory, SOURCE_NAME)
    with open(target, "wb") as handle:
        handle.write(data)
    with open(target, "rb") as handle:
        written = handle.read()
    if written != data:
        raise ValueError("written file differs from source bytes")
    return target


def main(argv=None):
    """Copy the bundled front page to the output directory."""
    data = read_source(source_path())
    width, height = validate(data)
    target = write_entry(data, output_dir())
    print(
        "wrote %s (%dx%d, %d bytes)"
        % (target, width, height, len(data))
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
