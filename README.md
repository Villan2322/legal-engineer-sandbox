# Legal Engineer Sandbox

A training ground for legal engineering, built like Hack The Box or Exercism: fork the repo, clone it down, pick a challenge, and make the tests pass. They fail until your logic is actually correct.

Maintained by [LegalEngineers.ai](https://legalengineers.ai) — the deployment layer for firm-owned legal AI.

## Why this exists

Law firms are getting hit by three problems at once:

1. **The non-billable leak** — intake, conflict checks, and billing categorization eat 20-30% of associate and paralegal hours.
2. **The verification bottleneck** — partners don't trust raw AI output on billable work. They want the machine drafting against a firm-approved playbook, deviations flagged, attorney in the reviewer seat.
3. **Data governance lock-in** — firms are scared of leaking privilege through generic web apps, and their prompt engineering vanishes when a SaaS contract ends.

Nobody is training the people who are supposed to solve this. This repo is a starting point.

## How it works

Each challenge under `challenges/` is self-contained:

```
challenges/01-intake-conflict-detection/
├── README.md            # the problem, the spec, what "done" means
├── fixtures/            # sample data — matters, parties, webhook payloads
├── intake_conflict/     # starter code with TODOs — this is what you edit
└── tests/               # pytest suite — fails until your implementation is correct
```

Each challenge's starter package is named for its topic (`intake_conflict/`, `ledes_reconciliation/`, and so on) rather than a generic name, so the whole suite can run in one `pytest` invocation without import collisions.

Pick a challenge, read its README, implement the logic in the challenge's package directory, and run its tests. Nothing else in the repo needs to change.

## Setup

Requires Python 3.11+.

```bash
git clone https://github.com/legalengineers-ai/legal-engineer-sandbox.git
cd legal-engineer-sandbox
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Run a single challenge's tests:

```bash
pytest challenges/01-intake-conflict-detection -v
```

Run everything:

```bash
pytest
```

Green tests mean you're done with that challenge.

## Challenges

| # | Challenge | Track | What you build |
|---|-----------|-------|-----------------|
| 01 | [Intake Conflict Detection](challenges/01-intake-conflict-detection) | Back office & ops | Fuzzy-match and entity-resolve incoming intake webhooks against active matters, subsidiaries, and adverse parties. |
| 02 | [Unbilled Activity & LEDES Reconciliation](challenges/02-unbilled-activity-ledes-reconciliation) | Back office & ops | Classify unassigned calendar blocks and emails to matter dockets and emit clean LEDES/UTBMS billing codes. |
| 03 | [Playbook-Driven NDA Redlining](challenges/03-playbook-nda-redlining) | Assisted billable | Redline inbound NDAs against a firm playbook, flagging out-of-bounds terms with bracketed negotiation notes while leaving compliant terms untouched. |
| 04 | [Commercial Lease Term Extraction](challenges/04-lease-term-extraction) | Assisted billable | Pull key lease covenants out of messy text into a validated schema for diligence prep. |
| 05 | [Privilege Scrubber & PII Guardrails](challenges/05-privilege-scrubber-pii-guardrails) | Governance & infrastructure | Redact privilege markers and sensitive entities before a query leaves the firm's perimeter, with local, reversible de-anonymization. |

Start with 01 — it doesn't touch billable work product, so there's no reason not to.

## Need more data to practice on?

Every challenge ships with a small set of fixed fixtures — enough to make the tests meaningful, not enough to really stress a solution. `tools/generate_fake_data.py` spawns as much additional synthetic data as you want, in the same shape, with a seed for reproducibility:

```bash
python tools/generate_fake_data.py all --count 25 --seed 1 --out-dir /tmp/fake_dataset/
```

See [tools/README.md](tools/README.md) for the full generator reference.

## Proof of work

Passing tests are the point. Fork this repo, solve a challenge, and the green checkmarks on your fork are real evidence you can do the work — link it on your resume or LinkedIn.

## Contributing

New challenges, better fixtures, and bug reports are welcome — open an issue or a PR. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Code in this repository is [MIT licensed](LICENSE). Copyright LegalEngineers.ai.
