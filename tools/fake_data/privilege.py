"""Synthetic data for Challenge 05 — Privilege Scrubber & PII Guardrails.

Generates a memo-style document with a privilege legend, PII (email, phone,
SSN), and known-entity names repeated multiple times — enough surface area
to exercise stable placeholder reuse and the longest-match-first rule for
overlapping entity names.
"""

from __future__ import annotations

from .common import FakeDataContext

_MARKERS = [
    "PRIVILEGED AND CONFIDENTIAL",
    "ATTORNEY WORK PRODUCT",
    "ATTORNEY-CLIENT PRIVILEGED COMMUNICATION",
]


def generate_privileged_doc(ctx: FakeDataContext, extra_known_entities: list[str] | None = None) -> dict:
    attorney = ctx.person_name()
    client_contact = ctx.person_name()
    # Deliberately include a name that's a prefix of another to exercise
    # longest-match-first redaction, mirroring the fixed challenge fixture.
    collision_base = ctx.person_name()
    collision_extended = f"{collision_base}-{ctx.faker.last_name()}"

    known_entities = [attorney, client_contact, collision_base, collision_extended]
    if extra_known_entities:
        known_entities.extend(extra_known_entities)

    email = ctx.email_for(client_contact)
    phone = ctx.phone_number()
    ssn = ctx.ssn()

    marker_top = ctx.random.choice(_MARKERS)
    marker_bottom = ctx.random.choice(_MARKERS)
    wrap = ctx.random.random() < 0.5

    def marker_line(text: str) -> str:
        return f"--- {text} ---" if wrap else text

    body = f"""{marker_line(marker_top)}

To: {attorney}
From: {client_contact}
Re: Settlement discussion follow-up

{attorney}, following up on our call — {client_contact} can be reached at {email} or {phone} \
for any follow-up questions. {collision_base} should be copied on the next round, but please \
route billing correspondence to {collision_extended} directly, not {collision_base}.

For file verification purposes, {client_contact}'s reference number on record is {ssn}. Please \
do not forward this memo outside the deal team.

{marker_line(marker_bottom)}
"""

    return {
        "text": body.strip() + "\n",
        "known_entities": known_entities,
        "pii": {"emails": [email], "phones": [phone], "ssns": [ssn]},
    }
