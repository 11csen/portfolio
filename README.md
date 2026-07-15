# 🧬 Protein of the Day

A famous protein for every calendar day — the **same one for everyone, everywhere**, chosen
deterministically from the date. Comes as a tiny zero-dependency Python library and CLI, plus a
static web app you can host on GitHub Pages.

Structures and images are drawn from the [RCSB Protein Data Bank](https://www.rcsb.org).

---

## What it does

- Picks one protein per day from a curated catalogue of 32 landmark proteins (myoglobin,
  hemoglobin, GFP, CRISPR-era favourites, the SARS-CoV-2 spike, and more).
- The choice is **deterministic**: the date maps to a protein with simple, portable arithmetic, so
  the CLI and the website always agree, and the whole catalogue rotates before any protein repeats.
- Works **fully offline** using bundled data. Optionally enriches output with live metadata
  (experimental method, resolution, release date) from the RCSB PDB when a network is available.

## The selection algorithm

```
epoch_day = whole days between 1970-01-01 and the target calendar date
index     = epoch_day mod (number of proteins)
```

Because the index advances by exactly one each day, every protein appears once before the cycle
repeats. The same formula is implemented in Python (`src/protein_of_the_day/selector.py`) and in
JavaScript (`docs/app.js`); they are verified to agree day-for-day.

## Command-line tool

Install (editable, from a clone):

```bash
pip install -e .
```

Use it:

```bash
protein-of-the-day                     # today's protein
protein-of-the-day --date 2026-12-25   # a specific day
protein-of-the-day --slug gfp          # look one up by slug
protein-of-the-day --list              # show the whole catalogue
protein-of-the-day --format json       # machine-readable output
protein-of-the-day --format html       # an HTML card fragment
protein-of-the-day --live              # add live details from the RCSB PDB
```

Example:

```text
Protein of the Day · 2026-07-15
p53 Tumour Suppressor
“The 'guardian of the genome'.”
────────────────────────────────────────────────────────────
Category   Tumour suppressor
Organism   Human
PDB entry  1TUP  (https://www.rcsb.org/structure/1TUP)

p53 senses DNA damage and can halt cell division or trigger cell death...

Did you know? Elephants carry around twenty copies of the p53 gene...
```

## Library

```python
from protein_of_the_day import protein_of_the_day, protein_for_date
import datetime as dt

today = protein_of_the_day()
print(today.name, today.pdb_id, today.rcsb_url)

xmas = protein_for_date(dt.date(2026, 12, 25))
print(xmas.name)
```

## Web app

The `docs/` folder is a self-contained static site. It loads the catalogue, works out the day's
protein in the browser (no build step, no server), lets you page through dates, and pulls the
structure image and a couple of live facts from the RCSB PDB.

Try it locally:

```bash
python -m http.server --directory docs 8000
# then open http://localhost:8000
```

### Publishing on GitHub Pages

Two options:

1. **From Actions (recommended):** in *Settings → Pages*, set the source to **GitHub Actions**.
   The included [`pages.yml`](.github/workflows/pages.yml) workflow then deploys `docs/` on every
   push to `main`.
2. **From a branch:** in *Settings → Pages*, choose your default branch and the `/docs` folder.

The page rotates the protein on its own each day, client-side, so there's nothing to rebuild daily.

## The data

The single source of truth is [`src/protein_of_the_day/data/proteins.json`](src/protein_of_the_day/data/proteins.json).
Each entry references a representative structure in the PDB by its 4-character ID and keeps to
well-established, textbook-stable facts. To add or edit a protein, change that file and regenerate
the web app's copy:

```bash
python scripts/build_site.py
```

The test suite fails if `docs/proteins.json` drifts out of sync, so this step is enforced in CI.

## Development

```bash
pip install -e ".[dev]"
pytest
```

The tests cover catalogue validation, the deterministic selector (including full-rotation and
wrap-around behaviour), both renderers, the CLI, the offline RCSB parser, and web/catalogue sync.

## License

[MIT](LICENSE). Protein structure data and images are provided by the RCSB Protein Data Bank; see
[rcsb.org](https://www.rcsb.org) for their terms and how to cite the PDB.
