# AC#1: count_words extracts tokens, lowercases, preserves case, filters by min_len, sorts by (-count, word)
# Subtask: count-words-tokens-sort-filter
# Target: wordfreq/cli.py::count_words
#
# Signature (keyword-only options):
#   count_words(text, *, min_len=1, ignore_case=True, top=None) -> list[tuple[str, int]]

import pytest

from wordfreq.cli import count_words


def test_count_words_extracts_alphanumeric_tokens_splits_on_punctuation():
    result = count_words("hello, world! foo-bar 123")

    assert sorted(result) == sorted(
        [("hello", 1), ("world", 1), ("foo", 1), ("bar", 1), ("123", 1)]
    )


def test_count_words_extracts_alphanumeric_tokens_ignores_underscore():
    result = count_words("snake_case")

    assert sorted(result) == sorted([("snake", 1), ("case", 1)])


def test_count_words_lowercases_by_default_merges_case_variants():
    result = count_words("Hello HELLO hello")

    assert result == [("hello", 3)]


def test_count_words_preserves_case_when_ignore_case_false():
    result = count_words("Hello hello HELLO", ignore_case=False)

    assert sorted(result) == sorted(
        [("Hello", 1), ("hello", 1), ("HELLO", 1)]
    )


def test_count_words_min_len_filters_short_tokens():
    result = count_words("a bb ccc a bb", min_len=2)

    assert result == [("bb", 2), ("ccc", 1)]


def test_count_words_min_len_filters_all_tokens_returns_empty():
    result = count_words("a b c", min_len=2)

    assert result == []


def test_count_words_sorts_by_negative_count_then_word():
    result = count_words("b a c a b")

    assert result == [("a", 2), ("b", 2), ("c", 1)]


def test_count_words_sort_breaks_count_ties_alphabetically():
    result = count_words("zebra apple mango")

    assert result == [("apple", 1), ("mango", 1), ("zebra", 1)]


def test_count_words_top_limits_to_first_n_sorted_results():
    result = count_words("b a c a b", top=2)

    assert result == [("a", 2), ("b", 2)]


@pytest.mark.parametrize(
    "text,kwargs,expected",
    [
        ("the cat the dog", {}, [("the", 2), ("cat", 1), ("dog", 1)]),
        ("The the THE", {"ignore_case": False}, [("THE", 1), ("The", 1), ("the", 1)]),
        ("aa b cc aa", {"min_len": 2, "top": 1}, [("aa", 2)]),
    ],
    ids=["default-sort", "case-preserved-sort", "min-len-then-top"],
)
def test_count_words_combined_options_returns_expected_list(text, kwargs, expected):
    result = count_words(text, **kwargs)

    assert result == expected
