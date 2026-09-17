"""Synthetic data for Challenge 04 — Commercial Lease Term Extraction.

Generates a randomized lease excerpt plus the `expected` LeaseAbstract field
values it should extract to, so generated leases double as extra test cases.
"""

from __future__ import annotations

from .common import FakeDataContext

_USES = [
    "general office use",
    "retail sale of consumer goods",
    "a full-service restaurant and bar",
    "light industrial warehousing and distribution",
    "a medical office and outpatient clinic",
]

_ASSIGNMENT_TEMPLATES = {
    "requires_consent": (
        "Tenant shall not assign this Lease or sublet the Premises without the prior written "
        "consent of Landlord, which consent shall not be unreasonably withheld."
    ),
    "not_allowed": (
        "Tenant shall not assign this Lease or sublet the Premises, in whole or in part, under "
        "any circumstances without exception."
    ),
    "allowed": (
        "Tenant may freely assign this Lease or sublet the Premises without obtaining Landlord's "
        "consent, provided Tenant gives Landlord written notice of any such assignment."
    ),
}


def generate_lease(ctx: FakeDataContext) -> dict:
    landlord = ctx.company_name()
    tenant = ctx.company_name()

    base_rent = ctx.random.choice([2500, 3200, 4800, 6100, 7500, 9200, 12000])
    lease_term_months = ctx.random.choice([12, 24, 36, 48, 60])
    renewal_option = ctx.random.random() < 0.6
    renewal_term_months = ctx.random.choice([12, 24, 36]) if renewal_option else None
    permitted_use = ctx.random.choice(_USES)
    assignment_key = ctx.random.choice(["requires_consent", "not_allowed", "allowed"])
    default_notice_days = ctx.random.choice([10, 15, 20, 30])

    renewal_clause = (
        f"Tenant shall have the option to renew this Lease for one additional term of "
        f"{renewal_term_months} months upon written notice to Landlord at least ninety (90) days "
        f"prior to expiration."
        if renewal_option
        else "This Lease does not grant Tenant any option to renew or extend the term."
    )

    text = f"""COMMERCIAL LEASE AGREEMENT

This Lease is entered into between {landlord} ("Landlord") and {tenant} ("Tenant") for the \
premises described herein.

Base Rent. Tenant shall pay Landlord base rent in the amount of ${base_rent:,.2f} per month, \
due on the first day of each calendar month.

Term. The term of this Lease shall be {lease_term_months} months, commencing on the Commencement \
Date set forth above.

Renewal. {renewal_clause}

Use of Premises. The Premises shall be used solely for {permitted_use} and for no other purpose \
without Landlord's prior written consent.

Assignment and Subletting. {_ASSIGNMENT_TEMPLATES[assignment_key]}

Default. In the event of a default by Tenant, Landlord shall provide written notice thereof, and \
Tenant shall have {default_notice_days} days from receipt of such notice to cure the default \
before Landlord may exercise its remedies under this Lease.
"""

    expected = {
        "base_rent_monthly": float(base_rent),
        "lease_term_months": lease_term_months,
        "renewal_option": renewal_option,
        "renewal_term_months": renewal_term_months,
        "permitted_use": permitted_use,
        "assignment_sublease": assignment_key,
        "default_notice_days": default_notice_days,
    }

    return {"text": text.strip() + "\n", "expected": expected}
