"""Smoke tests for the fake data generator itself — not a challenge, just
making sure the tool the challenges rely on for extra practice data actually
works and stays reproducible under a fixed seed.
"""

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.fake_data.activity import generate_activity_entries
from tools.fake_data.common import FakeDataContext
from tools.fake_data.lease import generate_lease
from tools.fake_data.matters import generate_matters, generate_webhooks
from tools.fake_data.nda import generate_nda
from tools.fake_data.privilege import generate_privileged_doc


class TestGeneratorsAreReproducible:
    def test_same_seed_produces_identical_matters(self):
        a = generate_matters(10, FakeDataContext(seed=42))
        b = generate_matters(10, FakeDataContext(seed=42))
        assert a == b

    def test_different_seed_produces_different_matters(self):
        a = generate_matters(10, FakeDataContext(seed=1))
        b = generate_matters(10, FakeDataContext(seed=2))
        assert a != b


class TestMattersAndWebhooks:
    def test_matters_shape(self):
        matters = generate_matters(5, FakeDataContext(seed=1))
        assert len(matters) == 5
        for m in matters:
            assert m["matter_id"].startswith("M-")
            assert m["status"] in ("open", "closed")
            assert m["client_name"]

    def test_webhooks_reference_valid_shape(self):
        ctx = FakeDataContext(seed=1)
        matters = generate_matters(10, ctx)
        webhooks = generate_webhooks(20, matters, ctx)
        assert len(webhooks) == 20
        for w in webhooks:
            assert w["intake_id"].startswith("W-")
            assert w["prospective_client"]


class TestActivity:
    def test_activity_shape_and_duration_values(self):
        ctx = FakeDataContext(seed=1)
        matters = generate_matters(5, ctx)
        code_rules = [
            {"category": "call", "task_code": "L100", "activity_code": "A101", "keywords": ["call"]},
            {"category": "other", "task_code": "L190", "activity_code": "A999", "keywords": []},
        ]
        entries = generate_activity_entries(15, matters, code_rules, ctx)
        assert len(entries) == 15
        for e in entries:
            assert e["entry_id"].startswith("A-")
            assert e["duration_minutes"] > 0


class TestNda:
    def test_violations_match_generated_terms(self):
        ctx = FakeDataContext(seed=1)
        for _ in range(20):
            result = generate_nda(ctx)
            assert "NON-DISCLOSURE AGREEMENT" in result["text"]
            assert isinstance(result["expected_violations"], list)
            valid_ids = {
                "confidentiality_term",
                "governing_law",
                "non_solicit_cap",
                "confidentiality_exclusions",
                "liability_cap",
            }
            assert set(result["expected_violations"]) <= valid_ids


class TestLease:
    def test_expected_fields_present(self):
        ctx = FakeDataContext(seed=1)
        result = generate_lease(ctx)
        expected = result["expected"]
        assert expected["base_rent_monthly"] > 0
        assert expected["lease_term_months"] > 0
        assert expected["assignment_sublease"] in ("allowed", "not_allowed", "requires_consent")
        if not expected["renewal_option"]:
            assert expected["renewal_term_months"] is None


class TestPrivilege:
    def test_known_entities_appear_in_text(self):
        ctx = FakeDataContext(seed=1)
        result = generate_privileged_doc(ctx)
        for entity in result["known_entities"]:
            assert entity in result["text"]
        assert result["pii"]["emails"][0] in result["text"]


class TestCli:
    def test_all_command_writes_expected_files(self, tmp_path):
        out_dir = tmp_path / "fake_dataset"
        subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "tools" / "generate_fake_data.py"),
                "all",
                "--seed",
                "1",
                "--count",
                "3",
                "--out-dir",
                str(out_dir),
            ],
            check=True,
            cwd=REPO_ROOT,
        )
        assert (out_dir / "matters.json").exists()
        assert (out_dir / "webhooks.json").exists()
        assert (out_dir / "ndas" / "manifest.json").exists()
        assert (out_dir / "leases" / "manifest.json").exists()
        assert (out_dir / "privilege" / "manifest.json").exists()
        matters = json.loads((out_dir / "matters.json").read_text())
        assert len(matters) == 3
