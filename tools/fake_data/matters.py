"""Synthetic data for Challenge 01 — Intake Conflict Detection.

Schema matches challenges/01-intake-conflict-detection/fixtures/*.json exactly,
so output from this generator can drop straight into that challenge (or be
used to stress-test a solution well past the size of the fixed fixtures).
"""

from __future__ import annotations

from .common import FakeDataContext


def generate_matters(count: int, ctx: FakeDataContext) -> list[dict]:
    matters = []
    for i in range(count):
        client = ctx.company_name()
        matter_id = f"M-{1000 + i:04d}"
        aliases = [ctx.suffix_variant(client)] if ctx.random.random() < 0.6 else []
        subsidiaries = [ctx.company_name() for _ in range(ctx.random.randint(0, 2))]
        adverse_parties = [ctx.company_name() for _ in range(ctx.random.randint(1, 2))]
        matters.append(
            {
                "matter_id": matter_id,
                "status": ctx.random.choices(["open", "closed"], weights=[0.8, 0.2])[0],
                "client_name": client,
                "client_aliases": aliases,
                "subsidiaries": subsidiaries,
                "adverse_parties": adverse_parties,
            }
        )
    return matters


def generate_webhooks(count: int, matters: list[dict], ctx: FakeDataContext, conflict_rate: float = 0.35) -> list[dict]:
    """Generate intake webhooks. `conflict_rate` of them are deliberately
    built to conflict with an existing matter (either direction); the rest
    are clean intakes with freshly generated names.
    """
    webhooks = []
    for i in range(count):
        intake_id = f"W-{2000 + i:04d}"
        if matters and ctx.random.random() < conflict_rate:
            matter = ctx.random.choice(matters)
            if ctx.random.random() < 0.5 and matter["adverse_parties"]:
                # prospective client conflicts with this matter's adverse party
                webhooks.append(
                    {
                        "intake_id": intake_id,
                        "prospective_client": ctx.random.choice(matter["adverse_parties"]),
                        "related_entities": [],
                        "counterparties": [ctx.company_name()],
                    }
                )
            else:
                # a counterparty on the new matter conflicts with this matter's client family
                family = [matter["client_name"], *matter["client_aliases"], *matter["subsidiaries"]]
                webhooks.append(
                    {
                        "intake_id": intake_id,
                        "prospective_client": ctx.company_name(),
                        "related_entities": [],
                        "counterparties": [ctx.random.choice(family)],
                    }
                )
        else:
            webhooks.append(
                {
                    "intake_id": intake_id,
                    "prospective_client": ctx.company_name(),
                    "related_entities": [ctx.company_name()] if ctx.random.random() < 0.2 else [],
                    "counterparties": [ctx.company_name() for _ in range(ctx.random.randint(1, 2))],
                }
            )
    return webhooks
