"""Shared helpers for the fake data generators."""

from __future__ import annotations

import random

from faker import Faker

CORPORATE_SUFFIXES = [
    "Inc.", "Inc", "LLC", "Corp", "Corporation", "Co.", "Company",
    "Ltd.", "Holdings", "PLLC", "PC", "LP",
]

# Faker's own company() sometimes appends one of these — strip it so we can
# control the suffix ourselves and generate suffix-variant aliases on demand.
_FAKER_SUFFIXES = (" Inc", " LLC", " Group", " and Sons", " PLC", " Ltd", " Ltd.")


class FakeDataContext:
    """Wraps a seeded Faker + random instance so a whole generation run is
    reproducible from one seed, and hands out a single shared instance to
    every generator function in a run instead of each one seeding globally.
    """

    def __init__(self, seed: int | None = None):
        self.faker = Faker()
        self.random = random.Random(seed)
        if seed is not None:
            Faker.seed(seed)

    def company_base(self) -> str:
        name = self.faker.company()
        for suffix in _FAKER_SUFFIXES:
            if name.endswith(suffix):
                name = name[: -len(suffix)]
        return name.strip()

    def company_name(self) -> str:
        return f"{self.company_base()} {self.random.choice(CORPORATE_SUFFIXES)}"

    def suffix_variant(self, name: str) -> str:
        """Return a plausible alternate rendering of the same company name —
        different corporate suffix and/or punctuation — for exercising fuzzy
        matching downstream (Challenge 01, Challenge 02).
        """
        base = name
        current_suffix = ""
        for suffix in sorted(CORPORATE_SUFFIXES, key=len, reverse=True):
            if base.endswith(" " + suffix):
                base = base[: -(len(suffix) + 1)]
                current_suffix = suffix
                break
        choices = [s for s in CORPORATE_SUFFIXES if s != current_suffix]
        new_suffix = self.random.choice(choices)
        return f"{base}, {new_suffix}" if self.random.random() < 0.5 else f"{base} {new_suffix}"

    def person_name(self) -> str:
        return self.faker.name()

    def phone_number(self) -> str:
        digits = [self.random.randint(2, 9)] + [self.random.randint(0, 9) for _ in range(9)]
        area, prefix, line = digits[0:3], digits[3:6], digits[6:10]
        fmt = self.random.choice(["paren", "dash", "dot"])
        area_s = "".join(map(str, area))
        prefix_s = "".join(map(str, prefix))
        line_s = "".join(map(str, line))
        if fmt == "paren":
            return f"({area_s}) {prefix_s}-{line_s}"
        if fmt == "dash":
            return f"{area_s}-{prefix_s}-{line_s}"
        return f"{area_s}.{prefix_s}.{line_s}"

    def ssn(self) -> str:
        return f"{self.random.randint(100, 899):03d}-{self.random.randint(10, 99):02d}-{self.random.randint(1000, 9999):04d}"

    def email_for(self, name: str) -> str:
        local = name.lower().replace(" ", ".").replace(",", "")
        return f"{local}@{self.faker.free_email_domain()}"
