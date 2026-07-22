"""Ensure the generated web data matches the canonical catalogue."""

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DATA = REPO_ROOT / "docs" / "catalogue" / "proteins.json"


def _load_build_module():
    import importlib.util

    script = REPO_ROOT / "scripts" / "build_site.py"
    spec = importlib.util.spec_from_file_location("build_site", script)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_docs_data_exists():
    assert DOCS_DATA.exists(), "run: python scripts/build_site.py"


def test_docs_data_matches_build_output():
    build = _load_build_module()
    expected = build.render(build.build_payload())
    actual = DOCS_DATA.read_text(encoding="utf-8")
    assert actual == expected, (
        "docs/proteins.json is stale — regenerate with: python scripts/build_site.py"
    )


def test_docs_data_is_valid_and_complete():
    payload = json.loads(DOCS_DATA.read_text(encoding="utf-8"))
    from protein_of_the_day.dataset import load_proteins

    assert payload["count"] == len(load_proteins())
    slugs = {p["slug"] for p in payload["proteins"]}
    assert slugs == {p.slug for p in load_proteins()}


@pytest.mark.parametrize("field", ["slug", "name", "pdb_id", "tagline", "description", "fun_fact"])
def test_docs_entries_have_display_fields(field):
    payload = json.loads(DOCS_DATA.read_text(encoding="utf-8"))
    for entry in payload["proteins"]:
        assert entry.get(field)
