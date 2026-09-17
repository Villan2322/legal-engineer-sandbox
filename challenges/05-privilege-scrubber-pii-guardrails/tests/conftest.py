import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def known_entities() -> list[str]:
    return json.loads((FIXTURES / "known_entities.json").read_text())
