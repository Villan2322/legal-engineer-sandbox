"""Synthetic data for Challenge 03 — Playbook-Driven NDA Redlining.

Generates a randomized NDA body text plus the `expected_violations` list of
rule_ids it *should* trigger against the challenge's fixed 5-rule playbook,
so generated contracts double as extra test cases, not just more reading
material.
"""

from __future__ import annotations

from .common import FakeDataContext

APPROVED_STATES = ["Delaware", "New York", "Texas"]
_OTHER_STATES = ["California", "Illinois", "Florida", "Nevada", "Massachusetts", "Georgia"]

EXCLUSIONS_CLAUSE = (
    " Confidential Information does not include information that (a) is or becomes publicly "
    "available through no fault of the receiving party, (b) was already known to the receiving "
    "party prior to disclosure, (c) is independently developed without use of the Confidential "
    "Information, or (d) is rightfully received from a third party without restriction."
)

CAPPED_LIABILITY_CLAUSE = (
    "Each party's liability arising under or in connection with this Agreement shall not exceed, "
    "and is capped at, the amounts paid under any related commercial agreement between the parties."
)

UNCAPPED_LIABILITY_CLAUSE = (
    "Each party agrees to indemnify and hold harmless the other party from any and all damages, "
    "losses, and liabilities of any kind arising from a breach of this Agreement, without limitation."
)


def generate_nda(ctx: FakeDataContext) -> dict:
    party_a = ctx.company_name()
    party_b = ctx.company_name()

    term_is_perpetual = ctx.random.random() < 0.15
    term_years = ctx.random.choice([1, 2, 3, 4, 5, 6])
    year_word = "year" if term_years == 1 else "years"
    term_clause = (
        "an indefinite period, with no fixed expiration"
        if term_is_perpetual
        else f"a period of {term_years} {year_word}"
    )

    state = ctx.random.choice(APPROVED_STATES + _OTHER_STATES)

    has_nonsolicit = ctx.random.random() < 0.7
    nonsolicit_months = ctx.random.choice([6, 12, 18, 24, 36]) if has_nonsolicit else None

    exclusions_present = ctx.random.random() < 0.6
    liability_capped = ctx.random.random() < 0.6

    if has_nonsolicit:
        nonsolicit_clause = (
            f"Each party agrees that it shall not solicit for employment the employees of the "
            f"other party who had access to Confidential Information, for a period of "
            f"{nonsolicit_months} months following the termination of this Agreement."
        )
    else:
        nonsolicit_clause = "This Agreement does not impose any non-solicitation obligation on either party."

    text = f"""NON-DISCLOSURE AGREEMENT

This Non-Disclosure Agreement (the "Agreement") is entered into by and between {party_a} \
("Discloser") and {party_b} ("Recipient").

1. Confidential Information. "Confidential Information" means any non-public business, \
technical, or financial information disclosed by either party to the other in connection with \
their discussions.{EXCLUSIONS_CLAUSE if exclusions_present else ""}

2. Term. The obligations of confidentiality set forth in this Agreement shall survive for \
{term_clause} following the date of disclosure.

3. Non-Solicitation. {nonsolicit_clause}

4. Governing Law. This Agreement shall be governed by the laws of the State of {state}, \
without regard to its conflict of laws principles.

5. Liability. {CAPPED_LIABILITY_CLAUSE if liability_capped else UNCAPPED_LIABILITY_CLAUSE}
"""

    expected_violations = []
    if term_is_perpetual or term_years > 3:
        expected_violations.append("confidentiality_term")
    if state not in APPROVED_STATES:
        expected_violations.append("governing_law")
    if has_nonsolicit and nonsolicit_months > 12:
        expected_violations.append("non_solicit_cap")
    if not exclusions_present:
        expected_violations.append("confidentiality_exclusions")
    if not liability_capped:
        expected_violations.append("liability_cap")

    return {"text": text.strip() + "\n", "expected_violations": expected_violations}
