"""Human-friendly rendering of a protein, as terminal text or as HTML."""

from __future__ import annotations

import datetime as _dt
import html
import shutil
import textwrap
from typing import Any

from .dataset import Protein


def _wrap(text: str, width: int, indent: str = "") -> str:
    wrapped = textwrap.fill(
        text,
        width=max(width, 20),
        initial_indent=indent,
        subsequent_indent=indent,
    )
    return wrapped


def render_text(
    protein: Protein,
    *,
    day: _dt.date | None = None,
    width: int | None = None,
    color: bool = False,
    live: dict[str, Any] | None = None,
) -> str:
    """Render a protein as a plain-text block suitable for a terminal.

    Args:
        protein: the protein to describe.
        day: the date it is the protein of (defaults to today).
        width: wrap width; defaults to the current terminal width (capped).
        color: emit ANSI colour codes if True.
        live: optional live metadata from :mod:`protein_of_the_day.rcsb`.
    """
    if width is None:
        width = min(shutil.get_terminal_size((80, 24)).columns, 88)
    day = day or _dt.date.today()

    def paint(code: str, text: str) -> str:
        return f"\033[{code}m{text}\033[0m" if color else text

    bar = "─" * min(width, 60)
    lines: list[str] = []
    lines.append(paint("2", f"Protein of the Day · {day.isoformat()}"))
    lines.append(paint("1;36", protein.name))
    lines.append(paint("3", f"“{protein.tagline}”"))
    lines.append(bar)
    lines.append(f"{paint('1', 'Category')}   {protein.category}")
    lines.append(f"{paint('1', 'Organism')}   {protein.organism}")
    lines.append(f"{paint('1', 'PDB entry')}  {protein.pdb_id}  ({protein.rcsb_url})")

    if live:
        if live.get("title"):
            lines.append(f"{paint('1', 'Title')}      {live['title']}")
        method = live.get("method")
        resolution = live.get("resolution")
        if method or resolution:
            detail = method or ""
            if resolution:
                detail = f"{detail}, {resolution} Å".strip(", ")
            lines.append(f"{paint('1', 'Structure')}  {detail}")
        if live.get("released"):
            lines.append(f"{paint('1', 'Released')}   {live['released']}")

    lines.append("")
    lines.append(_wrap(protein.description, width))
    lines.append("")
    lines.append(_wrap(f"Did you know? {protein.fun_fact}", width))
    return "\n".join(lines)


def render_html_card(
    protein: Protein,
    *,
    day: _dt.date | None = None,
    live: dict[str, Any] | None = None,
) -> str:
    """Render a self-contained HTML fragment describing the protein."""
    day = day or _dt.date.today()
    e = html.escape

    live_rows = ""
    if live:
        pairs: list[tuple[str, str]] = []
        if live.get("title"):
            pairs.append(("Title", str(live["title"])))
        if live.get("method"):
            pairs.append(("Method", str(live["method"])))
        if live.get("resolution"):
            pairs.append(("Resolution", f"{live['resolution']} Å"))
        if live.get("released"):
            pairs.append(("Released", str(live["released"])))
        live_rows = "".join(
            f'<div class="pod-meta-row"><dt>{e(k)}</dt><dd>{e(v)}</dd></div>'
            for k, v in pairs
        )

    return f"""<article class="pod-card">
  <p class="pod-date">Protein of the Day · {e(day.isoformat())}</p>
  <h1 class="pod-name">{e(protein.name)}</h1>
  <p class="pod-tagline">{e(protein.tagline)}</p>
  <img class="pod-image" src="{e(protein.image_url)}" alt="Structure of {e(protein.name)} (PDB {e(protein.pdb_id)})" loading="lazy">
  <dl class="pod-meta">
    <div class="pod-meta-row"><dt>Category</dt><dd>{e(protein.category)}</dd></div>
    <div class="pod-meta-row"><dt>Organism</dt><dd>{e(protein.organism)}</dd></div>
    <div class="pod-meta-row"><dt>PDB entry</dt><dd><a href="{e(protein.rcsb_url)}">{e(protein.pdb_id)}</a></dd></div>
    {live_rows}
  </dl>
  <p class="pod-description">{e(protein.description)}</p>
  <p class="pod-fun-fact"><strong>Did you know?</strong> {e(protein.fun_fact)}</p>
  <p class="pod-links">
    <a href="{e(protein.rcsb_url)}">View on RCSB PDB</a> ·
    <a href="{e(protein.rcsb_3d_url)}">Explore in 3-D</a>
  </p>
</article>"""
