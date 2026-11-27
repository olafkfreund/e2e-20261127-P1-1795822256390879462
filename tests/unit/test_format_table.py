# AC#2: format_table formats rows as word\tcount lines separated by \n, '' for empty
#
# Criterion: format_table formats rows as word<TAB>count lines separated by "\n",
# with no trailing newline, and returns "" for empty input.

import pytest

from wordfreq.cli import format_table


@pytest.fixture
def sample_rows():
    return [("the", 3), ("cat", 1), ("sat", 2)]


def test_format_table_rows_are_word_tab_count_lines(sample_rows):
    lines = format_table(sample_rows).split("\n")
    assert lines == ["the\t3", "cat\t1", "sat\t2"]


def test_format_table_rows_joined_with_newline_without_trailing_newline(sample_rows):
    assert format_table(sample_rows) == "the\t3\ncat\t1\nsat\t2"


def test_format_table_single_row_has_no_newline():
    assert format_table([("hello", 7)]) == "hello\t7"


def test_format_table_empty_input_returns_empty_string():
    assert format_table([]) == ""
