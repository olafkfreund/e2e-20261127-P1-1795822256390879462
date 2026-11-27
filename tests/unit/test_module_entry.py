# AC#3: main and python -m wordfreq read from path or stdin
#
# Subtask: main-file-path-and-module-entry
# Verify main reads a positional file path and that `python -m wordfreq`
# runs end-to-end via subprocess with stdin.

import os
import subprocess
import sys
from pathlib import Path

import pytest

import wordfreq
from wordfreq.cli import _read_text

_PROJECT_ROOT = str(Path(wordfreq.__file__).resolve().parent.parent)


def _run_module(args, stdin_text=None, cwd=None):
    """Run `python -m wordfreq` in a real subprocess and return the result."""
    env = dict(os.environ)
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = _PROJECT_ROOT + (os.pathsep + existing if existing else "")
    return subprocess.run(
        [sys.executable, "-m", "wordfreq", *args],
        input=stdin_text,
        capture_output=True,
        text=True,
        cwd=cwd,
        env=env,
        timeout=30,
    )


@pytest.fixture
def sample_file(tmp_path):
    path = tmp_path / "sample.txt"
    path.write_text("the quick brown fox jumps over the lazy dog the end\n", encoding="utf-8")
    return path


def test_read_text_positional_path_returns_file_contents(sample_file):
    assert _read_text(str(sample_file)) == sample_file.read_text(encoding="utf-8")


def test_module_entry_positional_path_exits_zero(sample_file, tmp_path):
    result = _run_module([str(sample_file)], cwd=tmp_path)
    assert result.returncode == 0


def test_module_entry_positional_path_produces_output(sample_file, tmp_path):
    result = _run_module([str(sample_file)], cwd=tmp_path)
    assert result.stdout.strip() != ""


def test_module_entry_positional_path_output_contains_input_word(sample_file, tmp_path):
    result = _run_module([str(sample_file)], cwd=tmp_path)
    assert "fox" in result.stdout


def test_module_entry_stdin_input_exits_zero(tmp_path):
    result = _run_module([], stdin_text="the quick brown fox\n", cwd=tmp_path)
    assert result.returncode == 0


def test_module_entry_stdin_input_produces_output(tmp_path):
    result = _run_module([], stdin_text="the quick brown fox\n", cwd=tmp_path)
    assert result.stdout.strip() != ""


def test_module_entry_stdin_input_output_contains_input_word(tmp_path):
    result = _run_module([], stdin_text="the quick brown fox\n", cwd=tmp_path)
    assert "fox" in result.stdout
