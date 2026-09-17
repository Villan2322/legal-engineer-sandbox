import json
from pathlib import Path

import pytest

from nda_redline.redline import PlaybookRule

FIXTURES = Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def playbook() -> list[PlaybookRule]:
    data = json.loads((FIXTURES / "playbook.json").read_text())
    return [PlaybookRule(**rule) for rule in data]


@pytest.fixture
def load_contract():
    def _load(name: str) -> str:
        return (FIXTURES / "contracts" / name).read_text()

    return _load
