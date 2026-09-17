import pytest

from intake_conflict.conflict_check import (
    IntakeWebhook,
    find_conflicts,
    fuzzy_match_score,
    normalize_entity_name,
)


class TestNormalizeEntityName:
    def test_strips_corporate_suffix_and_punctuation(self):
        assert normalize_entity_name("Blue Harbor Logistics, Inc.") == normalize_entity_name(
            "Blue Harbor Logistics Corp"
        )

    def test_case_insensitive(self):
        assert normalize_entity_name("Meridian Health Partners LLC") == normalize_entity_name(
            "MERIDIAN HEALTH PARTNERS llc"
        )

    def test_distinct_names_stay_distinct(self):
        assert normalize_entity_name("Alliance Medical Group") != normalize_entity_name(
            "Redstone Energy Partners"
        )


class TestFuzzyMatchScore:
    def test_identical_normalized_names_score_100(self):
        assert fuzzy_match_score("Blue Harbor Logistics Corp", "blue harbor logistics, inc.") == pytest.approx(
            100.0, abs=0.01
        )

    def test_unrelated_names_score_low(self):
        assert fuzzy_match_score("Blue Harbor Logistics Corp", "Grayson Mineral Rights Trust") < 50.0


class TestFindConflicts:
    def test_clean_intake_has_no_conflict(self, matters):
        webhook = IntakeWebhook(
            intake_id="W-1",
            prospective_client="Sunrise Bakery LLC",
            counterparties=["Golden Wheat Distributors"],
        )
        report = find_conflicts(webhook, matters)
        assert report.has_conflict is False
        assert report.conflicts == []

    def test_prospective_client_matches_adverse_party_exact(self, matters):
        webhook = IntakeWebhook(intake_id="W-2", prospective_client="Alliance Medical Group")
        report = find_conflicts(webhook, matters)
        assert report.has_conflict is True
        assert len(report.conflicts) == 1
        hit = report.conflicts[0]
        assert hit.matter_id == "M-1001"
        assert hit.match_type == "prospective_client_is_adverse_party"

    def test_counterparty_matches_client_with_suffix_variant(self, matters):
        webhook = IntakeWebhook(
            intake_id="W-3",
            prospective_client="Newco Ventures",
            counterparties=["Blue Harbor Logistics, Inc."],
        )
        report = find_conflicts(webhook, matters)
        assert report.has_conflict is True
        hit = report.conflicts[0]
        assert hit.matter_id == "M-1002"
        assert hit.match_type == "counterparty_is_client"

    def test_counterparty_matches_subsidiary(self, matters):
        webhook = IntakeWebhook(
            intake_id="W-4",
            prospective_client="Newco Ventures",
            counterparties=["Meridian Surgical Centers, Inc"],
        )
        report = find_conflicts(webhook, matters)
        assert report.has_conflict is True
        hit = report.conflicts[0]
        assert hit.matter_id == "M-1001"
        assert hit.matched_against == "Meridian Surgical Centers Inc."

    def test_counterparty_matches_alias_case_insensitive(self, matters):
        webhook = IntakeWebhook(
            intake_id="W-5",
            prospective_client="Newco Ventures",
            counterparties=["mhp"],
        )
        report = find_conflicts(webhook, matters)
        assert report.has_conflict is True
        assert report.conflicts[0].matter_id == "M-1001"

    def test_near_miss_below_threshold_is_not_a_conflict(self, matters):
        # Shares two of three words with the M-1001 adverse party, but names
        # a materially different entity. Should not cross the threshold.
        webhook = IntakeWebhook(intake_id="W-6", prospective_client="Alliance Home Health Group")
        report = find_conflicts(webhook, matters)
        assert report.has_conflict is False

    def test_closed_matters_are_still_checked(self, matters):
        webhook = IntakeWebhook(intake_id="W-7", prospective_client="Pinnacle Property Management")
        report = find_conflicts(webhook, matters)
        assert report.has_conflict is True
        hit = report.conflicts[0]
        assert hit.matter_id == "M-1003"
        assert hit.matter_status == "closed"

    def test_multiple_conflicts_across_matters(self, matters):
        webhook = IntakeWebhook(
            intake_id="W-8",
            prospective_client="Newco Ventures",
            counterparties=["Blue Harbor Logistics Corp", "MHP"],
        )
        report = find_conflicts(webhook, matters)
        matched_matters = {hit.matter_id for hit in report.conflicts}
        assert matched_matters == {"M-1001", "M-1002"}

    def test_related_entity_triggers_adverse_party_conflict(self, matters):
        webhook = IntakeWebhook(
            intake_id="W-9",
            prospective_client="Newco Ventures",
            related_entities=["Grayson Mineral Rights Trust"],
        )
        report = find_conflicts(webhook, matters)
        assert report.has_conflict is True
        hit = report.conflicts[0]
        assert hit.matter_id == "M-1004"
        assert hit.match_type == "prospective_client_is_adverse_party"

    def test_no_duplicate_hits_for_same_matter_and_direction(self, matters):
        # Two counterparty names both plausibly match the same matter's
        # client family — only the single best hit should be reported.
        webhook = IntakeWebhook(
            intake_id="W-10",
            prospective_client="Newco Ventures",
            counterparties=["Blue Harbor Logistics Corp", "Blue Harbor Logistics"],
        )
        report = find_conflicts(webhook, matters)
        hits_for_m1002 = [h for h in report.conflicts if h.matter_id == "M-1002"]
        assert len(hits_for_m1002) == 1
