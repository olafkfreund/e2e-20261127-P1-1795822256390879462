# AC#1: count_words raises ValueError('min_len must be >= 1') when min_len < 1,
# raises ValueError('top must be >= 0') when top < 0, and top=0 returns an empty list.

import pytest

from wordfreq.cli import count_words

SAMPLE_TEXT = "the quick brown fox jumps over the lazy dog the end"


@pytest.mark.parametrize("min_len", [0, -1], ids=["min_len_zero", "min_len_negative"])
def test_count_words_min_len_below_one_raises_value_error(min_len):
    with pytest.raises(ValueError, match=r"^min_len must be >= 1$"):
        count_words(SAMPLE_TEXT, min_len=min_len, top=10)


@pytest.mark.parametrize("top", [-1, -10], ids=["top_negative_one", "top_negative_ten"])
def test_count_words_top_negative_raises_value_error(top):
    with pytest.raises(ValueError, match=r"^top must be >= 0$"):
        count_words(SAMPLE_TEXT, min_len=1, top=top)


def test_count_words_top_zero_returns_empty_list():
    result = count_words(SAMPLE_TEXT, min_len=1, top=0)
    assert result == []
