"""Optional live enrichment from the RCSB Protein Data Bank.

This module is entirely optional. The core package works offline using the
bundled catalogue; :func:`fetch_entry_metadata` reaches out to the public
RCSB REST API only when the caller explicitly asks for it (for example via the
``--live`` flag of the command-line tool). Any network or parsing problem is
swallowed and reported as ``None`` so that a missing connection never breaks
the tool.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

RCSB_ENTRY_API = "https://data.rcsb.org/rest/v1/core/entry/{pdb_id}"


def fetch_entry_metadata(pdb_id: str, *, timeout: float = 6.0) -> dict[str, Any] | None:
    """Fetch a handful of summary fields for a PDB entry.

    Returns a dict with any of ``title``, ``method``, ``resolution`` and
    ``released`` that could be determined, or ``None`` if the entry could not
    be retrieved (offline, blocked, not found, or unexpected payload).
    """
    url = RCSB_ENTRY_API.format(pdb_id=pdb_id.upper())
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        return None
    return _parse_entry(payload)


def _parse_entry(payload: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None

    result: dict[str, Any] = {}

    struct = payload.get("struct")
    if isinstance(struct, dict) and struct.get("title"):
        result["title"] = str(struct["title"]).strip()

    methods = payload.get("exptl")
    if isinstance(methods, list) and methods:
        names = [m.get("method") for m in methods if isinstance(m, dict) and m.get("method")]
        if names:
            result["method"] = ", ".join(str(n).title() for n in names)

    entry_info = payload.get("rcsb_entry_info")
    if isinstance(entry_info, dict):
        resolution = entry_info.get("resolution_combined")
        if isinstance(resolution, list) and resolution:
            try:
                result["resolution"] = round(float(resolution[0]), 2)
            except (TypeError, ValueError):
                pass

    accession = payload.get("rcsb_accession_info")
    if isinstance(accession, dict) and accession.get("initial_release_date"):
        # Keep just the calendar date portion of the ISO timestamp.
        result["released"] = str(accession["initial_release_date"])[:10]

    return result or None
