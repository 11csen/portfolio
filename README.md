# 🧬 Protein of the Day

This repository hosts two things:

1. **A portfolio website** (`docs/`, deployed to GitHub Pages) whose flagship piece is an
   interactive **Protein of the Day** — a live 3D protein viewer that resolves a different protein
   each day from the AlphaFold database and renders it right in the browser.
2. **A small, zero-dependency Python library and CLI** (`src/`) that picks a famous protein for any
   calendar date from a curated, PDB-based catalogue. It's a standalone tool, handy for scripting.

The website is the single source of truth for the daily protein on the live site; the Python
library is an independent utility.

---

## The website (`docs/`)

The `docs/` folder is the GitHub Pages site:

- **`index.html`** — the portfolio/CV site (design by Caroline S. E. Nielsen). Its Work section
  features the Protein of the Day.
- **`protein-of-the-day.html`** — a self-contained interactive **3D protein viewer** (3Dmol.js +
  AlphaFold DB). It picks a different protein each day (deterministically, by date) and renders the
  live structure coloured by model confidence, with rotate and surface controls. Embedded in the
  portfolio and openable full-screen.
- **`cv.html`** — a printable academic CV page.

Try it locally:

```bash
python -m http.server --directory docs 8000
# then open http://localhost:8000
```

> The company logos on the portfolio use a typographic wordmark fallback until the real image files
> (`a51-logo.png`, `synapse-logo.png`, `techbbq-logo.png`, `caroline-photo.png`) are added to
> `docs/` — drop them in with those names and they appear automatically.

### Publishing on GitHub Pages

In *Settings → Pages*, set **Source** to **GitHub Actions**. The included
[`pages.yml`](.github/workflows/pages.yml) workflow then deploys `docs/` on every push to `main`.
The viewer rotates the protein on its own each day, client-side, so there's nothing to rebuild.

---

## The Python library & CLI (`src/`)

A separate, offline utility that picks a famous protein for any date from a curated catalogue of 32
landmark proteins (myoglobin, hemoglobin, GFP, the SARS-CoV-2 spike, and more), referencing
structures in the [RCSB Protein Data Bank](https://www.rcsb.org).

Selection is deterministic:

```
epoch_day = whole days between 1970-01-01 and the target calendar date
index     = epoch_day mod (number of proteins)
```

The index advances by one each day, so every protein appears once before the cycle repeats.

> Note: the library and the website's 3D viewer are independent — they use different protein lists
> and different daily formulas, so they won't necessarily show the same protein on a given day.

Install (editable, from a clone):

```bash
pip install -e .
```

Use the CLI:

```bash
protein-of-the-day                     # today's protein
protein-of-the-day --date 2026-12-25   # a specific day
protein-of-the-day --slug gfp          # look one up by slug
protein-of-the-day --list              # show the whole catalogue
protein-of-the-day --format json       # machine-readable output
protein-of-the-day --format html       # an HTML card fragment
protein-of-the-day --live              # add live details from the RCSB PDB
```

Or use it as a library:

```python
from protein_of_the_day import protein_of_the_day, protein_for_date
import datetime as dt

today = protein_of_the_day()
print(today.name, today.pdb_id, today.rcsb_url)

xmas = protein_for_date(dt.date(2026, 12, 25))
print(xmas.name)
```

The catalogue lives in
[`src/protein_of_the_day/data/proteins.json`](src/protein_of_the_day/data/proteins.json); each entry
references a representative PDB structure and keeps to well-established, textbook-stable facts.

## Development

```bash
pip install -e ".[dev]"
pytest
```

The tests cover catalogue validation, the deterministic selector (including full-rotation and
wrap-around behaviour), both renderers, the CLI, and the offline RCSB parser.

## License

[MIT](LICENSE). Protein structure data and images are provided by the RCSB Protein Data Bank; see
[rcsb.org](https://www.rcsb.org) for their terms and how to cite the PDB.
