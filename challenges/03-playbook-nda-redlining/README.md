# Challenge 03 — Playbook-Driven NDA Redlining

**Track:** Assisted billable (human-in-the-loop drafting)

## The problem

An inbound NDA lands from opposing counsel. Before an associate spends billable time marking it up, someone needs to check it against the firm's negotiation playbook: is the confidentiality term too long? Is the governing law somewhere the firm never agrees to litigate? Is there a non-solicit with no cap, or an indemnification clause with no ceiling?

Partners don't trust raw AI redlines on billable work product — a generative rewrite that silently changes contract language is a liability problem, not a time-saver. What they'll trust is a deterministic, explainable rule check: here are the five things we always check, here's exactly which ones this NDA violates, and here's the specific sentence that triggered each flag.

This challenge is scoped to structured flag extraction, not in-place text redlining. You are not inserting annotations at character offsets in the contract — that's fragile and out of scope. You're producing a list of `Flag` objects plus a `compliant: bool`. A rule that passes produces no flag at all; "compliant terms stay untouched" means exactly that — nothing is added, nothing is rewritten.

## The spec

The firm's playbook has five fixed rules:

1. **`confidentiality_term`** — the confidentiality obligation must not exceed 3 years, and must not be perpetual or indefinite. Detect a stated term via a phrase like "shall survive for a period of N years." If N > 3, or the survival clause is perpetual/indefinite, flag it. If no term is stated at all, don't flag — that's out of scope, don't guess.

2. **`governing_law`** — governing law must be one of an approved list: `Delaware`, `New York`, `Texas`. Detect via a phrase like "governed by the laws of the State of X." If the named state isn't approved, flag it, naming the state that was found.

3. **`non_solicit_cap`** — if a non-solicitation clause exists, its restriction period must not exceed 12 months. Detect a stated period via a phrase like "shall not solicit ... for a period of N months" (or years — convert to months). If the clause is absent entirely, don't flag — non-solicit is optional.

4. **`confidentiality_exclusions`** — the definition of "Confidential Information" must include the standard carve-out list: information that is or becomes publicly available, was already known, is independently developed, or is rightfully received from a third party. If the contract defines Confidential Information but never states this exclusions language, flag it as missing.

5. **`liability_cap`** — the contract must not impose unlimited liability or unlimited indemnification. Detect red-flag phrases such as "unlimited liability," or an indemnification clause requiring indemnification against "any and all" claims with no nearby limiting language (e.g. no "not to exceed" or "capped at"). If found, flag it.

These are regex/keyword heuristics, not NLP. They don't need to be bulletproof against arbitrary contract language — they need to be deterministic and correct against the fixtures in this challenge.

## What you implement

Everything lives in `nda_redline/redline.py`. Five functions have `TODO`s, one per rule:

- `check_confidentiality_term(text: str) -> Flag | None`
- `check_governing_law(text: str) -> Flag | None`
- `check_non_solicit_cap(text: str) -> Flag | None`
- `check_confidentiality_exclusions(text: str) -> Flag | None`
- `check_liability_cap(text: str) -> Flag | None`

And the aggregator:

- `redline_contract(contract_text: str, playbook: list[PlaybookRule]) -> RedlineResult` — runs all five checks (dispatch by `rule.rule_id` — a `_CHECKERS` table is already wired up) and aggregates the results.

The dataclasses (`PlaybookRule`, `Flag`, `RedlineResult`) are already defined and don't need to change. Each `Flag.note` should read like something an attorney could paste straight into a redline comment — specific and actionable, e.g. `"[NEGOTIATE: Confidentiality term of 5 years exceeds the 3-year playbook cap — request reduction to 3 years.]"`.

## Running the tests

```bash
pytest challenges/03-playbook-nda-redlining -v
```

They fail against the starter stub. When they're green, you've built a rule checker a partner would actually let near a real NDA.

## Hints

- `Flag.clause_excerpt` should be pulled straight from the source text — the sentence or phrase that triggered the flag — not paraphrased. A naive sentence splitter (split on `. ` ) is enough for the fixtures here.
- Write your regexes to match a whole sentence at a time where possible, so you can hand that same sentence back as the excerpt.
- For `confidentiality_exclusions` and `liability_cap`, the relevant language can be several sentences away from the definition it modifies — search a window of the document, not just one sentence.
- Read all five fixture contracts in `fixtures/contracts/` before writing any regex — `compliant_nda.txt` is your baseline; every other fixture is a one- or two-line diff away from it.
