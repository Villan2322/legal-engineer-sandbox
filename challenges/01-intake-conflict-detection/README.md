# Challenge 01 — Intake Conflict Detection

**Track:** Back office & ops (zero billable threat)

## The problem

A new-matter intake webhook lands with a prospective client name and the counterparties on the other side of the deal or dispute. Before anyone spends billable or non-billable time opening the matter, the firm needs an answer: does this conflict with anything already on the books?

Firms track this by hand today — a paralegal searches a client list, squints at name variants, and hopes they didn't miss a subsidiary. It's slow, it doesn't scale past a few hundred matters, and it's exactly the kind of check a computer should be doing before a human ever sees the intake form.

## The spec

You're given:

- A list of `Matter` records — each with a client name, known aliases, subsidiaries, and the parties the firm is adverse to on that matter.
- An `IntakeWebhook` — a prospective client name, any related entities (e.g. its own subsidiaries), and the counterparties involved in the new matter.

A conflict exists when a name on the webhook matches a name already tracked on a matter, in either direction:

1. **`counterparty_is_client`** — a counterparty in the new matter matches the client, a client alias, or a client subsidiary on an existing matter. The firm would be adverse to its own client.
2. **`prospective_client_is_adverse_party`** — the prospective client (or a related entity) matches a name the firm is already adverse to on an existing matter. The firm would be representing someone it's currently opposing elsewhere.

Matching has to survive the real-world mess of corporate names: `"Blue Harbor Logistics, Inc."`, `"Blue Harbor Logistics Corp"`, and `"blue harbor logistics"` all refer to the same entity. But it also has to *not* over-match — `"Alliance Medical Group"` and `"Alliance Home Health Group"` are different companies that happen to share two words, and should not trigger a conflict.

## What you implement

Everything lives in `intake_conflict/conflict_check.py`. Three functions have `TODO`s:

- `normalize_entity_name(name: str) -> str` — lowercase, strip punctuation, strip trailing corporate suffixes (Inc, LLC, Corp, ...), collapse whitespace.
- `fuzzy_match_score(a: str, b: str) -> float` — a 0-100 similarity score between two names, computed on their normalized forms. Use `rapidfuzz` (already a dependency) — don't hand-roll edit distance.
- `find_conflicts(webhook, matters, threshold=88.0) -> ConflictReport` — run both match directions against every matter and return the hits at or above threshold. One hit per (matter, direction) — don't emit duplicates when multiple names on one side match the same matter.

The dataclasses (`Matter`, `IntakeWebhook`, `ConflictHit`, `ConflictReport`) are already defined and don't need to change.

## Running the tests

```bash
pytest challenges/01-intake-conflict-detection -v
```

They fail against the starter stub. When they're green, you've built a conflict checker that would actually save a paralegal's morning.

## Hints

- `rapidfuzz.fuzz.token_sort_ratio` handles word-order differences; it's a reasonable default here since entity names are usually 2-4 tokens.
- Don't match against an empty string — normalizing a name down to nothing (rare, but possible with a name that's *only* a suffix) shouldn't produce a false match.
- The threshold is a real design decision, not just a test-passing knob: too low and you drown reviewers in false positives; too high and you miss real conflicts. 88 is provided as a starting point that the test fixtures are tuned against — if you change it, make sure you understand why.
