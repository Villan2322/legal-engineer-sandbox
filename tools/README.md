# Fake data generator

Every challenge ships with a small, fixed set of hand-authored fixtures — enough to make the tests meaningful, not enough to really stress a solution. This generator spawns as much additional synthetic data as you want, in the same shape the real fixtures use, so you can practice or load-test past what the repo hands you.

Nothing here touches your challenge attempt. It just writes files wherever you point it.

## Setup

Same environment as the rest of the repo:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python tools/generate_fake_data.py <dataset> [options]
```

| Dataset | What it produces | Maps to |
|---|---|---|
| `matters` | `matters.json` — synthetic client/adverse-party records | Challenge 01 |
| `webhooks` | intake webhooks, a configurable fraction deliberately conflicting | Challenge 01 |
| `activity` | raw calendar/email activity entries | Challenge 02 |
| `nda` | synthetic NDA `.txt` files + a manifest of expected playbook violations | Challenge 03 |
| `lease` | synthetic lease `.txt` files + a manifest of expected extracted terms | Challenge 04 |
| `privilege` | synthetic privileged memos + a manifest of known entities and embedded PII | Challenge 05 |
| `all` | one of everything, in a single output directory | all five |

Every dataset takes `--seed` — the same seed always produces the same output, so you can share a seed instead of a file when reporting a bug against generated data.

### Examples

```bash
# 50 matters, then 80 webhooks against them (~35% built to conflict on purpose)
python tools/generate_fake_data.py matters --count 50 --seed 1 --out /tmp/matters.json
python tools/generate_fake_data.py webhooks --count 80 --seed 1 \
  --matters-file /tmp/matters.json --out /tmp/webhooks.json

# 200 activity entries, reconciled against the real Challenge 02 fixtures by default
python tools/generate_fake_data.py activity --count 200 --seed 1 --out /tmp/activity.json

# 25 synthetic NDAs, each with its expected playbook violations recorded in manifest.json
python tools/generate_fake_data.py nda --count 25 --seed 1 --out-dir /tmp/ndas/

# One bundle of everything
python tools/generate_fake_data.py all --count 25 --seed 1 --out-dir /tmp/fake_dataset/
```

## Why the manifests matter

`nda`, `lease`, and `privilege` don't just produce more reading material — each document comes with a `manifest.json` recording the ground truth the generator built in on purpose (which playbook rules a given NDA should trip, what a lease's terms should extract to, which entities and PII a memo contains). That means generated data doubles as more test cases: run your own solution against a manifest entry and check the output matches, without touching the graded test suite.

`matters` + `webhooks` don't ship a manifest — the "ground truth" for those is just running your own `find_conflicts` against the generated files and inspecting the result, the same as you would with the real fixtures.

## Extending it

The generators live in `tools/fake_data/` — one module per challenge (`matters.py`, `activity.py`, `nda.py`, `lease.py`, `privilege.py`), plus `common.py` for shared name/company/PII generation. Each one is a plain function that takes a `FakeDataContext` (a seeded `Faker` + `random.Random` pair) and returns plain dicts — nothing here imports from any challenge's solution or stub, so it can't leak answers.
