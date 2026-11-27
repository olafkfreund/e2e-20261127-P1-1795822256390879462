# AC#3: main reads stdin by default or '-', honors options, terminates TSV with
# final newline, nothing for empty output.
import io
import sys

import pytest

from wordfreq.cli import main


def _feed_stdin(monkeypatch, text):
    monkeypatch.setattr(sys, "stdin", io.StringIO(text))


def _rows(output):
    return {tuple(line.split("\t")) for line in output.splitlines() if line}


def test_main_default_reads_stdin_and_emits_counts(monkeypatch, capsys):
    _feed_stdin(monkeypatch, "the the cat\n")

    main([])

    assert ("the", "2") in _rows(capsys.readouterr().out)


def test_main_dash_argument_reads_stdin_and_emits_counts(monkeypatch, capsys):
    _feed_stdin(monkeypatch, "the the cat\n")

    main(["-"])

    assert ("the", "2") in _rows(capsys.readouterr().out)


def test_main_default_folds_case_when_not_case_sensitive(monkeypatch, capsys):
    _feed_stdin(monkeypatch, "The the\n")

    main([])

    assert _rows(capsys.readouterr().out) == {("the", "2")}


def test_main_case_sensitive_keeps_case_variants_distinct(monkeypatch, capsys):
    _feed_stdin(monkeypatch, "The the\n")

    main(["--case-sensitive"])

    assert _rows(capsys.readouterr().out) == {("The", "1"), ("the", "1")}


def test_main_top_option_limits_row_count(monkeypatch, capsys):
    _feed_stdin(monkeypatch, "a a a b b c\n")

    main(["--top", "2"])

    assert len(_rows(capsys.readouterr().out)) == 2


def test_main_min_len_option_excludes_short_words(monkeypatch, capsys):
    _feed_stdin(monkeypatch, "a bb bb ccc\n")

    main(["--min-len", "3"])

    assert _rows(capsys.readouterr().out) == {("ccc", "1")}


def test_main_nonempty_output_terminates_with_newline(monkeypatch, capsys):
    _feed_stdin(monkeypatch, "the cat\n")

    main([])

    assert capsys.readouterr().out.endswith("\n")


@pytest.mark.parametrize(
    "argv,stdin_text",
    [
        pytest.param([], "", id="default-empty-stdin"),
        pytest.param(["-"], "", id="dash-empty-stdin"),
        pytest.param(["--min-len", "5"], "a b\n", id="all-filtered-out"),
    ],
)
def test_main_empty_result_writes_nothing(monkeypatch, capsys, argv, stdin_text):
    _feed_stdin(monkeypatch, stdin_text)

    main(argv)

    assert capsys.readouterr().out == ""
