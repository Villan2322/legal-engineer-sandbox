"""
Challenge 03 — Playbook-Driven NDA Redlining

An inbound NDA needs to be checked against a firm's five-rule negotiation
playbook. Terms within the playbook's bounds should pass silently — no
flag, no edit, nothing for the attorney to look at. Terms outside the
playbook's bounds should produce a structured `Flag` with a clear,
bracketed negotiation note an attorney can act on immediately.

This is deliberately NOT generative redlining. You are not rewriting the
contract or inserting annotations at character offsets — you're extracting
a list of `Flag` objects plus a `compliant: bool`. Partners don't trust raw
AI redlines; they trust a deterministic, explainable rule check they can
audit line by line.

Implement the five `check_*` functions and `redline_contract` below.
Nothing else in this file needs to change — the tests call the `check_*`
functions directly and `redline_contract` end to end.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable

# The firm's approved governing-law jurisdictions (rule: governing_law).
APPROVED_GOVERNING_LAW = ("Delaware", "New York", "Texas")


@dataclass
class PlaybookRule:
    rule_id: str
    name: str
    description: str


@dataclass
class Flag:
    rule_id: str
    clause_excerpt: str  # the sentence/phrase from the source text that triggered the flag
    note: str            # a bracketed attorney negotiation note, e.g. "[NEGOTIATE: ...]"


@dataclass
class RedlineResult:
    compliant: bool       # True only if `flags` is empty
    flags: list[Flag]


def _sentences(text: str) -> list[str]:
    """Naive sentence splitter: split after a period followed by whitespace."""
    raw = re.split(r"(?<=[.])\s+", text.strip())
    return [s.strip() for s in raw if s.strip()]


def check_confidentiality_term(text: str) -> Flag | None:
    """
    Rule: confidentiality_term.

    The confidentiality/survival obligation must not exceed 3 years, and
    must not be perpetual or indefinite.

    Detect a stated term via a phrase like "shall survive for a period of
    N years" (you can rely on the exact fixture wording, but write the
    regex to be reasonably tolerant). If N > 3, or the sentence mentions
    "perpetual"/"perpetuity"/"indefinite" in the survival context, return a
    Flag whose `clause_excerpt` is the offending sentence.

    If no term is stated anywhere in the text, return None — that's out of
    scope for this rule, don't guess.

    TODO: implement this.
    """
    raise NotImplementedError


def check_governing_law(text: str) -> Flag | None:
    """
    Rule: governing_law.

    Governing law must be one of APPROVED_GOVERNING_LAW. Detect via a
    phrase like "governed by the laws of the State of X". If the state
    named is not on the approved list, return a Flag naming the state that
    was found, with `clause_excerpt` set to the sentence containing the
    clause.

    If no governing-law clause is found at all, return None.

    TODO: implement this.
    """
    raise NotImplementedError


def check_non_solicit_cap(text: str) -> Flag | None:
    """
    Rule: non_solicit_cap.

    If a non-solicitation clause exists, its restriction period must not
    exceed 12 months. Detect a stated period via a phrase like "shall not
    solicit ... for a period of N months" (or "N years" — convert to
    months: 1 year = 12 months).

    If no non-solicitation clause is present at all, return None — a
    non-solicit clause is optional, its absence is not a violation.

    TODO: implement this.
    """
    raise NotImplementedError


def check_confidentiality_exclusions(text: str) -> Flag | None:
    """
    Rule: confidentiality_exclusions.

    The definition of "Confidential Information" must include the standard
    carve-out/exclusions list: information that is or becomes publicly
    available, was already known, is independently developed, or is
    rightfully received from a third party.

    Detect by checking whether the contract defines "Confidential
    Information" at all (if it doesn't, this rule is out of scope — return
    None). If it does, look for an exclusions section: a phrase like "does
    not include" or "shall not include", followed (within a reasonable
    window of text) by a mention of "publicly available" or "public
    domain". If the definition exists but no such exclusions language is
    found anywhere in the document, return a Flag noting the exclusions are
    missing, with `clause_excerpt` set to the sentence that defines
    Confidential Information.

    TODO: implement this.
    """
    raise NotImplementedError


def check_liability_cap(text: str) -> Flag | None:
    """
    Rule: liability_cap.

    The contract must not impose unlimited liability or unlimited
    indemnification. Detect red-flag phrases such as "unlimited liability",
    or an indemnification clause using language like "indemnify and hold
    harmless ... any and all" without a nearby limiting phrase (e.g.
    without "not to exceed" or "capped at" appearing nearby). If found,
    return a Flag with `clause_excerpt` set to the offending sentence.

    TODO: implement this.
    """
    raise NotImplementedError


# Dispatch table used by redline_contract — maps a playbook rule_id to the
# check function that implements it.
_CHECKERS: dict[str, Callable[[str], Flag | None]] = {
    "confidentiality_term": check_confidentiality_term,
    "governing_law": check_governing_law,
    "non_solicit_cap": check_non_solicit_cap,
    "confidentiality_exclusions": check_confidentiality_exclusions,
    "liability_cap": check_liability_cap,
}


def redline_contract(contract_text: str, playbook: list[PlaybookRule]) -> RedlineResult:
    """
    Run every rule in `playbook` against `contract_text` (dispatching by
    `rule.rule_id` via `_CHECKERS`) and aggregate the results into a
    RedlineResult. `compliant` is True only when no rule produced a Flag.

    TODO: implement this.
    """
    raise NotImplementedError
