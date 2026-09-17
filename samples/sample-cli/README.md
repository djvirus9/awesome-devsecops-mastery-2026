# Sample CLI

A small local text-printing command with bounded file input and concise errors. It uses only the Python standard library; Python 3.12 or newer is the repository baseline.

## Run

From the repository root:

```bash
python3 samples/sample-cli/main.py --input samples/sample-api/requirements.in
```

Expected output is the supplied file's text with leading/trailing whitespace removed and one final newline. The required `--input` interface and text-printing purpose are unchanged.

## Input and error contract

| Input/result | Behavior |
| --- | --- |
| Regular UTF-8 file up to 1,048,576 bytes (1 MiB) | Print stripped contents; exit 0. The bound is bytes, not characters. |
| Empty regular file | Print a newline; exit 0. |
| Missing or unreadable file | Concise explanation on stderr, no partial output or traceback; exit 1. |
| Directory, symbolic link, pipe, or other special file | Reject as unsupported input; exit 1. |
| Oversized file | Reject before output, including when metadata understates the current size; exit 1. |
| Invalid UTF-8 bytes | Reject before output; exit 1. |
| Missing `--input` or invalid command arguments | argparse usage/error message; exit 2. |

The filename extension does not change behavior: `.json` files are echoed as text and are not parsed or validated as JSON. The program checks the path before opening and the opened file descriptor afterward; the read itself is limited to the bound plus one byte. It performs no network calls or file modifications.

It prints the input content, so choose files appropriate for your terminal or output destination. This is a small local file-handling example, not a document-format validator.

## Verification and troubleshooting

```bash
make setup
.venv/bin/python -m unittest discover -s tests -p 'test_sample_cli.py' -v
```

The tests cover UTF-8 and whitespace preservation, extension-independent behavior, file types, nonblocking pipe rejection, unreadable inputs, exact/over-limit reads, and errors without tracebacks. They also run as part of `make test`.

For unreadable input, check file and parent-directory permissions. For UTF-8 errors, explicitly convert the source text using an appropriate editor/tool before retrying. For a symbolic link, select the intended regular file directly. No background process or generated application data needs cleanup.
