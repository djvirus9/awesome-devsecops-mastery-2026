import argparse
import os
from pathlib import Path
import stat
import sys


MAX_INPUT_BYTES = 1024 * 1024


class InputError(ValueError):
    """A concise input error that can be reported without a traceback."""


def check_regular_file(metadata) -> None:
    if not stat.S_ISREG(metadata.st_mode):
        raise InputError("Input must be a regular file; directories, links, and special files are unsupported")
    if metadata.st_size > MAX_INPUT_BYTES:
        raise InputError(f"Input file exceeds {MAX_INPUT_BYTES} bytes (1 MiB)")


def read_input(path: Path) -> str:
    """Read at most the limit plus one byte, including when a file grows during reading."""
    try:
        # Reject special files before opening, then check the opened descriptor too.
        check_regular_file(path.lstat())
        flags = os.O_RDONLY | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_NOFOLLOW", 0)
        flags |= getattr(os, "O_BINARY", 0)
        descriptor = os.open(path, flags)
        with os.fdopen(descriptor, "rb") as source:
            check_regular_file(os.fstat(source.fileno()))
            data = source.read(MAX_INPUT_BYTES + 1)
    except FileNotFoundError:
        raise InputError("Input file does not exist") from None
    except PermissionError:
        raise InputError("Input file is not readable; check file and directory permissions") from None
    except OSError:
        raise InputError("Input file could not be read") from None

    if len(data) > MAX_INPUT_BYTES:
        raise InputError(f"Input file exceeds {MAX_INPUT_BYTES} bytes (1 MiB)")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        raise InputError("Input file must contain valid UTF-8 text") from None


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Print a UTF-8 input file, up to 1 MiB")
    parser.add_argument("--input", required=True, type=Path, help="Path to a regular UTF-8 file")
    args = parser.parse_args(argv)
    try:
        contents = read_input(args.input)
    except InputError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    print(contents.strip())
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
