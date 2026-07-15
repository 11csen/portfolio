"""Protein of the Day.

A tiny library and command-line tool that picks a famous protein for any
given calendar date and tells you about it. The selection is deterministic:
everyone in the world sees the same "protein of the day" on the same date,
and the full catalogue rotates before any protein repeats.

Public API
----------
- :func:`~protein_of_the_day.selector.protein_for_date`
- :func:`~protein_of_the_day.selector.protein_of_the_day`
- :func:`~protein_of_the_day.dataset.load_proteins`
- :class:`~protein_of_the_day.dataset.Protein`
"""

from .dataset import Protein, load_proteins
from .selector import protein_for_date, protein_of_the_day

__all__ = [
    "__version__",
    "Protein",
    "load_proteins",
    "protein_for_date",
    "protein_of_the_day",
]

__version__ = "1.0.0"
