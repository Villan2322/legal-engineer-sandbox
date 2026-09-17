"""Synthetic data for Challenge 02 — Unbilled Activity & LEDES Reconciliation.

Takes the real matters.json / code_rules.json for that challenge (or ones you
generated yourself) as input, so generated entries always classify and
resolve against rules/matters that actually exist.
"""

from __future__ import annotations

import datetime

from .common import FakeDataContext

_ACTIONS = ["Call with", "Email to", "Meeting re", "Follow-up with", "Update for"]


def generate_activity_entries(
    count: int,
    matters: list[dict],
    code_rules: list[dict],
    ctx: FakeDataContext,
    unresolved_rate: float = 0.15,
    explicit_ref_rate: float = 0.5,
) -> list[dict]:
    entries = []
    keyworded_rules = [r for r in code_rules if r.get("keywords")]
    today = datetime.date.today()

    for i in range(count):
        entry_id = f"A-{3000 + i:04d}"
        timekeeper = ctx.person_name()
        date = (today - datetime.timedelta(days=ctx.random.randint(0, 29))).isoformat()
        duration_minutes = ctx.random.choice([5, 6, 12, 15, 18, 20, 25, 30, 33, 45, 60, 90])

        keyword_phrase = ""
        if keyworded_rules:
            rule = ctx.random.choice(keyworded_rules)
            keyword_phrase = ctx.random.choice(rule["keywords"])

        action = ctx.random.choice(_ACTIONS)

        if matters and ctx.random.random() >= unresolved_rate:
            matter = ctx.random.choice(matters)
            if ctx.random.random() < explicit_ref_rate:
                subject = f"{matter['matter_id']} ({matter['client_name']})"
            else:
                subject = matter["client_name"]
            description = f"{action} {subject} — {keyword_phrase}".strip(" —")
        else:
            # Deliberately unresolvable: no matter code, no known client name.
            description = f"{action} {ctx.company_name()} — {keyword_phrase}".strip(" —")

        entries.append(
            {
                "entry_id": entry_id,
                "timekeeper": timekeeper,
                "date": date,
                "duration_minutes": duration_minutes,
                "description": description,
            }
        )
    return entries
