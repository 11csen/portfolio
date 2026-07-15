"""Command-line interface for Protein of the Day."""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from typing import Any, Sequence

from . import __version__
from .dataset import Protein, get_by_slug, load_proteins
from .render import render_html_card, render_text
from .selector import protein_for_date


def _parse_date(value: str) -> _dt.date:
    try:
        return _dt.date.fromisoformat(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"invalid date {value!r}: expected ISO format YYYY-MM-DD"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="protein-of-the-day",
        description="Show a famous protein chosen deterministically for a given day.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    what = parser.add_mutually_exclusive_group()
    what.add_argument(
        "-d",
        "--date",
        type=_parse_date,
        metavar="YYYY-MM-DD",
        help="show the protein for a specific date (default: today)",
    )
    what.add_argument(
        "-s",
        "--slug",
        metavar="SLUG",
        help="show a specific protein by its slug (see --list)",
    )
    what.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="list every protein in the catalogue and exit",
    )

    parser.add_argument(
        "-f",
        "--format",
        choices=("text", "json", "html"),
        default="text",
        help="output format (default: text)",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="enrich the output with live metadata from the RCSB PDB (needs network)",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=None,
        help="wrap width for text output (default: terminal width)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="disable ANSI colours in text output",
    )
    return parser


def _fetch_live(protein: Protein) -> dict[str, Any] | None:
    # Imported lazily so the dependency-free core never touches the network
    # module unless the user opts in.
    from .rcsb import fetch_entry_metadata

    return fetch_entry_metadata(protein.pdb_id)


def _render_list(proteins: Sequence[Protein], fmt: str) -> str:
    if fmt == "json":
        return json.dumps([p.to_dict() for p in proteins], indent=2, ensure_ascii=False)
    width = max((len(p.slug) for p in proteins), default=0)
    lines = [f"{len(proteins)} proteins in the catalogue:", ""]
    for protein in proteins:
        lines.append(f"  {protein.slug.ljust(width)}  {protein.name} ({protein.pdb_id})")
    return "\n".join(lines)


def _render_one(
    protein: Protein,
    fmt: str,
    day: _dt.date,
    *,
    color: bool,
    width: int | None,
    live: dict[str, Any] | None,
) -> str:
    if fmt == "json":
        data = protein.to_dict()
        data["date"] = day.isoformat()
        if live:
            data["live"] = live
        return json.dumps(data, indent=2, ensure_ascii=False)
    if fmt == "html":
        return render_html_card(protein, day=day, live=live)
    return render_text(protein, day=day, width=width, color=color, live=live)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        proteins = load_proteins()
    except (ValueError, OSError) as exc:  # pragma: no cover - guards bad data
        print(f"error: could not load protein catalogue: {exc}", file=sys.stderr)
        return 2

    if args.list:
        print(_render_list(proteins, args.format))
        return 0

    if args.slug:
        try:
            protein = get_by_slug(args.slug)
        except KeyError:
            print(f"error: no protein with slug {args.slug!r}", file=sys.stderr)
            print("       run with --list to see available slugs", file=sys.stderr)
            return 1
        day = _dt.date.today()
    else:
        day = args.date or _dt.date.today()
        protein = protein_for_date(day)

    live = _fetch_live(protein) if args.live else None
    if args.live and live is None:
        print("note: could not reach the RCSB PDB; showing offline data.", file=sys.stderr)

    color = (not args.no_color) and args.format == "text" and sys.stdout.isatty()
    print(_render_one(protein, args.format, day, color=color, width=args.width, live=live))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
