"""CLI for running DostLang source files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .dostlang import DostLangError, run_source


def main() -> int:
    parser = argparse.ArgumentParser(description="Run DostLang source code.")
    parser.add_argument("file", nargs="?", help="Path to .dost source file")
    parser.add_argument(
        "-c",
        "--code",
        help="Run source code passed directly as a string",
    )
    args = parser.parse_args()

    if not args.file and not args.code:
        parser.error("Provide a source file or --code input.")

    if args.code:
        source = args.code
    else:
        source_path = Path(args.file)
        try:
            source = source_path.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"error: unable to read '{source_path}': {exc}", file=sys.stderr)
            return 1

    try:
        result = run_source(source)
    except DostLangError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    for line in result.output:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
