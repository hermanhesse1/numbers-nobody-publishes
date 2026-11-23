import copy
import csv
from datetime import date
from pathlib import Path

import pytest

import build_workbook as wb
import check
import estimates
import validate

ROOT = Path(__file__).resolve().parents[1]


def b(mid, low=None, high=None):
    return estimates.band(mid, mid if low is None else low, mid if high is None else high)


def rows_by_id():
    return {r["id"]: r for r in estimates.ROWS}


def matches():
    return {r["id"]: r for r in csv.DictReader(open(ROOT / "data" / "sample_matching.csv", encoding="utf-8"))}


# Revenue calculations

def test_msc_revenue_adds_container_cruise_and_other():
    p = {("msc", "fleet_teu"): b(2), ("msc", "revenue_per_teu"): b(10000, 8000, 12000),
         ("msc", "cruise_passengers"): b(1), ("msc", "cruise_revenue_per_passenger"): b(2, 1, 3),
         ("msc", "other_revenue"): b(5, 4, 6)}
    out = estimates.msc_group_revenue(p)
    assert out == pytest.approx({"mid": 2 * 10 + 2 + 5, "low": 2 * 8 + 1 + 4, "high": 2 * 12 + 3 + 6})


def test_hotel_revenue_formula():
    p = {("drury", "hotels"): b(10), ("drury", "rooms_per_hotel"): b(100), ("drury", "occupancy"): b(0.5),
         ("drury", "room_rate"): b(100), ("drury", "other_revenue_share"): b(0.1)}
    assert estimates.drury_revenue(p)["mid"] == pytest.approx(10 * 100 * 365 * 0.5 * 100 * 1.1 / 1e6)


def test_customers_per_employee_inverts_the_band():
    p = {("kedny", "customers"): b(1000), ("kedny", "customers_per_employee"): b(100, 50, 200)}
    out = estimates.kedny_employees(p)
    assert (out["low"], out["mid"], out["high"]) == (5, 10, 20)


def test_revenue_per_employee_formula():
    p = {("margot", "employees"): b(10), ("margot", "revenue_per_employee"): b(0.05, 0.04, 0.06)}
    assert estimates.margot_revenue(p) == pytest.approx({"mid": 0.5, "low": 0.4, "high": 0.6})


def test_published_estimates_come_from_the_input_file():
    fresh = estimates.load_inputs()
    assert estimates.msc == pytest.approx(estimates.msc_group_revenue(fresh))
    assert estimates.drury == pytest.approx(estimates.drury_revenue(fresh))
    assert estimates.margot == pytest.approx(estimates.margot_revenue(fresh))


def test_no_function_is_defined_twice():
    import ast
    for path in (ROOT / "code").glob("*.py"):
        names = [n.name for n in ast.parse(path.read_text(encoding="utf-8")).body if isinstance(n, ast.FunctionDef)]
        assert len(names) == len(set(names)), f"{path.name} redefines {sorted({n for n in names if names.count(n) > 1})}"


# Currency conversions

def test_currency_conversion_uses_the_rate_table():
    assert estimates.usd_value(b(100), "GBP", "Revenue") == pytest.approx(128)
    assert estimates.usd_value(b(100), "USD", "Revenue") == 100


def test_unknown_currency_is_rejected_not_guessed():
    with pytest.raises(ValueError, match="unknown currency"):
        estimates.usd_value(b(100), "JPY", "Revenue")


def test_non_revenue_metrics_get_no_usd_value():
    assert estimates.usd_value(b(518000), "SGD", "Net portfolio value at market value") is None
    assert estimates.usd_value(None, "GBP", "Revenue") is None


def test_published_usd_column_matches_the_conversion():
    for r in csv.DictReader(open(ROOT / "output" / "sample_estimates.csv", encoding="utf-8")):
        if r["revenue_usd_m"]:
            expected = float(r["revenue_m"]) * estimates.USD_PER[r["currency"]]
            assert float(r["revenue_usd_m"]) == pytest.approx(expected, rel=1e-3), r["id"]


# Figures in the wrong unit

@pytest.mark.parametrize("mid, factor", [("IN-015", 1000), ("IN-061", 1e6), ("IN-016", 0.001), ("IN-007", 1000)])
def test_revenue_in_the_wrong_unit_is_caught(mid, factor):
    row = copy.deepcopy(rows_by_id()[mid])
    row["rev"] = {k: v * factor for k, v in row["rev"].items()}
    with pytest.raises(ValueError, match="thousands or millions|check the unit"):
        estimates.validate_rows([row], matches())


def test_headcount_in_the_wrong_unit_is_caught():
    row = copy.deepcopy(rows_by_id()["IN-011"])
    row["emp"] = {k: v * 1000 for k, v in row["emp"].items()}
    with pytest.raises(ValueError, match="per employee"):
        estimates.validate_rows([row], matches())


def test_every_committed_row_passes_the_unit_check():
    estimates.validate_rows(estimates.ROWS, matches())


def test_revenue_beyond_any_company_is_rejected_without_headcount():
    with pytest.raises(ValueError, match="check the unit"):
        validate.check_revenue_scale(5_000_000)


# Missing and zero values

def test_zero_employees_with_revenue_is_allowed():
    validate.check_revenue_scale(0.093, 0)
    estimates.validate_rows([rows_by_id()["IN-064"]], matches())


def test_zero_revenue_is_allowed():
    validate.check_revenue_scale(0, 5)


def test_zero_employees_is_the_micro_tier():
    assert wb.tier(0, wb.STAFF_EDGES) == "Micro"


def test_missing_value_has_no_tier():
    assert wb.tier(None, wb.STAFF_EDGES) is None


def test_missing_low_end_is_rejected():
    row = copy.deepcopy(rows_by_id()["IN-099"])
    row["rev"]["low"] = None
    with pytest.raises(ValueError, match="missing"):
        estimates.validate_rows([row], matches())


@pytest.mark.parametrize("staff, tier", [(9, "Micro"), (10, "Small"), (49, "Small"), (50, "Medium"),
                                         (249, "Medium"), (250, "Large"), (4999, "Large"), (5000, "Enterprise")])
def test_tier_boundaries(staff, tier):
    assert wb.tier(staff, wb.STAFF_EDGES) == tier


def workbook_row(**kw):
    r = {k: "" for k in ("employees", "employees_low", "employees_high", "revenue_usd_m", "revenue_m",
                         "revenue_low_m", "revenue_high_m", "employees_basis", "revenue_basis")}
    r["outcome_bucket"] = "MATCHED"
    r.update(kw)
    return r


def test_no_figures_cannot_be_sized():
    assert wb.size(workbook_row()) == ("Cannot size", "", "None")


def test_range_crossing_a_tier_is_low_confidence():
    r = workbook_row(employees="40", employees_low="30", employees_high="60", employees_basis="PROXY")
    assert wb.size(r) == ("Small to Medium", "Headcount", "Low")


def test_revenue_tier_converts_the_range_to_usd():
    r = workbook_row(revenue_m="30", revenue_low_m="25", revenue_high_m="35", revenue_usd_m="6.6",
                     revenue_basis="REPORTED")
    assert wb.size(r) == ("Small", "Revenue", "High")


# Inactive companies

def test_inactive_company_is_not_sized_even_with_figures():
    r = workbook_row(outcome_bucket="MATCHED_INACTIVE", employees="50", employees_low="50", employees_high="50")
    assert wb.size(r) == ("Not operating", "", "None")


def test_inactive_companies_carry_no_figures_in_the_output(tmp_path, monkeypatch):
    monkeypatch.setattr(estimates, "OUT_FILE", tmp_path / "out.csv")
    estimates.main()
    inactive = [r for r in csv.DictReader(open(tmp_path / "out.csv", encoding="utf-8"))
                if r["outcome_bucket"] == "MATCHED_INACTIVE"]
    assert {r["id"] for r in inactive} == {"IN-082", "IN-086", "IN-087"}
    for r in inactive:
        assert r["revenue_basis"] == r["employees_basis"] == "NONE"
        assert r["revenue_m"] == r["employees"] == ""
        assert r["client_action"]


def test_check_flags_an_inactive_company_with_figures():
    rows = list(csv.DictReader(open(ROOT / "output" / "sample_estimates.csv", encoding="utf-8")))
    bad = next(r for r in rows if r["id"] == "IN-087")
    bad.update(revenue_basis="REPORTED", revenue_m="1", revenue_low_m="1", revenue_high_m="1", revenue_as_of="2025-01-01")
    check.errors.clear()
    check.rows_checks(rows, list(matches().values()))
    assert any("inactive company carries figures" in e for e in check.errors)
    check.errors.clear()


# Dates

def test_age_in_months():
    assert estimates.months_old(date(2025, 5, 31)) == 18
    assert estimates.months_old(date(2025, 4, 1)) == 19


def test_as_of_before_2000_is_rejected():
    with pytest.raises(ValueError, match="before"):
        estimates.validate_rows([rows_by_id()["IN-061"]], matches(), as_of={"IN-061": (date(1998, 1, 1), None)})


def test_as_of_after_reference_is_rejected():
    with pytest.raises(ValueError, match="after the reference"):
        estimates.validate_rows([rows_by_id()["IN-061"]], matches(), as_of={"IN-061": (None, date(2027, 6, 30))})


# Unexpected input formats

def test_matching_file_with_a_missing_column_is_rejected(tmp_path, monkeypatch):
    p = tmp_path / "matching.csv"
    p.write_text("id,licensee_name,matched_entity\nIN-061,MARGOT BAKERY LIMITED,MARGOT BAKERY LIMITED\n", encoding="utf-8")
    monkeypatch.setattr(estimates, "MATCH_FILE", p)
    with pytest.raises(validate.SchemaError, match="outcome_bucket"):
        estimates.main()


def test_matching_file_with_a_bad_identifier_is_rejected(tmp_path, monkeypatch):
    src = (ROOT / "data" / "sample_matching.csv").read_text(encoding="utf-8")
    p = tmp_path / "matching.csv"
    p.write_text(src.replace("CUI 38120136", "CUI 38120137"), encoding="utf-8")
    monkeypatch.setattr(estimates, "MATCH_FILE", p)
    with pytest.raises(ValueError, match="check digit"):
        estimates.main()


def test_inputs_with_formatted_numbers_are_rejected(tmp_path):
    p = tmp_path / "inputs.csv"
    p.write_text('proxy,parameter,mid,low,high,unit,as_of,source\nx,y,"1,234",1,2,unit,2025,somewhere\n', encoding="utf-8")
    with pytest.raises(ValueError):
        estimates.load_inputs(p)


def test_inputs_with_the_wrong_delimiter_are_rejected(tmp_path):
    p = tmp_path / "inputs.csv"
    p.write_text("proxy;parameter;mid;low;high;unit;as_of;source\nx;y;1;1;1;unit;2025;somewhere\n", encoding="utf-8")
    with pytest.raises(validate.SchemaError):
        estimates.load_inputs(p)
