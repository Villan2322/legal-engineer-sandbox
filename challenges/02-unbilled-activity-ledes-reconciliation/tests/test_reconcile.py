import pytest

from ledes_reconciliation.reconcile import (
    RawActivityEntry,
    classify_activity,
    extract_matter_reference,
    reconcile_activity,
    resolve_matter,
    to_units,
)


class TestExtractMatterReference:
    def test_finds_reference_present(self):
        assert extract_matter_reference("Notes regarding M-2031 filing.") == "M-2031"

    def test_returns_none_when_absent(self):
        assert extract_matter_reference("Notes regarding the filing.") is None

    def test_case_insensitive_on_m(self):
        assert extract_matter_reference("see m-2044 for details") == "M-2044"

    def test_returns_leftmost_reference_when_multiple_present(self):
        assert extract_matter_reference("Compare M-2031 against M-2044.") == "M-2031"

    def test_does_not_match_wrong_digit_count(self):
        assert extract_matter_reference("Reference M-203 is incomplete.") is None


class TestToUnits:
    @pytest.mark.parametrize(
        "duration_minutes, expected_units",
        [
            (1, 0.1),
            (6, 0.1),
            (7, 0.2),
            (30, 0.5),
            (33, 0.6),
            (60, 1.0),
        ],
    )
    def test_rounds_up_to_nearest_six_minute_increment(self, duration_minutes, expected_units):
        assert to_units(duration_minutes) == pytest.approx(expected_units, abs=1e-9)

    def test_zero_duration_is_not_billed(self):
        assert to_units(0) == 0.0


class TestClassifyActivity:
    def test_matches_first_rule_by_keyword(self, code_rules):
        rule = classify_activity("Legal research on case law for the motion.", code_rules)
        assert rule.category == "legal_research"
        assert rule.task_code == "L120"

    def test_respects_list_order_when_multiple_categories_match(self, code_rules):
        # Contains both a document_review keyword ("discovery documents")
        # and a drafting keyword ("drafting"). document_review is earlier
        # in code_rules, so it must win regardless of where each keyword
        # appears in the text.
        text = "Drafting a memo after reviewing the discovery documents for the matter."
        rule = classify_activity(text, code_rules)
        assert rule.category == "document_review"
        assert rule.task_code == "L110"

    def test_falls_back_to_catch_all_rule_when_nothing_matches(self, code_rules):
        rule = classify_activity("Updated the case management system.", code_rules)
        assert rule.category == "other"
        assert rule.task_code == "L190"
        assert rule.activity_code == "A999"


class TestResolveMatter:
    def test_resolves_via_explicit_matter_code(self, matters):
        entry = RawActivityEntry(
            entry_id="X-1",
            timekeeper="T. Test",
            date="2026-01-01",
            duration_minutes=10,
            description="Email regarding M-2068 lease terms.",
        )
        matter = resolve_matter(entry, matters)
        assert matter is not None
        assert matter.matter_id == "M-2068"

    def test_resolves_via_fuzzy_client_name_match(self, matters):
        entry = RawActivityEntry(
            entry_id="X-2",
            timekeeper="T. Test",
            date="2026-01-01",
            duration_minutes=10,
            description="Call with client to discuss Kestrel Home Goods renewal.",
        )
        matter = resolve_matter(entry, matters)
        assert matter is not None
        assert matter.matter_id == "M-2057"

    def test_falls_back_to_fuzzy_when_explicit_code_is_unknown(self, matters):
        entry = RawActivityEntry(
            entry_id="X-3",
            timekeeper="T. Test",
            date="2026-01-01",
            duration_minutes=10,
            description="Notes on M-9999 follow-up for Alderbrook Manufacturing.",
        )
        matter = resolve_matter(entry, matters)
        assert matter is not None
        assert matter.matter_id == "M-2031"

    def test_returns_none_when_nothing_resolves(self, matters):
        entry = RawActivityEntry(
            entry_id="X-4",
            timekeeper="T. Test",
            date="2026-01-01",
            duration_minutes=10,
            description="Quick call about scheduling next steps.",
        )
        assert resolve_matter(entry, matters) is None


class TestReconcileActivity:
    def test_every_entry_lands_in_exactly_one_bucket(self, raw_activity, matters, code_rules):
        result = reconcile_activity(raw_activity, matters, code_rules)
        billed_ids = {line.entry_id for line in result.billed}
        review_ids = {entry.entry_id for entry in result.needs_review}
        assert billed_ids.isdisjoint(review_ids)
        assert billed_ids | review_ids == {e.entry_id for e in raw_activity}

    def test_unresolvable_entry_goes_to_needs_review_only(self, raw_activity, matters, code_rules):
        result = reconcile_activity(raw_activity, matters, code_rules)
        review_ids = {entry.entry_id for entry in result.needs_review}
        billed_ids = {line.entry_id for line in result.billed}
        assert review_ids == {"E-007"}
        assert "E-007" not in billed_ids

    def test_billed_lines_have_correct_matter_task_and_units(self, raw_activity, matters, code_rules):
        result = reconcile_activity(raw_activity, matters, code_rules)
        by_id = {line.entry_id: line for line in result.billed}

        # Explicit matter reference, client-communication keyword, 30 min -> 0.5 units.
        line = by_id["E-001"]
        assert line.matter_id == "M-2031"
        assert line.task_code == "L100"
        assert line.activity_code == "A104"
        assert line.units == pytest.approx(0.5)
        assert line.narrative == "Email to client regarding M-2031 discovery schedule updates."

        # Fuzzy client-name resolution, keyword-order priority (document_review
        # over drafting), 7 min -> 0.2 units.
        line = by_id["E-004"]
        assert line.matter_id == "M-2057"
        assert line.task_code == "L110"
        assert line.units == pytest.approx(0.2)

        # Explicit matter reference, no keyword match -> fallback rule.
        line = by_id["E-009"]
        assert line.matter_id == "M-2057"
        assert line.task_code == "L190"
        assert line.activity_code == "A999"
        assert line.units == pytest.approx(0.1)
