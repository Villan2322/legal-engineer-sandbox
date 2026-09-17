"""
Challenge 04 — Commercial Lease Term Extraction

A lease abstract today gets built by a paralegal reading a 40-page lease
and manually filling in a spreadsheet: base rent, term, renewal rights,
permitted use, assignment restrictions, default notice periods. It's the
first thing a real estate associate hands off on any acquisition or
financing where the target holds commercial leases — and it's exactly the
kind of extraction-into-a-validated-schema task a machine should draft
and a human should verify.

`LeaseAbstract` is the validated schema. `extract_lease_terms` parses raw
lease text with regex/keyword heuristics and returns a validated
`LeaseAbstract`, or raises `LeaseExtractionError` naming the field it
couldn't find — never a raw KeyError/AttributeError, and never a silent
wrong default.

Implement the functions below. Nothing else in this file needs to
change — the tests only import `LeaseAbstract`, `LeaseExtractionError`,
and `extract_lease_terms`.
"""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

AssignmentTerms = Literal["allowed", "not_allowed", "requires_consent"]


class LeaseExtractionError(Exception):
    """Raised when a required field cannot be located in the source lease text."""


class LeaseAbstract(BaseModel):
    base_rent_monthly: float = Field(gt=0)
    lease_term_months: int = Field(gt=0)
    renewal_option: bool
    renewal_term_months: int | None = Field(default=None, gt=0)
    permitted_use: str
    assignment_sublease: AssignmentTerms
    default_notice_days: int = Field(gt=0)

    @field_validator("permitted_use")
    @classmethod
    def _permitted_use_not_empty(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("permitted_use must not be empty")
        return stripped

    @model_validator(mode="after")
    def _check_renewal_consistency(self) -> "LeaseAbstract":
        if self.renewal_option and self.renewal_term_months is None:
            raise ValueError(
                "renewal_term_months must be set when renewal_option is True"
            )
        if not self.renewal_option and self.renewal_term_months is not None:
            raise ValueError(
                "renewal_term_months must be None when renewal_option is False"
            )
        return self


# A number in parentheses immediately followed by "months", e.g. "(36) months".
# Both the lease-term and renewal-term extraction helpers rely on this — the
# spelled-out word before the parenthetical ("sixty (60)") is not parsed,
# only the digits in parentheses are treated as authoritative.
_MONTHS_PATTERN = re.compile(r"\((\d+)\)\s*months", re.IGNORECASE)


def _sentences(text: str) -> list[str]:
    """Split lease text into naive sentence-ish chunks on '. ' boundaries."""
    return [s.strip() for s in re.split(r"(?<=\.)\s+", text) if s.strip()]


def _extract_base_rent(text: str) -> float:
    """
    Find the monthly base rent dollar amount. Look for a sentence that
    mentions "rent" and pull the first "$X,XXX.XX"-style figure out of it.

    TODO: implement this. Raise LeaseExtractionError("base_rent_monthly: ...")
    if no such sentence/amount can be found.
    """
    raise NotImplementedError


def _extract_lease_term_months(text: str) -> int:
    """
    Find the primary lease term length in months. Look for a sentence that
    mentions "term" but is NOT talking about a renewal/extension option
    (i.e. doesn't also mention "renew", "extend", "additional", or
    "option"), and pull the number out of its "(NN) months" parenthetical.

    TODO: implement this. Raise LeaseExtractionError("lease_term_months: ...")
    if no such sentence/number can be found.
    """
    raise NotImplementedError


def _extract_renewal_option(text: str) -> bool:
    """
    Determine whether the lease grants a renewal/extension option.

    Check for an explicit negation first (e.g. "no option ... to renew or
    extend") — if found, the answer is False regardless of anything else.
    Otherwise, look for positive language ("option to renew" / "option to
    extend").

    TODO: implement this.
    """
    raise NotImplementedError


def _extract_renewal_term_months(text: str) -> int:
    """
    Find the renewal/extension term length in months. Only called when
    `_extract_renewal_option` returned True. Look for a sentence mentioning
    "renew" or "extend" and pull the number out of its "(NN) months"
    parenthetical.

    TODO: implement this. Raise LeaseExtractionError("renewal_term_months: ...")
    if renewal_option is True but no renewal term length can be found.
    """
    raise NotImplementedError


def _extract_permitted_use(text: str) -> str:
    """
    Find the free-text description of the permitted use of the premises.
    Look for phrasing like "shall be used solely for ..." or "shall use
    the Premises exclusively for ...", capturing everything up to a
    terminator like ", and for no other ..." or the end of the sentence.

    TODO: implement this. Raise LeaseExtractionError("permitted_use: ...")
    if no such phrase can be found.
    """
    raise NotImplementedError


def _extract_assignment_sublease(text: str) -> AssignmentTerms:
    """
    Classify the lease's assignment/subletting terms. Scan sentences that
    mention "assign" in order, and classify the first one that clearly
    fits one of three buckets:

      - "allowed"          — permissive language ("may ... without ...
                              consent", "freely assign", etc.)
      - "requires_consent"  — mentions "consent" without permissive framing
      - "not_allowed"       — prohibitive language ("shall not ...",
                              "prohibited") with no consent mechanism

    TODO: implement this. Raise LeaseExtractionError("assignment_sublease: ...")
    if no sentence in the text can be classified.
    """
    raise NotImplementedError


def _extract_default_notice_days(text: str) -> int:
    """
    Find the cure/notice period on default, in days. Look for a sentence
    that mentions both "default" and "cure", and pull the number out of
    its "(NN) days" parenthetical.

    TODO: implement this. Raise LeaseExtractionError("default_notice_days: ...")
    if no such sentence/number can be found.
    """
    raise NotImplementedError


def extract_lease_terms(text: str) -> LeaseAbstract:
    """
    Parse raw lease text into a validated LeaseAbstract.

    Required fields that cannot be found in the source text must raise
    LeaseExtractionError naming the field — never let a raw
    KeyError/AttributeError/regex None-access propagate, and never
    silently default a missing value.

    TODO: implement this by calling the helper functions above (or your
    own) and constructing a LeaseAbstract from their results.
    """
    raise NotImplementedError
