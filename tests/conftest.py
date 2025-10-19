"""Pytest configuration ensuring the project root is importable."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--trials",
        action="store",
        type=int,
        default=100,
        help="Number of randomized molecules generated in stochastic tests.",
    )
    parser.addoption(
        "--dataset-samples",
        action="store",
        type=int,
        default=200,
        help=(
            "Maximum number of rows to exercise per dataset when running the "
            "round-trip regression tests."
        ),
    )


@pytest.fixture()
def trials(pytestconfig: pytest.Config) -> int:
    return int(pytestconfig.getoption("--trials"))


@pytest.fixture()
def dataset_samples(pytestconfig: pytest.Config) -> int:
    return int(pytestconfig.getoption("--dataset-samples"))
