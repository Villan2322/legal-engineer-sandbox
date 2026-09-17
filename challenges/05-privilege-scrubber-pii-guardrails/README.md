# Challenge 05 — Privilege Scrubber & PII Guardrails

**Track:** Governance & proprietary infrastructure

## The problem

Every generic AI tool a firm plugs into is a potential privilege leak. Before a query or document snippet can go out to an external LLM, someone needs to strip the privilege legends off the top of the email, redact the names, emails, phone numbers, and SSNs that shouldn't leave the building — and then, when the response comes back, turn those placeholders back into real names so the attorney isn't reading a wall of `[REDACTED_PERSON_3]`.

Doing this by hand doesn't scale, and doing it wrong is a malpractice problem, not a bug ticket. The redaction also has to be *reversible* — the whole point is that the attorney gets a normal, readable answer back, with the mapping from placeholder to real identity kept entirely local and never sent anywhere.

## The spec

You're given a block of free text (an email, a memo excerpt, a client intake note) and a list of known entities (attorneys, clients, contacts the firm already has on file). The scrubbing pipeline runs in three stages:

1. **Strip privilege markers** — legend lines like `PRIVILEGED AND CONFIDENTIAL`, `ATTORNEY WORK PRODUCT`, or `ATTORNEY-CLIENT PRIVILEGED COMMUNICATION` get removed outright. They're metadata about the document's privilege status, not privileged content themselves, so they're gone for good — not reversibly redacted.
2. **Redact known entities** — every occurrence of a name the firm already knows about gets replaced with a stable `[REDACTED_PERSON_N]` placeholder.
3. **Redact PII patterns** — emails, phone numbers, and SSNs found anywhere in the remaining text get replaced with `[REDACTED_EMAIL_N]` / `[REDACTED_PHONE_N]` / `[REDACTED_SSN_N]` placeholders.

Every redaction is recorded in a local mapping. Once the external LLM's response comes back, `unscrub` reverses the whole thing so the attorney sees real names and real contact details again.

## What you implement

Everything lives in `privilege_scrubber/scrubber.py`. Five functions have `TODO`s:

- `strip_privilege_markers(text: str) -> str` — remove standalone privilege legend lines (case-insensitive, tolerant of dash/asterisk wrapping), collapsing any blank line left behind to at most one.
- `redact_pii(text: str) -> ScrubResult` — redact emails, US phone numbers, and SSNs with stable, sequentially-numbered placeholders (numbered independently per category, in order of first appearance; repeats of the exact same value reuse the same placeholder).
- `redact_known_entities(text: str, known_entities: list[str]) -> ScrubResult` — redact every occurrence of each known name (case-insensitive, whole-word/phrase matching, longest names matched first so a name like `"Jane Doe-Smith"` doesn't get clobbered by a shorter `"Jane Doe"` match).
- `scrub(text: str, known_entities: list[str]) -> ScrubResult` — orchestrate all three above, in order (markers, then entities, then PII), and return one `ScrubResult` with a single merged mapping.
- `unscrub(text: str, mapping: dict[str, str]) -> str` — reverse the redaction using the mapping.

The `ScrubResult` dataclass (`scrubbed_text`, `mapping`) is already defined and doesn't need to change.

## Running the tests

```bash
pytest challenges/05-privilege-scrubber-pii-guardrails -v
```

They fail against the starter stub. When they're green, you've built the piece that lets a firm actually point an external LLM at real client correspondence without gambling on privilege.

## Hints

- Sort known entities by length, longest first, before building your match pattern — that's what keeps `"Jane Doe-Smith"` from being partially matched and mangled by a `"Jane Doe"` rule.
- `\b` word boundaries matter on both sides of a name — without a trailing boundary, `"Grant Sable"` would also match the first eleven characters of an unrelated `"Grant Sableton"`.
- Keep placeholder numbering scoped per category (`EMAIL`, `PHONE`, `SSN`, `PERSON`) and assign numbers in order of first appearance, not in some arbitrary scan order — the round trip only works if the mapping is unambiguous.
- `unscrub` doesn't need to know anything about categories — it's a pure placeholder-to-value substitution over whatever mapping `scrub` handed you.
