# Challenge 04 — Commercial Lease Term Extraction

**Track:** Assisted billable (human-in-the-loop drafting)

## The problem

Before an M&A deal or a commercial real estate financing closes, someone has to know exactly what the target's leases say — base rent, how much term is left, whether there's a renewal option, what the space can be used for, whether the lease can be assigned if the deal is structured as an asset sale, and how long there is to cure a default. This is due diligence prep, and today it means a paralegal reading a 40-page lease front to back and filling in an abstract spreadsheet, one lease at a time.

Lease language is not standardized. Two leases covering the same terms will say so in completely different words, in a different order, with different section headings. An abstraction tool that only works on one law firm's own template is useless the moment a target company's leases come from ten different landlords' forms. That's the extraction problem this challenge is about.

## The spec

You're given raw lease text (a `str` — the body of a single commercial lease). You need to extract seven fields into a validated `LeaseAbstract`:

| Field | Type | Notes |
|---|---|---|
| `base_rent_monthly` | `float` | Must be > 0 |
| `lease_term_months` | `int` | Must be > 0 |
| `renewal_option` | `bool` | Whether the lease grants a renewal/extension option |
| `renewal_term_months` | `int \| None` | Set if `renewal_option` is True (must be > 0); must be `None` if `renewal_option` is False |
| `permitted_use` | `str` | Free text describing what the premises may be used for; non-empty |
| `assignment_sublease` | `Literal["allowed", "not_allowed", "requires_consent"]` | How the lease treats assignment/subletting |
| `default_notice_days` | `int` | The cure/notice period on default; must be > 0 |

`LeaseAbstract` is a `pydantic` `BaseModel` — invalid combinations (e.g. a zero rent, or a `renewal_term_months` set while `renewal_option` is False) are rejected by validators, not left to the caller to notice.

A second class, `LeaseExtractionError`, is a plain `Exception` you raise — naming the field — when a *required* field's value genuinely cannot be found anywhere in the source text. A lease missing its default-notice language entirely should fail loudly and specifically, not crash with a raw `AttributeError` from a `None` regex match, and not silently get defaulted to some made-up number of days. A wrong abstract that looks confident is worse than no abstract at all — a partner who trusts a bad extraction signs off on the wrong deal terms.

## What you implement

Everything lives in `lease_extraction/extract.py`. The `LeaseAbstract` model and `LeaseExtractionError` are already defined and don't need to change. Implement:

- `extract_lease_terms(text: str) -> LeaseAbstract` — the one public entry point. Parse the raw text with regex/keyword heuristics for each field, then construct and return a validated `LeaseAbstract`.

The stub also sketches seven small private helper functions (`_extract_base_rent`, `_extract_lease_term_months`, `_extract_renewal_option`, `_extract_renewal_term_months`, `_extract_permitted_use`, `_extract_assignment_sublease`, `_extract_default_notice_days`), each with its own `TODO` docstring describing the heuristic it should use. You don't have to keep exactly this split — it's there because per-field helpers are easier to get right (and to unit-test against a fixture) than one giant regex — but the public surface tests import is just `extract_lease_terms`, `LeaseAbstract`, and `LeaseExtractionError`.

## Running the tests

```bash
pytest challenges/04-lease-term-extraction -v
```

They fail against the starter stub. When they're green, you've built something that would actually save a paralegal a full read-through per lease.

## Hints

- Work sentence by sentence, not against the whole document in one regex. Split on `. ` boundaries and search each chunk for the keywords relevant to the field you're extracting (`"rent"`, `"term"` without `"renew"`/`"extend"`, `"default"` and `"cure"` together, and so on). This is what keeps you from grabbing the wrong number when a document mentions several dollar amounts or several "(NN) months"/"(NN) days" parentheticals.
- Lease drafters spell out numbers and then parenthesize the digits — `"sixty (60) months"`, `"fifteen (15) days"`. Parse the digits in parentheses; don't try to parse English number words.
- `renewal_option` needs a negation check before a positive check: `"Tenant has no option ... to renew or extend"` contains the word "option" and the word "renew," but it means the opposite of `"Tenant shall have ... an option to renew."` Look for explicit negation language first.
- `assignment_sublease` has three outcomes, not two — don't collapse "requires consent" into either "allowed" or "not allowed." A sentence that says a tenant *may* assign *without* consent is different from one that says a tenant needs the landlord's *consent* to assign, which is different again from an outright prohibition.
- Four fixtures are provided under `fixtures/leases/`: three fully-specified leases with deliberately different phrasing, section order, and structure (so nothing about your solution can rely on the fields always showing up in the same position), and one, `lease_incomplete.txt`, that's missing its default/cure-period language entirely — this is the one that should raise `LeaseExtractionError` instead of crashing or inventing a value.
