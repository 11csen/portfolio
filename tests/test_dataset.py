"""Tests for loading and validating the protein catalogue."""

import re

import pytest

from protein_of_the_day.dataset import Protein, get_by_slug, load_proteins

PDB_ID_RE = re.compile(r"^[0-9][A-Za-z0-9]{3}$")


def test_catalogue_is_non_empty():
    proteins = load_proteins()
    assert len(proteins) >= 20


def test_catalogue_is_cached_and_immutable():
    first = load_proteins()
    second = load_proteins()
    assert first is second  # lru_cache returns the identical tuple
    assert isinstance(first, tuple)


def test_every_entry_has_required_fields():
    for protein in load_proteins():
        assert protein.slug
        assert protein.name
        assert protein.category
        assert protein.organism
        assert protein.tagline
        assert len(protein.description) > 40
        assert protein.fun_fact


def test_pdb_ids_are_well_formed():
    for protein in load_proteins():
        assert PDB_ID_RE.match(protein.pdb_id), f"bad PDB id: {protein.pdb_id!r}"


def test_slugs_are_url_safe_and_unique():
    slugs = [p.slug for p in load_proteins()]
    assert len(slugs) == len(set(slugs))
    for slug in slugs:
        assert re.match(r"^[a-z0-9-]+$", slug), f"bad slug: {slug!r}"


def test_pdb_ids_are_unique():
    ids = [p.pdb_id.upper() for p in load_proteins()]
    assert len(ids) == len(set(ids))


def test_derived_links_use_pdb_id():
    protein = load_proteins()[0]
    assert protein.pdb_id in protein.rcsb_url
    assert protein.pdb_id in protein.rcsb_3d_url
    assert protein.pdb_id.lower() in protein.image_url
    assert protein.rcsb_url.startswith("https://")


def test_to_dict_round_trip():
    protein = load_proteins()[0]
    data = protein.to_dict()
    assert data["slug"] == protein.slug
    assert data["rcsb_url"] == protein.rcsb_url
    assert "image_url" in data


def test_get_by_slug_is_case_insensitive():
    protein = load_proteins()[0]
    assert get_by_slug(protein.slug.upper()) is protein
    assert get_by_slug(f"  {protein.slug}  ") is protein


def test_get_by_slug_unknown_raises():
    with pytest.raises(KeyError):
        get_by_slug("does-not-exist")


def test_from_dict_missing_field_raises():
    with pytest.raises(ValueError, match="missing required field"):
        Protein.from_dict({"slug": "x", "name": "X"})
