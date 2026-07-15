"""Tests for the text and HTML renderers."""

import datetime as dt

from protein_of_the_day.dataset import load_proteins
from protein_of_the_day.render import render_html_card, render_text

PROTEIN = load_proteins()[0]
DAY = dt.date(2025, 5, 20)


def test_render_text_contains_key_fields():
    out = render_text(PROTEIN, day=DAY, color=False, width=80)
    # Text is line-wrapped, so normalise whitespace before substring checks.
    flat = " ".join(out.split())
    assert PROTEIN.name in flat
    assert PROTEIN.pdb_id in flat
    assert PROTEIN.category in flat
    assert "2025-05-20" in flat
    assert PROTEIN.fun_fact in flat
    assert PROTEIN.description in flat


def test_render_text_no_ansi_when_color_false():
    out = render_text(PROTEIN, day=DAY, color=False)
    assert "\033[" not in out


def test_render_text_has_ansi_when_color_true():
    out = render_text(PROTEIN, day=DAY, color=True)
    assert "\033[" in out


def test_render_text_includes_live_metadata():
    live = {"title": "MYOGLOBIN", "method": "X-Ray Diffraction", "resolution": 2.0}
    out = render_text(PROTEIN, day=DAY, color=False, live=live)
    assert "X-Ray Diffraction" in out
    assert "2.0" in out


def test_render_html_card_is_escaped_and_complete():
    out = render_html_card(PROTEIN, day=DAY)
    assert "<article" in out
    assert PROTEIN.name in out
    assert PROTEIN.rcsb_url in out
    assert PROTEIN.image_url in out
    assert "2025-05-20" in out


def test_render_html_escapes_special_characters():
    from protein_of_the_day.dataset import Protein

    nasty = Protein(
        slug="x",
        name="Prot<script>",
        pdb_id="1ABC",
        category="Cat & Co",
        organism="Org",
        tagline="Tag \"quote\"",
        description="Desc",
        fun_fact="Fact",
    )
    out = render_html_card(nasty, day=DAY)
    assert "<script>" not in out
    assert "&lt;script&gt;" in out
    assert "Cat &amp; Co" in out


def test_render_html_includes_live_rows():
    live = {"method": "Electron Microscopy", "resolution": 3.1, "released": "2020-01-01"}
    out = render_html_card(PROTEIN, day=DAY, live=live)
    assert "Electron Microscopy" in out
    assert "3.1" in out
    assert "2020-01-01" in out
