"""Tests for the command-line interface."""

import json

import pytest

from protein_of_the_day.cli import main
from protein_of_the_day.selector import protein_for_date


def test_default_prints_today(capsys):
    rc = main(["--no-color"])
    out = capsys.readouterr().out
    assert rc == 0
    assert protein_for_date(None).name in out


def test_specific_date(capsys):
    rc = main(["--date", "2025-01-01", "--no-color"])
    out = capsys.readouterr().out
    assert rc == 0
    import datetime as dt

    assert protein_for_date(dt.date(2025, 1, 1)).name in out


def test_json_format_is_valid_json(capsys):
    rc = main(["--date", "2025-01-01", "--format", "json"])
    out = capsys.readouterr().out
    assert rc == 0
    data = json.loads(out)
    assert data["date"] == "2025-01-01"
    assert "pdb_id" in data
    assert data["rcsb_url"].startswith("https://")


def test_html_format(capsys):
    rc = main(["--format", "html"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "<article" in out


def test_list_text(capsys):
    rc = main(["--list"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "proteins in the catalogue" in out


def test_list_json(capsys):
    rc = main(["--list", "--format", "json"])
    out = capsys.readouterr().out
    assert rc == 0
    data = json.loads(out)
    assert isinstance(data, list)
    assert len(data) >= 20


def test_slug_lookup(capsys):
    rc = main(["--slug", "myoglobin", "--no-color"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Myoglobin" in out


def test_unknown_slug_errors(capsys):
    rc = main(["--slug", "nope"])
    captured = capsys.readouterr()
    assert rc == 1
    assert "no protein with slug" in captured.err


def test_invalid_date_is_rejected():
    with pytest.raises(SystemExit):
        main(["--date", "not-a-date"])


def test_mutually_exclusive_options():
    with pytest.raises(SystemExit):
        main(["--slug", "myoglobin", "--list"])


def test_version(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "protein-of-the-day" in out
