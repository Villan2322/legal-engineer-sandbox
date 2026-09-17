"""
Challenge 05 — Privilege Scrubber & PII Guardrails

Before any query or document snippet leaves the firm's perimeter to an
external LLM, privilege markers need to be stripped and sensitive entities
redacted — with a LOCAL, reversible mapping so the attorney can see the real
names again once the response comes back. This is the piece that lets a
firm safely call a generic external LLM at all without leaking privileged
or personally identifying content.

The pipeline has three stages, run in this order by `scrub`:

  1. `strip_privilege_markers` — remove privilege legend lines (these are
     metadata about privilege status, not privileged content themselves, so
     they're stripped permanently rather than reversibly redacted).
  2. `redact_known_entities` — replace every occurrence of a name the firm
     already knows about (attorneys, clients, contacts) with a stable
     placeholder.
  3. `redact_pii` — replace emails, phone numbers, and SSNs found in the
     remaining text with stable placeholders.

`scrub` merges the mappings from steps 2 and 3 into a single ScrubResult.
`unscrub` reverses it, so the response that comes back from the external
LLM can be de-anonymized locally before an attorney ever sees it.

Implement the functions below. Nothing else in this file needs to change —
the tests only call `strip_privilege_markers`, `redact_pii`,
`redact_known_entities`, `scrub`, and `unscrub`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class ScrubResult:
    scrubbed_text: str
    mapping: dict[str, str] = field(default_factory=dict)


def strip_privilege_markers(text: str) -> str:
    """
    Remove standalone privilege legend lines/headers such as:

      - "PRIVILEGED AND CONFIDENTIAL"
      - "ATTORNEY WORK PRODUCT"
      - "ATTORNEY-CLIENT PRIVILEGED COMMUNICATION"

    Matching must be case-insensitive and tolerant of the line also being
    wrapped in dashes/asterisks/etc, e.g. "--- PRIVILEGED AND CONFIDENTIAL
    ---". These typically appear as their own line at the top or bottom of
    an email or memo.

    Remove the whole line. Any leading/trailing blank line left behind by
    the removal should be collapsed to at most one blank line. The
    substantive text should otherwise be unchanged.

    TODO: implement this.
    """
    raise NotImplementedError


def redact_pii(text: str) -> ScrubResult:
    """
    Redact PII patterns with stable, per-call sequential placeholders:

      - Email addresses                -> [REDACTED_EMAIL_N]
      - US phone numbers                -> [REDACTED_PHONE_N]
        (formats: "(555) 123-4567", "555-123-4567", "555.123.4567")
      - SSNs in the format 123-45-6789  -> [REDACTED_SSN_N]

    Numbering is independent per category and assigned in order of first
    appearance in the text (i.e. the first email found becomes
    [REDACTED_EMAIL_1], the first phone number found becomes
    [REDACTED_PHONE_1], etc). If the exact same string appears more than
    once in the text, every occurrence must reuse the same placeholder —
    don't burn a new number on a repeat.

    TODO: implement this.
    """
    raise NotImplementedError


def redact_known_entities(text: str, known_entities: list[str]) -> ScrubResult:
    """
    Redact every occurrence of each name in `known_entities` with a
    placeholder [REDACTED_PERSON_N].

    Matching is case-insensitive and must use word boundaries so a name
    like "Grant Sable" doesn't accidentally match inside an unrelated word
    (e.g. "Grantham"). Numbering is assigned by order of first appearance
    across the whole text, one number per distinct entity — every
    occurrence of the SAME entity gets the SAME number.

    Match longer names before shorter ones so that a longer name
    containing a shorter one as a substring (e.g. "Jane Doe-Smith" vs
    "Jane Doe") isn't partially clobbered by the shorter match.

    TODO: implement this.
    """
    raise NotImplementedError


def scrub(text: str, known_entities: list[str]) -> ScrubResult:
    """
    Orchestrate the full pipeline, in this order:

      1. strip_privilege_markers
      2. redact_known_entities
      3. redact_pii

    Return a single ScrubResult whose mapping merges everything redacted in
    steps 2 and 3 (placeholder keys across categories won't collide since
    each category has a distinct prefix).

    TODO: implement this.
    """
    raise NotImplementedError


def unscrub(text: str, mapping: dict[str, str]) -> str:
    """
    Reverse the redaction: replace every placeholder key found in `text`
    with its original value from `mapping`.

    TODO: implement this.
    """
    raise NotImplementedError
