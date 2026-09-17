# Contributing

This repo is maintained by [LegalEngineers.ai](https://legalengineers.ai) as a public training ground for legal engineering.

## Reporting issues

If a challenge's tests are ambiguous, unsolvable as specified, or you think a fixture is unrealistic, open an issue. Include the challenge number and what you expected vs. what happened.

## Proposing a new challenge

Open an issue first describing the workflow it targets and the firm problem it solves (non-billable leak, verification bottleneck, or governance/infrastructure lock-in — see the README). We want challenges that map to real work, not puzzles for their own sake.

A new challenge PR should include:

- `README.md` — the problem statement and what "done" means
- `fixtures/` — realistic, synthetic sample data (no real client or matter data, ever)
- `challenge/` — a starter stub with TODOs, not a solved implementation
- `tests/` — a pytest suite that fails against the stub and passes against a correct solution

## Pull requests

Keep PRs scoped to one challenge or one fix. Run `pytest` before opening.

## Contact

hello@legalengineers.ai
