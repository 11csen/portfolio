"""Loading and modelling the curated protein catalogue."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from importlib import resources
from typing import Any

#: URL templates for building links to external resources from a PDB id.
RCSB_STRUCTURE_URL = "https://www.rcsb.org/structure/{pdb_id}"
RCSB_3D_VIEW_URL = "https://www.rcsb.org/3d-view/{pdb_id}"
#: Structure summary image served by the RCSB content-delivery network.
RCSB_IMAGE_URL = (
    "https://cdn.rcsb.org/images/structures/{pdb_id_lower}_assembly-1.jpeg"
)

_REQUIRED_FIELDS = (
    "slug",
    "name",
    "pdb_id",
    "category",
    "organism",
    "tagline",
    "description",
    "fun_fact",
)


@dataclass(frozen=True)
class Protein:
    """A single entry in the protein catalogue.

    Attributes mirror the fields stored in ``proteins.json``. The link and
    image helpers are derived purely from :attr:`pdb_id`, so they are valid
    for any real Protein Data Bank identifier.
    """

    slug: str
    name: str
    pdb_id: str
    category: str
    organism: str
    tagline: str
    description: str
    fun_fact: str

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Protein":
        missing = [field for field in _REQUIRED_FIELDS if not raw.get(field)]
        if missing:
            name = raw.get("name") or raw.get("slug") or "<unknown>"
            raise ValueError(
                f"Protein entry {name!r} is missing required field(s): "
                + ", ".join(missing)
            )
        return cls(**{field: str(raw[field]) for field in _REQUIRED_FIELDS})

    @property
    def rcsb_url(self) -> str:
        """Link to the structure's page on RCSB.org."""
        return RCSB_STRUCTURE_URL.format(pdb_id=self.pdb_id)

    @property
    def rcsb_3d_url(self) -> str:
        """Link to an interactive 3-D view of the structure."""
        return RCSB_3D_VIEW_URL.format(pdb_id=self.pdb_id)

    @property
    def image_url(self) -> str:
        """URL of a rendered image of the structure (may 404 for a few entries)."""
        return RCSB_IMAGE_URL.format(pdb_id_lower=self.pdb_id.lower())

    def to_dict(self) -> dict[str, str]:
        """Return a plain-dict view including the derived link fields."""
        data = {field: getattr(self, field) for field in _REQUIRED_FIELDS}
        data["rcsb_url"] = self.rcsb_url
        data["rcsb_3d_url"] = self.rcsb_3d_url
        data["image_url"] = self.image_url
        return data


def _read_raw_dataset() -> dict[str, Any]:
    """Read and parse the bundled ``proteins.json`` resource.

    The file is resolved relative to the ``protein_of_the_day`` package (which
    has an ``__init__``) rather than the ``data`` directory. On Python 3.9,
    ``importlib.resources.files`` raises ``TypeError`` for a directory without
    an ``__init__`` because it is treated as a namespace package with no
    ``__spec__.origin``; going through the real package and chaining single-arg
    ``joinpath`` calls avoids that and works on 3.9 through 3.12.
    """
    resource = (
        resources.files("protein_of_the_day").joinpath("data").joinpath("proteins.json")
    )
    with resource.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@lru_cache(maxsize=1)
def load_proteins() -> tuple[Protein, ...]:
    """Load the curated catalogue, validated and de-duplicated.

    The result is cached and returned as an immutable tuple so callers can
    rely on a stable ordering (the "protein of the day" rotation depends on
    it).

    Raises:
        ValueError: if the dataset is empty, an entry is malformed, or a
            ``slug``/``pdb_id`` is duplicated.
    """
    raw = _read_raw_dataset()
    entries = raw.get("proteins")
    if not isinstance(entries, list) or not entries:
        raise ValueError("proteins.json does not contain a non-empty 'proteins' list")

    proteins = tuple(Protein.from_dict(entry) for entry in entries)

    seen_slugs: set[str] = set()
    seen_pdb: set[str] = set()
    for protein in proteins:
        if protein.slug in seen_slugs:
            raise ValueError(f"Duplicate slug in catalogue: {protein.slug!r}")
        if protein.pdb_id.upper() in seen_pdb:
            raise ValueError(f"Duplicate PDB id in catalogue: {protein.pdb_id!r}")
        seen_slugs.add(protein.slug)
        seen_pdb.add(protein.pdb_id.upper())

    return proteins


def get_by_slug(slug: str) -> Protein:
    """Return the protein with the given slug (case-insensitive).

    Raises:
        KeyError: if no protein matches.
    """
    target = slug.strip().lower()
    for protein in load_proteins():
        if protein.slug.lower() == target:
            return protein
    raise KeyError(slug)
