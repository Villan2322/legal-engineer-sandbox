import json
from pathlib import Path

import pytest

from ledes_reconciliation.reconcile import CodeRule, MatterRef, RawActivityEntry

FIXTURES = Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def matters() -> list[MatterRef]:
    data = json.loads((FIXTURES / "matters.json").read_text())
    return [MatterRef.from_dict(m) for m in data]


@pytest.fixture
def code_rules() -> list[CodeRule]:
    data = json.loads((FIXTURES / "code_rules.json").read_text())
    return [CodeRule.from_dict(r) for r in data]


@pytest.fixture
def raw_activity() -> list[RawActivityEntry]:
    data = json.loads((FIXTURES / "raw_activity.json").read_text())
    return [RawActivityEntry.from_dict(e) for e in data]
