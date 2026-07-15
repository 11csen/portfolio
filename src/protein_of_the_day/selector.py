"""Deterministic date-based selection of the protein of the day.

The selection algorithm is deliberately simple and portable so that it can be
reproduced exactly in other languages (see ``docs/app.js`` for the JavaScript
twin used by the web app):

    epoch_day = number of whole days between 1970-01-01 and the target date
    index     = epoch_day mod (number of proteins)

Because the index steps forward by one each day, the catalogue rotates
completely before any protein repeats, and every date maps to a single,
globally consistent protein.
"""

from __future__ import annotations

import datetime as _dt

from .dataset import Protein, load_proteins

#: Anchor date for the rotation. Chosen to match the Unix epoch so the same
#: arithmetic (``floor(Date.UTC(...) / 86400000)``) works in JavaScript.
_EPOCH = _dt.date(1970, 1, 1)


def epoch_day(day: _dt.date) -> int:
    """Return the number of whole days from 1970-01-01 to ``day``."""
    return (day - _EPOCH).days


def index_for_date(day: _dt.date, count: int) -> int:
    """Return the catalogue index for ``day`` given a catalogue of ``count`` items.

    Raises:
        ValueError: if ``count`` is not positive.
    """
    if count <= 0:
        raise ValueError("count must be a positive integer")
    # Python's modulo already returns a non-negative result for a positive
    # divisor, which keeps pre-1970 dates well behaved.
    return epoch_day(day) % count


def _coerce_date(day: _dt.date | _dt.datetime | None) -> _dt.date:
    if day is None:
        return _dt.date.today()
    if isinstance(day, _dt.datetime):
        return day.date()
    if isinstance(day, _dt.date):
        return day
    raise TypeError(f"Expected a date or datetime, got {type(day).__name__}")


def protein_for_date(day: _dt.date | _dt.datetime | None = None) -> Protein:
    """Return the protein assigned to ``day`` (defaults to today, local time)."""
    resolved = _coerce_date(day)
    proteins = load_proteins()
    return proteins[index_for_date(resolved, len(proteins))]


def protein_of_the_day() -> Protein:
    """Return today's protein (local calendar date)."""
    return protein_for_date(None)
