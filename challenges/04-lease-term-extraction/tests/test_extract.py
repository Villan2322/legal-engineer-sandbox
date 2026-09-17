import pytest
from pydantic import ValidationError

from lease_extraction.extract import (
    LeaseAbstract,
    LeaseExtractionError,
    extract_lease_terms,
)


def _valid_kwargs(**overrides) -> dict:
    base = dict(
        base_rent_monthly=8500.0,
        lease_term_months=60,
        renewal_option=True,
        renewal_term_months=36,
        permitted_use="general office use",
        assignment_sublease="requires_consent",
        default_notice_days=15,
    )
    base.update(overrides)
    return base


class TestLeaseAbstractValidation:
    def test_valid_lease_with_renewal(self):
        abstract = LeaseAbstract(**_valid_kwargs())
        assert abstract.renewal_term_months == 36

    def test_valid_lease_without_renewal(self):
        abstract = LeaseAbstract(
            **_valid_kwargs(renewal_option=False, renewal_term_months=None)
        )
        assert abstract.renewal_option is False
        assert abstract.renewal_term_months is None

    def test_renewal_term_set_while_no_renewal_option_rejected(self):
        with pytest.raises(ValidationError):
            LeaseAbstract(**_valid_kwargs(renewal_option=False, renewal_term_months=12))

    def test_renewal_option_true_without_term_rejected(self):
        with pytest.raises(ValidationError):
            LeaseAbstract(**_valid_kwargs(renewal_option=True, renewal_term_months=None))

    def test_zero_base_rent_rejected(self):
        with pytest.raises(ValidationError):
            LeaseAbstract(**_valid_kwargs(base_rent_monthly=0))

    def test_negative_base_rent_rejected(self):
        with pytest.raises(ValidationError):
            LeaseAbstract(**_valid_kwargs(base_rent_monthly=-500.0))

    def test_zero_lease_term_months_rejected(self):
        with pytest.raises(ValidationError):
            LeaseAbstract(**_valid_kwargs(lease_term_months=0))

    def test_zero_renewal_term_months_rejected(self):
        with pytest.raises(ValidationError):
            LeaseAbstract(**_valid_kwargs(renewal_term_months=0))

    def test_empty_permitted_use_rejected(self):
        with pytest.raises(ValidationError):
            LeaseAbstract(**_valid_kwargs(permitted_use="   "))

    def test_invalid_assignment_literal_rejected(self):
        with pytest.raises(ValidationError):
            LeaseAbstract(**_valid_kwargs(assignment_sublease="sometimes"))

    def test_zero_default_notice_days_rejected(self):
        with pytest.raises(ValidationError):
            LeaseAbstract(**_valid_kwargs(default_notice_days=0))


class TestExtractLeaseTerms:
    def test_lease_alpha(self, lease_alpha_text):
        abstract = extract_lease_terms(lease_alpha_text)
        assert abstract.base_rent_monthly == pytest.approx(8500.00)
        assert abstract.lease_term_months == 60
        assert abstract.renewal_option is True
        assert abstract.renewal_term_months == 36
        assert abstract.permitted_use == "general office and professional services purposes"
        assert abstract.assignment_sublease == "requires_consent"
        assert abstract.default_notice_days == 15

    def test_lease_beta(self, lease_beta_text):
        abstract = extract_lease_terms(lease_beta_text)
        assert abstract.base_rent_monthly == pytest.approx(12250.00)
        assert abstract.lease_term_months == 84
        assert abstract.renewal_option is False
        assert abstract.renewal_term_months is None
        assert (
            abstract.permitted_use
            == "the retail sale of coffee, tea, and related beverages and light food items"
        )
        assert abstract.assignment_sublease == "not_allowed"
        assert abstract.default_notice_days == 10

    def test_lease_gamma(self, lease_gamma_text):
        abstract = extract_lease_terms(lease_gamma_text)
        assert abstract.base_rent_monthly == pytest.approx(6100.50)
        assert abstract.lease_term_months == 36
        assert abstract.renewal_option is False
        assert abstract.renewal_term_months is None
        assert abstract.permitted_use == "warehousing, distribution, and light assembly of consumer goods"
        assert abstract.assignment_sublease == "allowed"
        assert abstract.default_notice_days == 30

    def test_lease_incomplete_raises_extraction_error(self, lease_incomplete_text):
        with pytest.raises(LeaseExtractionError):
            extract_lease_terms(lease_incomplete_text)
