import csv
from datetime import date
from pathlib import Path

import pytest

import validate as v

ROOT = Path(__file__).resolve().parents[1]


def test_known_currency_passes():
    v.check_currency("GBP", {"GBP": 1.28})


def test_unexpected_currency_fails():
    with pytest.raises(ValueError, match="unknown currency"):
        v.check_currency("JPY", {"USD": 1.0, "GBP": 1.28})


@pytest.mark.parametrize("band", [(None, 1, 2), (1, None, 2), (1, 0, None)])
def test_missing_values_fail(band):
    with pytest.raises(ValueError, match="missing"):
        v.check_band(*band)


def test_range_out_of_order_fails():
    with pytest.raises(ValueError, match="out of order"):
        v.check_band(10, 12, 15)


def test_negative_value_fails():
    with pytest.raises(ValueError, match="negative"):
        v.check_band(-1, -2, 0)


def test_dates():
    ref = date(2026, 11, 20)
    v.check_as_of(None, ref)
    v.check_as_of(date(2025, 12, 31), ref)
    with pytest.raises(ValueError, match="after the reference"):
        v.check_as_of(date(2027, 1, 1), ref)
    with pytest.raises(ValueError, match="before"):
        v.check_as_of(date(1999, 12, 31), ref)
    with pytest.raises(ValueError, match="not a date"):
        v.check_as_of("2025-12-31", ref)


@pytest.mark.parametrize("bad", ["IN-7", "IN-0071", "in-007", "", None])
def test_bad_licensee_ids_fail(bad):
    with pytest.raises(ValueError):
        v.check_licensee_id(bad)


@pytest.mark.parametrize("cui", ["38120136", "4857649", "RO15412557"])
def test_valid_cui(cui):
    v.check_cui(cui)


@pytest.mark.parametrize("cui", ["38120137", "4857640", "12A45", "1"])
def test_invalid_cui(cui):
    with pytest.raises(ValueError):
        v.check_cui(cui)


def test_lei_checksum():
    v.check_lei("222100L55MU9BDNLAF50")
    with pytest.raises(ValueError, match="checksum"):
        v.check_lei("222100L55MU9BDNLAF51")
    with pytest.raises(ValueError):
        v.check_lei("222100L55MU9BDNLAF5")


@pytest.mark.parametrize("number", ["09689240", "SC123456", "NI624062"])
def test_valid_uk_company_numbers(number):
    v.check_uk_company_number(number)


@pytest.mark.parametrize("number", ["9689240", "AB123456", "0968924X", ""])
def test_invalid_uk_company_numbers(number):
    with pytest.raises(ValueError):
        v.check_uk_company_number(number)


def test_swiss_uid():
    v.check_swiss_uid("CHE-111.954.803")
    with pytest.raises(ValueError):
        v.check_swiss_uid("CHE-111.954.804")


def test_every_registration_id_in_the_sample_is_valid():
    rows = list(csv.DictReader(open(ROOT / "data" / "sample_matching.csv", encoding="utf-8")))
    checked = sum(v.check_registration_ids(r["registration_id"]) for r in rows)
    assert checked == 13


def test_corrupted_registration_id_is_caught():
    with pytest.raises(ValueError):
        v.check_registration_ids("CUI 38120130; ONRC J2017014655409")


def test_missing_columns_raise_schema_error():
    with pytest.raises(v.SchemaError, match="CUI"):
        v.require_columns(["COD_INMATRICULARE"], ["COD_INMATRICULARE", "CUI"], "od_firme.csv")


def test_manifest_rows_are_complete():
    rows = list(csv.DictReader(open(ROOT / "data" / "manifest.csv", encoding="utf-8")))
    assert rows
    for r in rows:
        assert r["path"].startswith("big_data/")
        assert int(r["bytes"]) > 0
        assert len(r["sha256"]) == 64 and int(r["sha256"], 16) >= 0
        assert r["url"]
