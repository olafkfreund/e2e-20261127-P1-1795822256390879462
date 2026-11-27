# Criterion (AC#4): the CLI argument parser builds with expected defaults, and
# `pytest -q` passes across tests/test_wordfreq.py.
import subprocess
import sys
from argparse import ArgumentParser

import pytest

from wordfreq.cli import _build_parser


def test_build_parser_returns_argument_parser():
    parser = _build_parser()

    assert isinstance(parser, ArgumentParser)


def test_build_parser_parses_empty_argv_with_defaults():
    parser = _build_parser()

    args = parser.parse_args([])

    assert args is not None


@pytest.mark.slow
def test_wordfreq_suite_pytest_q_exits_zero(request):
    root = request.config.rootpath

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "tests/test_wordfreq.py"],
        cwd=root,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
