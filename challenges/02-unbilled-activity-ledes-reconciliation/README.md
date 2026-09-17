# Challenge 02 — Unbilled Activity & LEDES Reconciliation

**Track:** Back office & ops

## The problem

Attorneys and paralegals block off calendar time and fire off email summaries that never get logged against a matter. Some of it is genuinely non-billable — but a lot of it is real work that just never made it into the billing system, because logging time to the right matter and task code is tedious and easy to defer until "later." Later rarely comes, and the firm eats the leak either way: non-billable hours spent reconstructing what happened, or billable hours nobody ever captured.

The fix isn't asking timekeepers to be more disciplined. It's parsing the raw activity — calendar blocks, email subject lines, whatever text trail exists — and doing the matching and coding a paralegal would otherwise do by hand, so a partner reviews clean LEDES/UTBMS billing lines instead of raw noise. Anything the system can't confidently resolve goes to a review queue instead of getting silently dropped or mis-billed.

## The spec

You're given:

- A list of `MatterRef` records — just a `matter_id` and `client_name` for each active matter.
- A list of `CodeRule` records — an ordered set of billing-code rules, each with a `task_code`/`activity_code` pair and a list of lowercase keywords to match against activity text. One rule is a catch-all with no keywords, placed last.
- A list of `RawActivityEntry` records — raw, unstructured activity: a timekeeper, a date, a duration in minutes, and a free-text description.

For each entry, reconcile it to a matter and a billing code:

1. **Matter resolution** — first look for an explicit matter reference in the text (a pattern like `M-2031`). If that's present and matches a known matter, use it. Otherwise, fuzzy-match each matter's client name against the entry text and take the best match above a threshold. If nothing resolves either way, the entry goes to a review queue instead of being guessed at.
2. **Code classification** — walk the billing code rules in order and take the first one whose keywords appear in the entry text. Order matters: if text could plausibly match two categories, the earlier rule in the list wins, every time. The catch-all rule at the end always matches, so every resolved entry gets *some* code.
3. **Units** — convert minutes to billable units in the standard 6-minute-increment way, rounded up. A timekeeper never gets shorted for a partial increment.

## What you implement

Everything lives in `ledes_reconciliation/reconcile.py`. Four functions have `TODO`s:

- `extract_matter_reference(text: str) -> str | None` — regex-extract an explicit `M-XXXX` matter code from text, case-insensitive on the "M", normalized to uppercase.
- `resolve_matter(entry, matters) -> MatterRef | None` — explicit reference first, fuzzy client-name match second (via `rapidfuzz.fuzz.partial_ratio`), `None` if nothing clears the bar.
- `classify_activity(text, code_rules) -> CodeRule` — first rule in list order whose keywords hit; the empty-keyword rule is the always-matching fallback.
- `to_units(duration_minutes: float) -> float` — ceiling-round to the nearest 0.1 unit (6-minute increment).
- `reconcile_activity(entries, matters, code_rules) -> ReconciliationResult` — ties the four functions above together: resolve each entry's matter, classify it, compute its units, and split the batch into `billed` LEDES lines and a `needs_review` queue for anything that didn't resolve.

The dataclasses (`MatterRef`, `CodeRule`, `RawActivityEntry`, `LedesLine`, `ReconciliationResult`) are already defined and don't need to change.

## Running the tests

```bash
pytest challenges/02-unbilled-activity-ledes-reconciliation -v
```

They fail against the starter stub. When they're green, you've built a reconciliation pass that would actually clear a partner's unbilled-time report.

## Hints

- `extract_matter_reference` only needs to find the pattern, not validate that the matter exists — `resolve_matter` is the one that checks it against known matters and decides whether to fall back to fuzzy matching.
- Fuzzy-match on the *un-normalized* client name against the *un-normalized* description — `partial_ratio` is already built to find the best-scoring substring alignment, so it doesn't need help from lowercasing beyond what the spec asks for.
- Don't optimize `classify_activity` by scanning for the "best" keyword match across all rules — the spec is explicit that list order wins over anything that looks like a stronger match further down the list. Iterate straight through in order and return on the first hit.
- `math.ceil` is your friend for `to_units`; watch out for float noise (`round(..., 1)` after the ceiling division) before comparing against expected values in the tests.
