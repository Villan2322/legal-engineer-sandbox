from nda_redline.redline import (
    check_confidentiality_exclusions,
    check_confidentiality_term,
    check_governing_law,
    check_liability_cap,
    check_non_solicit_cap,
    redline_contract,
)


class TestCheckConfidentialityTerm:
    def test_flags_term_over_three_years(self, load_contract):
        text = load_contract("long_confidentiality_term.txt")
        flag = check_confidentiality_term(text)
        assert flag is not None
        assert flag.rule_id == "confidentiality_term"
        assert "5 years" in flag.clause_excerpt

    def test_compliant_term_is_not_flagged(self, load_contract):
        text = load_contract("compliant_nda.txt")
        assert check_confidentiality_term(text) is None


class TestCheckGoverningLaw:
    def test_flags_unapproved_state(self, load_contract):
        text = load_contract("unapproved_governing_law.txt")
        flag = check_governing_law(text)
        assert flag is not None
        assert flag.rule_id == "governing_law"
        assert "California" in flag.note

    def test_approved_state_is_not_flagged(self, load_contract):
        text = load_contract("compliant_nda.txt")
        assert check_governing_law(text) is None


class TestCheckNonSolicitCap:
    def test_flags_period_over_twelve_months(self, load_contract):
        text = load_contract("uncapped_nonsolicit.txt")
        flag = check_non_solicit_cap(text)
        assert flag is not None
        assert flag.rule_id == "non_solicit_cap"
        assert "24" in flag.clause_excerpt

    def test_compliant_period_is_not_flagged(self, load_contract):
        text = load_contract("compliant_nda.txt")
        assert check_non_solicit_cap(text) is None


class TestCheckConfidentialityExclusions:
    def test_flags_missing_exclusions(self, load_contract):
        text = load_contract("missing_exclusions_and_unlimited_liability.txt")
        flag = check_confidentiality_exclusions(text)
        assert flag is not None
        assert flag.rule_id == "confidentiality_exclusions"

    def test_present_exclusions_are_not_flagged(self, load_contract):
        text = load_contract("compliant_nda.txt")
        assert check_confidentiality_exclusions(text) is None


class TestCheckLiabilityCap:
    def test_flags_unlimited_liability(self, load_contract):
        text = load_contract("missing_exclusions_and_unlimited_liability.txt")
        flag = check_liability_cap(text)
        assert flag is not None
        assert flag.rule_id == "liability_cap"

    def test_capped_liability_is_not_flagged(self, load_contract):
        text = load_contract("compliant_nda.txt")
        assert check_liability_cap(text) is None


class TestRedlineContract:
    def test_compliant_contract_has_no_flags(self, load_contract, playbook):
        result = redline_contract(load_contract("compliant_nda.txt"), playbook)
        assert result.compliant is True
        assert result.flags == []

    def test_long_confidentiality_term_flags_only_that_rule(self, load_contract, playbook):
        result = redline_contract(load_contract("long_confidentiality_term.txt"), playbook)
        assert result.compliant is False
        assert len(result.flags) == 1
        assert result.flags[0].rule_id == "confidentiality_term"

    def test_unapproved_governing_law_flags_only_that_rule(self, load_contract, playbook):
        result = redline_contract(load_contract("unapproved_governing_law.txt"), playbook)
        assert result.compliant is False
        assert len(result.flags) == 1
        assert result.flags[0].rule_id == "governing_law"

    def test_uncapped_nonsolicit_flags_only_that_rule(self, load_contract, playbook):
        result = redline_contract(load_contract("uncapped_nonsolicit.txt"), playbook)
        assert result.compliant is False
        assert len(result.flags) == 1
        assert result.flags[0].rule_id == "non_solicit_cap"

    def test_dual_violation_flags_both_rules(self, load_contract, playbook):
        result = redline_contract(
            load_contract("missing_exclusions_and_unlimited_liability.txt"), playbook
        )
        assert result.compliant is False
        assert len(result.flags) == 2
        rule_ids = {flag.rule_id for flag in result.flags}
        assert rule_ids == {"confidentiality_exclusions", "liability_cap"}
