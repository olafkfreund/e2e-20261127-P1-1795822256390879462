# Criterion (AC#3): main returns 0 on success or 2 with non-empty stderr on
# invalid arguments or missing files; --top 0 succeeds.
#
# Subtask main-exit-codes-and-errors:
#   - negative --top               -> return 2, non-empty stderr
#   - --min-len 0                  -> return 2, non-empty stderr
#   - missing input file           -> return 2, non-empty stderr
#   - --top 0 with no rows         -> return 0

import pytest

from wordfreq.cli import main


@pytest.fixture
def empty_input(tmp_path):
    path = tmp_path / "empty.txt"
    path.write_text("", encoding="utf-8")
    return path


@pytest.fixture
def missing_input(tmp_path):
    return tmp_path / "does_not_exist.txt"


@pytest.mark.parametrize(
    "argv_builder",
    [
        pytest.param(lambda p: ["--top=-1", str(p)], id="negative-top"),
        pytest.param(lambda p: ["--min-len", "0", str(p)], id="min-len-zero"),
    ],
)
def test_main_invalid_argument_returns_2(argv_builder, empty_input):
    assert main(argv_builder(empty_input)) == 2


@pytest.mark.parametrize(
    "argv_builder",
    [
        pytest.param(lambda p: ["--top=-1", str(p)], id="negative-top"),
        pytest.param(lambda p: ["--min-len", "0", str(p)], id="min-len-zero"),
    ],
)
def test_main_invalid_argument_writes_stderr(argv_builder, empty_input, capsys):
    main(argv_builder(empty_input))
    captured = capsys.readouterr()
    assert captured.err.strip() != ""


def test_main_missing_file_returns_2(missing_input):
    assert main([str(missing_input)]) == 2


def test_main_missing_file_writes_stderr(missing_input, capsys):
    main([str(missing_input)])
    captured = capsys.readouterr()
    assert captured.err.strip() != ""


def test_main_top_zero_empty_input_returns_0(empty_input):
    assert main(["--top", "0", str(empty_input)]) == 0
