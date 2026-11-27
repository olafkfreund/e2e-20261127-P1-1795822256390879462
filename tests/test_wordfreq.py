"""Visible smoke tests for the wordfreq package."""

from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

from wordfreq.cli import count_words, format_table, main

REPO_ROOT = Path(__file__).resolve().parent.parent


def _write_sample(tmp_path: Path, text: str) -> Path:
    sample = tmp_path / "sample.txt"
    sample.write_text(text, encoding="utf-8")
    return sample


def _run_module(
    args: list[str], *, stdin_text: str | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "wordfreq", *args],
        cwd=REPO_ROOT,
        input=stdin_text,
        capture_output=True,
        text=True,
        check=False,
    )


def test_count_words_basic_ranking() -> None:
    text = "Apple banana apple, cherry! Banana apple."
    assert count_words(text) == [("apple", 3), ("banana", 2), ("cherry", 1)]


def test_format_table_tsv() -> None:
    assert format_table([("apple", 3), ("banana", 2)]) == "apple\t3\nbanana\t2"


def test_cli_top_and_min_len(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("to be or not to be that is the question", encoding="utf-8")
    rc = main([str(sample), "--min-len", "3", "--top", "2"])
    assert rc == 0
    out = capsys.readouterr().out
    assert out.strip().splitlines() == ["not\t1", "question\t1"]


# Unit tests for count_words


def test_count_words_breaks_ties_alphabetically() -> None:
    text = "zebra mango apple mango zebra apple"
    assert count_words(text) == [("apple", 2), ("mango", 2), ("zebra", 2)]


def test_count_words_orders_by_count_before_word() -> None:
    assert count_words("b b a") == [("b", 2), ("a", 1)]


def test_count_words_tie_order_ignores_input_order() -> None:
    assert count_words("alpha beta gamma") == count_words("gamma beta alpha")
    assert count_words("gamma beta alpha") == [
        ("alpha", 1),
        ("beta", 1),
        ("gamma", 1),
    ]


def test_count_words_lowercases_by_default() -> None:
    assert count_words("Apple APPLE apple") == [("apple", 3)]


def test_count_words_preserves_case_when_ignore_case_is_false() -> None:
    assert count_words("Apple apple APPLE", ignore_case=False) == [
        ("APPLE", 1),
        ("Apple", 1),
        ("apple", 1),
    ]


def test_count_words_tokens_are_ascii_alphanumeric_runs() -> None:
    text = "snake_case, don't x42 café"
    assert count_words(text) == [
        ("caf", 1),
        ("case", 1),
        ("don", 1),
        ("snake", 1),
        ("t", 1),
        ("x42", 1),
    ]


def test_count_words_filters_by_min_len() -> None:
    assert count_words("a an the cat a", min_len=2) == [
        ("an", 1),
        ("cat", 1),
        ("the", 1),
    ]


def test_count_words_top_limits_results() -> None:
    assert count_words("c c b b a", top=1) == [("b", 2)]
    assert count_words("a b", top=0) == []


def test_count_words_empty_input_returns_empty_list() -> None:
    assert count_words("") == []
    assert count_words("  !!! ...  ") == []


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"min_len": 0}, "min_len must be >= 1"),
        ({"min_len": -1}, "min_len must be >= 1"),
        ({"top": -1}, "top must be >= 0"),
    ],
)
def test_count_words_rejects_invalid_arguments(
    kwargs: dict[str, int], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        count_words("a b", **kwargs)


# Unit tests for format_table


def test_format_table_empty_returns_empty_string() -> None:
    assert format_table([]) == ""


def test_format_table_has_no_trailing_newline() -> None:
    assert format_table([("a", 1)]) == "a\t1"


# CLI tests for main


def test_cli_tie_breaking_is_alphabetical(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = _write_sample(tmp_path, "pear fig apple fig pear apple kiwi")
    assert main([str(sample)]) == 0
    assert capsys.readouterr().out == "apple\t2\nfig\t2\npear\t2\nkiwi\t1\n"


def test_cli_case_sensitive_keeps_case_variants_separate(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = _write_sample(tmp_path, "Apple apple APPLE apple")

    assert main([str(sample)]) == 0
    assert capsys.readouterr().out == "apple\t4\n"

    assert main(["--case-sensitive", str(sample)]) == 0
    assert capsys.readouterr().out == "apple\t2\nAPPLE\t1\nApple\t1\n"


def test_cli_reads_stdin_by_default(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("the cat the\n"))
    assert main([]) == 0
    assert capsys.readouterr().out == "the\t2\ncat\t1\n"


def test_cli_reads_stdin_when_path_is_dash(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("dog dog\n"))
    assert main(["-"]) == 0
    assert capsys.readouterr().out == "dog\t2\n"


@pytest.mark.parametrize(
    ("argv_extra", "expected_message"),
    [
        (["--min-len", "0"], "min_len must be >= 1"),
        (["--min-len", "-2"], "min_len must be >= 1"),
        (["--top", "-1"], "top must be >= 0"),
        (["--top", "many"], "invalid int value"),
        (["--no-such-flag"], "unrecognized arguments"),
    ],
)
def test_cli_invalid_arguments_exit_2_with_stderr(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    argv_extra: list[str],
    expected_message: str,
) -> None:
    sample = _write_sample(tmp_path, "a b c")
    assert main([*argv_extra, str(sample)]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert expected_message in captured.err


def test_cli_top_zero_succeeds_with_no_rows(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = _write_sample(tmp_path, "a b c")
    assert main(["--top", "0", str(sample)]) == 0
    assert capsys.readouterr().out == ""


def test_cli_top_zero_json_emits_empty_array(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = _write_sample(tmp_path, "a b c")
    assert main(["--top", "0", "--json", str(sample)]) == 0
    assert capsys.readouterr().out == "[]\n"


def test_cli_tsv_output_ends_with_single_newline(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = _write_sample(tmp_path, "apple banana apple")
    assert main([str(sample)]) == 0
    out = capsys.readouterr().out
    assert out == "apple\t2\nbanana\t1\n"
    assert not out.endswith("\n\n")


def test_cli_empty_tsv_output_writes_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = _write_sample(tmp_path, "!!! ... ")
    assert main([str(sample)]) == 0
    assert capsys.readouterr().out == ""


def test_cli_json_output_ends_with_single_newline(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = _write_sample(tmp_path, "apple banana apple")
    assert main(["--json", str(sample)]) == 0
    out = capsys.readouterr().out
    assert json.loads(out) == [
        {"word": "apple", "count": 2},
        {"word": "banana", "count": 1},
    ]
    assert out.endswith("\n")
    assert not out.endswith("\n\n")


def test_cli_empty_json_output_is_empty_array(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = _write_sample(tmp_path, "!!! ... ")
    assert main(["--json", str(sample)]) == 0
    assert capsys.readouterr().out == "[]\n"


def test_cli_missing_file_exits_2_with_stderr(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    missing = tmp_path / "does-not-exist.txt"
    assert main([str(missing)]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "cannot read" in captured.err


# Subprocess tests for `python -m wordfreq`


def test_python_m_wordfreq_counts_stdin() -> None:
    result = _run_module([], stdin_text="the cat the\n")
    assert result.returncode == 0
    assert result.stdout == "the\t2\ncat\t1\n"
    assert result.stderr == ""


def test_python_m_wordfreq_reads_file_and_emits_json(tmp_path: Path) -> None:
    sample = _write_sample(tmp_path, "apple banana apple")
    result = _run_module(["--json", str(sample)])
    assert result.returncode == 0
    assert json.loads(result.stdout) == [
        {"word": "apple", "count": 2},
        {"word": "banana", "count": 1},
    ]
    assert result.stdout.endswith("\n")
    assert not result.stdout.endswith("\n\n")
    assert result.stderr == ""


def test_python_m_wordfreq_missing_file_exits_2(tmp_path: Path) -> None:
    result = _run_module([str(tmp_path / "missing.txt")])
    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr != ""
