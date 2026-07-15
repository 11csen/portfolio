#!/usr/bin/env python3
"""Generate the data file used by the static web app in ``docs/``.

The canonical catalogue lives inside the Python package
(``src/protein_of_the_day/data/proteins.json``). To avoid two copies drifting
apart, the web app does not ship its own hand-maintained list; instead this
script projects the canonical data into ``docs/proteins.json``.

Run it whenever the catalogue changes::

    python scripts/build_site.py

The test-suite asserts that ``docs/proteins.json`` matches the output of this
script, so CI will fail if someone edits the catalogue without regenerating.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "src"
OUTPUT = REPO_ROOT / "docs" / "proteins.json"

# Fields the web app consumes. Links are derived client-side from ``pdb_id``.
DISPLAY_FIELDS = (
    "slug",
    "name",
    "pdb_id",
    "category",
    "organism",
    "tagline",
    "description",
    "fun_fact",
)


def build_payload() -> dict[str, object]:
    sys.path.insert(0, str(SRC))
    from protein_of_the_day.dataset import load_proteins

    proteins = [
        {field: getattr(p, field) for field in DISPLAY_FIELDS}
        for p in load_proteins()
    ]
    return {
        "version": 1,
        "generated_by": "scripts/build_site.py",
        "count": len(proteins),
        "proteins": proteins,
    }


def render(payload: dict[str, object]) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    payload = build_payload()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render(payload), encoding="utf-8")
    print(f"Wrote {payload['count']} proteins to {OUTPUT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
