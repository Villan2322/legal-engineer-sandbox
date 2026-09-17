"""
Root conftest — makes every challenge's starter package importable
regardless of which directory pytest treats as the import root for a given
test file.

Each challenge's `tests/` directory intentionally has no `__init__.py` (so
`tests/test_*.py` files don't collide with each other's bare `tests` module
name when the whole repo's suite runs in one session). That means pytest
won't automatically add the challenge's own directory to `sys.path` the way
it would for a package-style test layout — so we do it explicitly here,
once, for every challenge.
"""

import sys
from pathlib import Path

_CHALLENGES_DIR = Path(__file__).parent / "challenges"

if _CHALLENGES_DIR.is_dir():
    for _entry in sorted(_CHALLENGES_DIR.iterdir()):
        if _entry.is_dir():
            sys.path.insert(0, str(_entry))
