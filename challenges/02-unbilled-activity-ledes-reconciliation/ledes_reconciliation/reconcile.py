"""
Challenge 02 — Unbilled Activity & LEDES Reconciliation

Attorneys and paralegals block off calendar time and send summary emails
that never get logged against a matter. That eats non-billable admin time
to clean up later, and it quietly loses real billable time when nobody
gets around to the cleanup at all.

This module takes raw activity entries (the kind you'd scrape from a
calendar export or a timekeeper's end-of-day notes) and reconciles each
one to:

  1. a matter, by resolving an explicit matter reference in the text or,
     failing that, fuzzy-matching the client's name against the entry
     text, and
  2. a LEDES/UTBMS-style task/activity code, by matching keywords in the
     entry text against an ordered list of billing code rules.

Entries that can't be resolved to a matter fall into a review queue
instead of being silently dropped or mis-billed — a partner has to look
at those by hand.

Implement the four functions below. Nothing else in this file needs to
change — the tests only call `reconcile_activity` and the three helpers
it depends on.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field

from rapidfuzz import fuzz

FUZZY_MATCH_THRESHOLD = 85.0

_MATTER_REF_PATTERN = re.compile(r"[Mm]-(\d{4})")


@dataclass
class MatterRef:
    matter_id: str
    client_name: str

    @classmethod
    def from_dict(cls, data: dict) -> "MatterRef":
        return cls(matter_id=data["matter_id"], client_name=data["client_name"])


@dataclass
class CodeRule:
    category: str
    task_code: str
    activity_code: str
    keywords: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "CodeRule":
        return cls(
            category=data["category"],
            task_code=data["task_code"],
            activity_code=data["activity_code"],
            keywords=data.get("keywords", []),
        )


@dataclass
class RawActivityEntry:
    entry_id: str
    timekeeper: str
    date: str
    duration_minutes: float
    description: str

    @classmethod
    def from_dict(cls, data: dict) -> "RawActivityEntry":
        return cls(
            entry_id=data["entry_id"],
            timekeeper=data["timekeeper"],
            date=data["date"],
            duration_minutes=data["duration_minutes"],
            description=data["description"],
        )


@dataclass
class LedesLine:
    entry_id: str
    matter_id: str
    timekeeper: str
    date: str
    task_code: str
    activity_code: str
    units: float
    narrative: str


@dataclass
class ReconciliationResult:
    billed: list[LedesLine]
    needs_review: list[RawActivityEntry]


def extract_matter_reference(text: str) -> str | None:
    """
    Find an explicit matter reference in free text and return it in
    normalized form, e.g. "M-2031".

    The reference pattern is the letter "M" (case-insensitive), a hyphen,
    and exactly four digits — "M-2031", "m-2031". Return the match
    normalized to an uppercase "M" followed by the digits as found (e.g.
    "M-2031"), or None if no such reference appears anywhere in the text.

    If the text contains more than one reference, return the first one
    (leftmost in the string).

    TODO: implement this.
    """
    raise NotImplementedError


def resolve_matter(entry: RawActivityEntry, matters: list[MatterRef]) -> MatterRef | None:
    """
    Resolve a raw activity entry to a known matter.

    Resolution order:
      1. Look for an explicit matter reference in `entry.description` via
         `extract_matter_reference`. If found and it matches the
         `matter_id` of one of `matters`, return that matter.
      2. Otherwise (no explicit reference, or it doesn't match any known
         matter), fall back to fuzzy-matching each matter's `client_name`
         against `entry.description`. Use `rapidfuzz.fuzz.partial_ratio`
         (case-insensitive — lowercase both sides) between
         `matter.client_name` and `entry.description`. A matter is a
         candidate if its score is >= `FUZZY_MATCH_THRESHOLD` (85). If
         more than one matter clears the threshold, return the
         highest-scoring one.
      3. If nothing resolves either way, return None.

    TODO: implement this.
    """
    raise NotImplementedError


def classify_activity(text: str, code_rules: list[CodeRule]) -> CodeRule:
    """
    Classify free text against an ordered list of billing code rules and
    return the matching rule.

    Walk `code_rules` in the order given. For each rule with a non-empty
    `keywords` list, if any keyword appears as a case-insensitive
    substring of `text`, return that rule immediately — first match in
    list order wins, even if a later rule's keyword also appears in the
    text and would otherwise seem like a "better" match.

    A rule with an empty `keywords` list is a fallback/catch-all: it
    matches any text, but only once every earlier rule with keywords has
    been checked and none matched. The fixtures always include exactly
    one such fallback rule at the end of the list, so this function
    always returns a rule and never raises for a valid `code_rules` list.

    TODO: implement this.
    """
    raise NotImplementedError


def to_units(duration_minutes: float) -> float:
    """
    Convert a duration in minutes to billable units, rounded UP to the
    nearest 6-minute (0.1 unit) increment — standard timekeeping
    practice, so a timekeeper is never shorted for a partial increment.

    units = ceil(duration_minutes / 6) * 0.1, rounded to 1 decimal place
    to avoid floating point noise.

    A duration of 0 returns 0.0 (there's nothing to bill).

    Examples:
      1  minute  -> 0.1
      6  minutes -> 0.1
      7  minutes -> 0.2
      30 minutes -> 0.5
      33 minutes -> 0.6
      60 minutes -> 1.0

    TODO: implement this.
    """
    raise NotImplementedError


def reconcile_activity(
    entries: list[RawActivityEntry],
    matters: list[MatterRef],
    code_rules: list[CodeRule],
) -> ReconciliationResult:
    """
    Reconcile a batch of raw activity entries against known matters and
    billing code rules.

    For each entry, in order:
      1. Resolve its matter via `resolve_matter`.
      2. If a matter resolves, classify the entry's description via
         `classify_activity`, compute `units` via `to_units`, and build a
         `LedesLine` (narrative = the original description). Append it
         to `billed`.
      3. If no matter resolves, append the original `RawActivityEntry`
         (unmodified) to `needs_review`.

    Never raise on an individual entry and never drop one silently —
    every entry ends up in exactly one of `billed` or `needs_review`.

    TODO: implement this.
    """
    raise NotImplementedError
