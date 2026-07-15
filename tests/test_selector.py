"""Tests for the deterministic date-based selector."""

import datetime as dt

import pytest

from protein_of_the_day.dataset import load_proteins
from protein_of_the_day.selector import (
    epoch_day,
    index_for_date,
    protein_for_date,
    protein_of_the_day,
)


def test_epoch_day_anchor():
    assert epoch_day(dt.date(1970, 1, 1)) == 0
    assert epoch_day(dt.date(1970, 1, 2)) == 1
    assert epoch_day(dt.date(1969, 12, 31)) == -1


def test_selection_is_deterministic():
    day = dt.date(2024, 3, 14)
    assert protein_for_date(day) is protein_for_date(day)


def test_selection_advances_by_one_each_day():
    count = len(load_proteins())
    base = dt.date(2025, 1, 1)
    for offset in range(count * 2):
        day = base + dt.timedelta(days=offset)
        expected = (index_for_date(base, count) + offset) % count
        assert index_for_date(day, count) == expected


def test_full_rotation_before_repeat():
    """Every protein appears exactly once across one catalogue-length window."""
    count = len(load_proteins())
    start = dt.date(2025, 6, 1)
    seen = {
        protein_for_date(start + dt.timedelta(days=offset)).slug
        for offset in range(count)
    }
    assert len(seen) == count


def test_index_wraps_around():
    count = len(load_proteins())
    a = dt.date(2025, 1, 1)
    b = a + dt.timedelta(days=count)
    assert index_for_date(a, count) == index_for_date(b, count)


def test_pre_epoch_dates_have_valid_index():
    count = len(load_proteins())
    day = dt.date(1900, 1, 1)
    idx = index_for_date(day, count)
    assert 0 <= idx < count


def test_index_for_date_rejects_bad_count():
    with pytest.raises(ValueError):
        index_for_date(dt.date(2025, 1, 1), 0)


def test_protein_for_date_accepts_datetime():
    day = dt.date(2025, 9, 9)
    moment = dt.datetime(2025, 9, 9, 13, 30, 0)
    assert protein_for_date(moment) is protein_for_date(day)


def test_default_is_today():
    assert protein_of_the_day() is protein_for_date(dt.date.today())


def test_protein_for_date_rejects_bad_type():
    with pytest.raises(TypeError):
        protein_for_date("2025-01-01")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "iso,expected_index",
    [
        ("1970-01-01", 0),
        ("1970-01-02", 1),
    ],
)
def test_known_reference_points(iso, expected_index):
    count = len(load_proteins())
    day = dt.date.fromisoformat(iso)
    assert index_for_date(day, count) == expected_index % count
