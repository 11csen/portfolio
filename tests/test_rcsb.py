"""Offline tests for the RCSB metadata parser.

These tests never touch the network; they exercise the pure parsing logic on
representative and malformed payloads.
"""

from protein_of_the_day.rcsb import _parse_entry


def test_parse_full_payload():
    payload = {
        "struct": {"title": "SPERM WHALE MYOGLOBIN"},
        "exptl": [{"method": "X-RAY DIFFRACTION"}],
        "rcsb_entry_info": {"resolution_combined": [2.0]},
        "rcsb_accession_info": {"initial_release_date": "1973-04-01T00:00:00Z"},
    }
    result = _parse_entry(payload)
    assert result == {
        "title": "SPERM WHALE MYOGLOBIN",
        "method": "X-Ray Diffraction",
        "resolution": 2.0,
        "released": "1973-04-01",
    }


def test_parse_partial_payload():
    result = _parse_entry({"struct": {"title": "Something"}})
    assert result == {"title": "Something"}


def test_parse_multiple_methods():
    payload = {"exptl": [{"method": "X-RAY DIFFRACTION"}, {"method": "NEUTRON DIFFRACTION"}]}
    result = _parse_entry(payload)
    assert result is not None
    assert result["method"] == "X-Ray Diffraction, Neutron Diffraction"


def test_parse_empty_returns_none():
    assert _parse_entry({}) is None


def test_parse_non_dict_returns_none():
    assert _parse_entry([]) is None  # type: ignore[arg-type]


def test_parse_bad_resolution_is_skipped():
    payload = {"rcsb_entry_info": {"resolution_combined": ["oops"]}}
    assert _parse_entry(payload) is None
