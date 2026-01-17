import argparse
from pathlib import Path

def main() -> None:
    parser = argparse.ArgumentParser(description="Sample CLI")
    parser.add_argument("--input", required=True, help="Input file path")
    args = parser.parse_args()

    path = Path(args.input)
    if not path.exists():
        raise SystemExit("Input file does not exist")

    print(path.read_text().strip())

if __name__ == "__main__":
    main()
