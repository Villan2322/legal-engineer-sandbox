import json
from pathlib import Path

import pytest

from intake_conflict.conflict_check import Matter

FIXTURES = Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def matters() -> list[Matter]:
    data = json.loads((FIXTURES / "matters.json").read_text())
    return [Matter.from_dict(m) for m in data]
