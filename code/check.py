"""Check the outputs for internal consistency and the README against the outputs.

Run from the repo root after the other scripts:  python3 code/check.py
"""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
errors = []


def check(ok, msg):
    if not ok:
        errors.append(msg)


def num(s):
    return float(s) if s else None


def rows_checks(rows, matching):
    ids = [r["id"] for r in rows]
    check(len(ids) == len(set(ids)), "duplicate ids in sample_estimates.csv")
    check(set(ids) == {m["id"] for m in matching}, "estimate ids differ from sample_matching.csv")
    for r in rows:
        i = r["id"]
        for k in ("revenue", "employees"):
            mid_key = "revenue_m" if k == "revenue" else "employees"
            lo_key = "revenue_low_m" if k == "revenue" else "employees_low"
            hi_key = "revenue_high_m" if k == "revenue" else "employees_high"
            mid, lo, hi = num(r[mid_key]), num(r[lo_key]), num(r[hi_key])
            basis = r[f"{k}_basis"]
            if basis == "NONE":
                check(mid is None, f"{i}: {k} basis NONE but a value is given")
            else:
                check(None not in (mid, lo, hi), f"{i}: {k} has basis {basis} but no full range")
                if None not in (mid, lo, hi):
                    check(lo <= mid <= hi, f"{i}: {k} range out of order {lo} {mid} {hi}")
                check(r[f"{k}_as_of"] != "" or "no date" in r["age_flag"], f"{i}: {k} undated without a flag")
        if r["revenue_basis"] != "NONE" or r["employees_basis"] != "NONE":
            check(r["sources"].strip() != "", f"{i}: figures without sources")
            check(r["derivation"].strip() != "", f"{i}: figures without a derivation")
        check(r["client_action"].strip() != "", f"{i}: no client action")
        if r["outcome_bucket"] == "MATCHED_INACTIVE":
            check(r["revenue_basis"] == r["employees_basis"] == "NONE", f"{i}: inactive company carries figures")
        months = num(r["oldest_figure_months"])
        stale = "older than 18 months" in r["age_flag"]
        check(stale == (months is not None and months > 18), f"{i}: age flag disagrees with {months} months")


def readme_checks(rows, readme):
    def count(col, values):
        return sum(r[col] in values for r in rows)
    table = {
        "Reported in a filing or a segment of one": ({"REPORTED", "REPORTED_SEGMENT"},),
        "Declared by the company": ({"SELF_DECLARED"},),
        "Estimated from proxies": ({"PROXY"},),
        "Left blank, with a reason": ({"NONE"},),
    }
    for label, (values,) in table.items():
        m = re.search(rf"\| {re.escape(label)} \| (\d+) \| (\d+) \|", readme)
        check(m is not None, f"README basis row missing: {label}")
        if m:
            check(int(m.group(1)) == count("revenue_basis", values), f"README revenue count wrong for {label}")
            check(int(m.group(2)) == count("employees_basis", values), f"README employee count wrong for {label}")
    stale = sum("older than 18 months" in r["age_flag"] for r in rows)
    words = {3: "three", 4: "four", 5: "five", 6: "six", 7: "seven"}
    check(f"{words.get(stale, stale)} rows hold a figure over 18 months old" in readme,
          f"README stale row count should be {stale}")
    check(f"{len(rows)} entities" in readme, f"README sample size should be {len(rows)}")

    reg = (OUT / "register_counts.txt").read_text()
    uk = (OUT / "uk_accounts_counts.txt").read_text()
    for figure, source, name in [
        (r"inside the line.*?: ([\d,]+)", reg, "inside the line"),
        (r"single capacity code only:\s+([\d,]+)", reg, "lower bound"),
        (r"any capacity code:\s+([\d,]+)", reg, "upper bound"),
        (r"living, operating with no dead status:\s+([\d,]+)", reg, "living register"),
        (r"filings:\s+([\d,]+)", uk, "UK filings"),
        (r"with the headcount tag:.*= ([\d.]+%)", uk, "UK tag share"),
        (r"with a headcount above zero:.*= ([\d.]+%)", uk, "UK headcount share"),
        (r"with turnover reported:.*= ([\d.]+%)", uk, "UK turnover share"),
    ]:
        m = re.search(figure, source)
        check(m is not None and m.group(1) in readme, f"README does not show {name} {m.group(1) if m else '?'}")
    check(not re.search("[\\u2013\\u2014]", readme), "README contains dashes")


def main():
    rows = list(csv.DictReader(open(OUT / "sample_estimates.csv", encoding="utf-8")))
    matching = list(csv.DictReader(open(ROOT / "data" / "sample_matching.csv", encoding="utf-8")))
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    rows_checks(rows, matching)
    readme_checks(rows, readme)
    if errors:
        print("\n".join(errors))
        sys.exit(1)
    print(f"all checks passed on {len(rows)} rows and the README")


if __name__ == "__main__":
    main()
