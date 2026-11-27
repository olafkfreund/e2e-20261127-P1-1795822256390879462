"""Command-line entry point and word frequency helpers for wordfreq."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9]+")
_STDIN_PATH = "-"
_PROG = "wordfreq"


def count_words(
    text: str,
    *,
    min_len: int = 1,
    ignore_case: bool = True,
    top: int | None = None,
) -> list[tuple[str, int]]:
    """Count word occurrences in *text* and return `(word, count)` pairs.

    Tokens are maximal ASCII alphanumeric runs. They are lowercased unless
    *ignore_case* is ``False``, filtered by *min_len*, and sorted by
    descending count then ascending word. *top* limits the number of pairs.
    """
    if min_len < 1:
        msg = "min_len must be >= 1"
        raise ValueError(msg)
    if top is not None and top < 0:
        msg = "top must be >= 0"
        raise ValueError(msg)

    tokens = _TOKEN_PATTERN.findall(text)
    if ignore_case:
        tokens = [token.lower() for token in tokens]
    counts = Counter(token for token in tokens if len(token) >= min_len)
    ranked = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    if top is not None:
        ranked = ranked[:top]
    return ranked


def format_table(rows: Sequence[tuple[str, int]]) -> str:
    """Format `(word, count)` pairs as tab-separated lines."""
    return "\n".join(f"{word}\t{count}" for word, count in rows)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=_PROG,
        description="Deterministically count and rank words in text.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=_STDIN_PATH,
        help="UTF-8 text file to read; '-' or omitted reads standard input.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=None,
        help="Only emit the N most frequent words (default: all).",
    )
    parser.add_argument(
        "--min-len",
        type=int,
        default=1,
        help="Ignore words shorter than M characters (default: 1).",
    )
    parser.add_argument(
        "--case-sensitive",
        action="store_true",
        help="Preserve token case instead of lowercasing words.",
    )
    parser.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help='Emit a JSON array of {"word", "count"} objects.',
    )
    return parser


def _read_text(path: str) -> str:
    if path == _STDIN_PATH:
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    """Run the wordfreq CLI and return the process exit code."""
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        # argparse reports its own errors on stderr and exits; surface the code.
        return int(exc.code) if isinstance(exc.code, int) else 0

    try:
        text = _read_text(args.path)
    except (OSError, UnicodeDecodeError) as exc:
        sys.stderr.write(f"{_PROG}: error: cannot read {args.path}: {exc}\n")
        return 2

    try:
        rows = count_words(
            text,
            min_len=args.min_len,
            ignore_case=not args.case_sensitive,
            top=args.top,
        )
    except ValueError as exc:
        sys.stderr.write(f"{_PROG}: error: {exc}\n")
        return 2

    if args.as_json:
        payload = [{"word": word, "count": count} for word, count in rows]
        sys.stdout.write(json.dumps(payload) + "\n")
    elif rows:
        sys.stdout.write(format_table(rows) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
