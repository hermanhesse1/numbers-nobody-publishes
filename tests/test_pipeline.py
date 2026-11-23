import csv
from datetime import date
from pathlib import Path
from statistics import median

import pytest

import backtest
import estimates
import ixbrl
import uk_licensees
import validate

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).parent / "fixtures"


def write_inputs(tmp_path, rows, header="proxy,parameter,mid,low,high,unit,as_of,source"):
    p = tmp_path / "inputs.csv"
    p.write_text(header + "\n" + "\n".join(rows) + "\n", encoding="utf-8")
    return p


def test_inputs_without_a_source_are_rejected(tmp_path):
    with pytest.raises(ValueError, match="no source"):
        estimates.load_inputs(write_inputs(tmp_path, ["x,y,1,1,1,unit,2025,"]))


def test_inputs_out_of_order_are_rejected(tmp_path):
    with pytest.raises(ValueError, match="out of order"):
        estimates.load_inputs(write_inputs(tmp_path, ["x,y,5,6,7,unit,2025,somewhere"]))


def test_inputs_with_a_changed_layout_are_rejected(tmp_path):
    with pytest.raises(validate.SchemaError):
        estimates.load_inputs(write_inputs(tmp_path, ["x,y,1"], header="proxy,parameter,value"))


def row(**kw):
    base = dict(id="IN-061", cur="GBP", rev=estimates.band(1, 1, 1), emp=estimates.band(13, 13, 13))
    base.update(kw)
    return base


def test_unexpected_currency_in_a_row_is_rejected():
    with pytest.raises(ValueError, match="unknown currency"):
        estimates.validate_rows([row(cur="JPY")], {"IN-061": {}})


def test_row_for_an_unmatched_id_is_rejected():
    with pytest.raises(ValueError, match="not in"):
        estimates.validate_rows([row(id="IN-999")], {"IN-061": {}})


def test_future_as_of_date_is_rejected():
    with pytest.raises(ValueError, match="after the reference"):
        estimates.validate_rows([row()], {"IN-061": {}}, as_of={"IN-061": (date(2027, 1, 1), None)})


def test_missing_employee_range_is_rejected():
    with pytest.raises(ValueError, match="missing"):
        estimates.validate_rows([row(emp=estimates.band(13, None, 13))], {"IN-061": {}})


def test_proxy_formulas_reproduce_the_published_estimates():
    msc, drury, margot = estimates.msc_group_revenue(), estimates.drury_revenue(), estimates.margot_revenue()
    assert round(msc["mid"]) == 68 and round(msc["low"]) == 55 and round(msc["high"]) == 76
    assert round(drury["mid"], -1) == 940
    assert margot["mid"] == pytest.approx(0.624)


def test_shipping_rate_input_matches_the_peer_median():
    rates = [rev / teu * 1000 for teu, rev in backtest.CARRIERS.values()]
    assert estimates.P["msc", "revenue_per_teu"]["mid"] == pytest.approx(median(rates), rel=0.01)


def test_estimates_reproduce_the_committed_csv(tmp_path, monkeypatch):
    committed = (ROOT / "output" / "sample_estimates.csv").read_text(encoding="utf-8")
    monkeypatch.setattr(estimates, "OUT_FILE", tmp_path / "out.csv")
    estimates.main()
    assert (tmp_path / "out.csv").read_text(encoding="utf-8") == committed


def test_backtest_coverage_matches_the_readme_claim():
    cases = backtest.shipping() + backtest.gas() + backtest.hotels()
    assert sum(lo <= actual <= hi for _, _, _, lo, hi, actual in cases) == 8 and len(cases) == 11


def test_summarise_a_micro_filing():
    out = uk_licensees.summarise(ixbrl.parse((FIXTURES / "micro.html").read_bytes()))
    assert out == dict(period_end="2025-12-31", employees=13, turnover_gbp_m="",
                       note="headcount reported; turnover not disclosed")


def test_uk_licensee_numbers_are_valid():
    for _, _, number in uk_licensees.LICENSEES:
        validate.check_uk_company_number(number)


def test_outputs_pass_the_consistency_check():
    import check
    check.errors.clear()
    rows = list(csv.DictReader(open(ROOT / "output" / "sample_estimates.csv", encoding="utf-8")))
    matching = list(csv.DictReader(open(ROOT / "data" / "sample_matching.csv", encoding="utf-8")))
    check.rows_checks(rows, matching)
    check.readme_checks(rows, (ROOT / "README.md").read_text(encoding="utf-8"))
    assert check.errors == []
