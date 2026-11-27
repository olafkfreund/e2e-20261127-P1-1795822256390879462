# AC#3: --json output terminated with a final newline.
# Criterion (from subtask main-json-output): main --json emits a JSON array of
# {word, count} objects ending with a newline, including '[]' for empty input.

import json

import pytest

from wordfreq.cli import main


def _run_json(tmp_path, capsys, text):
    input_file = tmp_path / "input.txt"
    input_file.write_text(text, encoding="utf-8")
    main(["--json", str(input_file)])
    return capsys.readouterr().out


def test_main_json_output_ends_with_newline_for_nonempty_input(tmp_path, capsys):
    out = _run_json(tmp_path, capsys, "apple apple banana")
    assert out.endswith("\n")


def test_main_json_output_is_array_of_word_count_objects(tmp_path, capsys):
    out = _run_json(tmp_path, capsys, "apple apple banana")
    data = json.loads(out)
    assert isinstance(data, list)
    assert all(set(item.keys()) == {"word", "count"} for item in data)


def test_main_json_output_contains_expected_word_counts(tmp_path, capsys):
    out = _run_json(tmp_path, capsys, "apple apple banana")
    pairs = sorted((item["word"], item["count"]) for item in json.loads(out))
    assert pairs == [("apple", 2), ("banana", 1)]


def test_main_json_output_empty_input_is_empty_array(tmp_path, capsys):
    out = _run_json(tmp_path, capsys, "")
    assert out == "[]\n"


def test_main_json_output_empty_input_ends_with_newline(tmp_path, capsys):
    out = _run_json(tmp_path, capsys, "")
    assert out.endswith("\n")
