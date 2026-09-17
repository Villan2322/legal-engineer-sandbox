#!/usr/bin/env python
"""
Spawn a synthetic dataset to build or test against — for practicing beyond
the fixed challenge fixtures, or for stress-testing your own solution at a
size the hand-authored fixtures don't reach.

Examples
--------
Generate 50 matters and 80 intake webhooks (~35% deliberately conflicting):

    python tools/generate_fake_data.py matters --count 50 --seed 1 --out /tmp/matters.json
    python tools/generate_fake_data.py webhooks --count 80 --seed 1 \\
        --matters-file /tmp/matters.json --out /tmp/webhooks.json

Generate 200 activity entries against the real Challenge 02 fixtures:

    python tools/generate_fake_data.py activity --count 200 --seed 1 --out /tmp/activity.json

Generate 25 synthetic NDAs with their expected playbook violations:

    python tools/generate_fake_data.py nda --count 25 --seed 1 --out-dir /tmp/ndas/

Generate 25 synthetic leases with their expected extracted terms:

    python tools/generate_fake_data.py lease --count 25 --seed 1 --out-dir /tmp/leases/

Generate 25 synthetic privileged memos with known entities and PII:

    python tools/generate_fake_data.py privilege --count 25 --seed 1 --out-dir /tmp/memos/

Or spawn one of everything into a single directory in one shot:

    python tools/generate_fake_data.py all --count 25 --seed 1 --out-dir /tmp/fake_dataset/

Every command takes --seed for reproducibility — the same seed always
produces the same dataset.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.fake_data.activity import generate_activity_entries
from tools.fake_data.common import FakeDataContext
from tools.fake_data.lease import generate_lease
from tools.fake_data.matters import generate_matters, generate_webhooks
from tools.fake_data.nda import generate_nda
from tools.fake_data.privilege import generate_privileged_doc

DEFAULT_MATTERS_FILE = REPO_ROOT / "challenges/01-intake-conflict-detection/fixtures/matters.json"
DEFAULT_CODE_RULES_FILE = REPO_ROOT / "challenges/02-unbilled-activity-ledes-reconciliation/fixtures/code_rules.json"


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")
    print(f"wrote {path}")


def _load_json(path: Path):
    return json.loads(path.read_text())


def cmd_matters(args) -> None:
    ctx = FakeDataContext(seed=args.seed)
    matters = generate_matters(args.count, ctx)
    _write_json(Path(args.out), matters)


def cmd_webhooks(args) -> None:
    ctx = FakeDataContext(seed=args.seed)
    matters_file = Path(args.matters_file) if args.matters_file else DEFAULT_MATTERS_FILE
    matters = _load_json(matters_file)
    webhooks = generate_webhooks(args.count, matters, ctx, conflict_rate=args.conflict_rate)
    _write_json(Path(args.out), webhooks)


def cmd_activity(args) -> None:
    ctx = FakeDataContext(seed=args.seed)
    matters_file = Path(args.matters_file) if args.matters_file else DEFAULT_MATTERS_FILE
    code_rules_file = Path(args.code_rules_file) if args.code_rules_file else DEFAULT_CODE_RULES_FILE
    matters = _load_json(matters_file)
    code_rules = _load_json(code_rules_file)
    entries = generate_activity_entries(args.count, matters, code_rules, ctx, unresolved_rate=args.unresolved_rate)
    _write_json(Path(args.out), entries)


def _spawn_text_dataset(kind: str, count: int, seed: int, out_dir: Path) -> None:
    ctx = FakeDataContext(seed=seed)
    generator = {"nda": generate_nda, "lease": generate_lease}[kind]
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for i in range(count):
        result = generator(ctx)
        filename = f"{kind}_{i:03d}.txt"
        (out_dir / filename).write_text(result["text"])
        entry = {"file": filename}
        entry.update({k: v for k, v in result.items() if k != "text"})
        manifest.append(entry)
    _write_json(out_dir / "manifest.json", manifest)
    print(f"wrote {count} {kind} documents to {out_dir}")


def cmd_nda(args) -> None:
    _spawn_text_dataset("nda", args.count, args.seed, Path(args.out_dir))


def cmd_lease(args) -> None:
    _spawn_text_dataset("lease", args.count, args.seed, Path(args.out_dir))


def cmd_privilege(args) -> None:
    ctx = FakeDataContext(seed=args.seed)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for i in range(args.count):
        result = generate_privileged_doc(ctx)
        filename = f"privilege_{i:03d}.txt"
        (out_dir / filename).write_text(result["text"])
        manifest.append(
            {
                "file": filename,
                "known_entities": result["known_entities"],
                "pii": result["pii"],
            }
        )
    _write_json(out_dir / "manifest.json", manifest)
    print(f"wrote {args.count} privilege documents to {out_dir}")


def cmd_all(args) -> None:
    out_dir = Path(args.out_dir)
    ctx = FakeDataContext(seed=args.seed)

    matters = generate_matters(args.count, ctx)
    _write_json(out_dir / "matters.json", matters)

    webhooks = generate_webhooks(args.count, matters, ctx)
    _write_json(out_dir / "webhooks.json", webhooks)

    code_rules_file = Path(args.code_rules_file) if args.code_rules_file else DEFAULT_CODE_RULES_FILE
    if code_rules_file.exists():
        code_rules = _load_json(code_rules_file)
        activity = generate_activity_entries(args.count, matters, code_rules, ctx)
        _write_json(out_dir / "activity.json", activity)
    else:
        print(f"skipping activity.json — code rules file not found at {code_rules_file}")

    _spawn_text_dataset("nda", args.count, args.seed, out_dir / "ndas")
    _spawn_text_dataset("lease", args.count, args.seed, out_dir / "leases")

    manifest = []
    for i in range(args.count):
        result = generate_privileged_doc(ctx)
        filename = f"privilege_{i:03d}.txt"
        (out_dir / "privilege").mkdir(parents=True, exist_ok=True)
        (out_dir / "privilege" / filename).write_text(result["text"])
        manifest.append({"file": filename, "known_entities": result["known_entities"], "pii": result["pii"]})
    _write_json(out_dir / "privilege" / "manifest.json", manifest)

    print(f"\nspawned a full fake dataset ({args.count} of each) into {out_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="dataset", required=True)
    seed_parent = argparse.ArgumentParser(add_help=False)
    seed_parent.add_argument("--seed", type=int, default=None, help="seed for reproducible output")

    p = sub.add_parser("matters", parents=[seed_parent], help="Challenge 01 matters.json")
    p.add_argument("--count", type=int, default=20)
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_matters)

    p = sub.add_parser("webhooks", parents=[seed_parent], help="Challenge 01 incoming intake webhooks")
    p.add_argument("--count", type=int, default=30)
    p.add_argument("--matters-file", default=None, help=f"default: {DEFAULT_MATTERS_FILE}")
    p.add_argument("--conflict-rate", type=float, default=0.35)
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_webhooks)

    p = sub.add_parser("activity", parents=[seed_parent], help="Challenge 02 raw activity entries")
    p.add_argument("--count", type=int, default=50)
    p.add_argument("--matters-file", default=None, help=f"default: {DEFAULT_MATTERS_FILE}")
    p.add_argument("--code-rules-file", default=None, help=f"default: {DEFAULT_CODE_RULES_FILE}")
    p.add_argument("--unresolved-rate", type=float, default=0.15)
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_activity)

    p = sub.add_parser("nda", parents=[seed_parent], help="Challenge 03 synthetic NDAs + expected playbook violations")
    p.add_argument("--count", type=int, default=20)
    p.add_argument("--out-dir", required=True)
    p.set_defaults(func=cmd_nda)

    p = sub.add_parser("lease", parents=[seed_parent], help="Challenge 04 synthetic leases + expected extracted terms")
    p.add_argument("--count", type=int, default=20)
    p.add_argument("--out-dir", required=True)
    p.set_defaults(func=cmd_lease)

    p = sub.add_parser("privilege", parents=[seed_parent], help="Challenge 05 synthetic privileged memos + known entities/PII")
    p.add_argument("--count", type=int, default=20)
    p.add_argument("--out-dir", required=True)
    p.set_defaults(func=cmd_privilege)

    p = sub.add_parser("all", parents=[seed_parent], help="Spawn one bundle of everything into --out-dir")
    p.add_argument("--count", type=int, default=15, help="count per dataset")
    p.add_argument("--code-rules-file", default=None, help=f"default: {DEFAULT_CODE_RULES_FILE}")
    p.add_argument("--out-dir", required=True)
    p.set_defaults(func=cmd_all)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
