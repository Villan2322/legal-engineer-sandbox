from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent.parent / "fixtures" / "leases"


def _load(name: str) -> str:
    return (FIXTURES / name).read_text()


@pytest.fixture
def lease_alpha_text() -> str:
    return _load("lease_alpha.txt")


@pytest.fixture
def lease_beta_text() -> str:
    return _load("lease_beta.txt")


@pytest.fixture
def lease_gamma_text() -> str:
    return _load("lease_gamma.txt")


@pytest.fixture
def lease_incomplete_text() -> str:
    return _load("lease_incomplete.txt")
