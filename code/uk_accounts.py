"""How often do UK electronic accounts carry a reported headcount?

Reads Companies House daily bulk accounts zips from big_data/ch/ and counts
filings that contain AverageNumberEmployeesDuringPeriod.

Run from the repo root:  python3 code/uk_accounts.py
"""
import zipfile
from collections import Counter
from pathlib import Path

import ixbrl

ROOT = Path(__file__).resolve().parents[1]
CH = ROOT / "big_data" / "ch"
TURNOVER = ("TurnoverRevenue", "Turnover")


def band(v):
    return "1 to 9" if v < 10 else "10 to 49" if v < 50 else "50 to 249" if v < 250 else "250 or more"


def main():
    zips = sorted(CH.glob("Accounts_Bulk_Data-*.zip"))
    n = has_emp = emp_pos = has_turn = dormant = unreadable = recovered = 0
    scale_flags = Counter()
    skipped = Counter()
    bands = Counter()
    for z in zips:
        with zipfile.ZipFile(z) as zf:
            for name in zf.namelist():
                if not name.lower().endswith((".html", ".xhtml", ".xml")):
                    skipped[name.rsplit(".", 1)[-1].lower()] += 1
                    continue
                n += 1
                try:
                    f = ixbrl.parse(zf.read(name))
                except ixbrl.FilingFormatError:
                    unreadable += 1
                    continue
                recovered += f.recovered
                is_dormant = f.is_dormant()
                dormant += is_dormant
                has_turn += f.first(*TURNOVER) is not None
                emp = f.first("AverageNumberEmployeesDuringPeriod")
                if emp:
                    has_emp += 1
                    if emp.scale:
                        scale_flags[emp.scale] += 1
                    if emp.shown:
                        emp_pos += 1
                        bands[band(emp.shown)] += 1
                    elif not is_dormant:
                        bands["0, trading"] += 1
    print(f"daily files: {', '.join(z.stem[-10:] for z in zips)}")
    print(f"filings:                         {n:,}")
    print(f"  with the headcount tag:        {has_emp:,} = {has_emp / n:.1%}")
    print(f"  with a headcount above zero:   {emp_pos:,} = {emp_pos / n:.1%}")
    print(f"  with turnover reported:        {has_turn:,} = {has_turn / n:.1%}")
    print(f"  flagged dormant:               {dormant:,} = {dormant / n:.1%}")
    print("headcount bands among tagged filings:")
    for b in ["0, trading", "1 to 9", "10 to 49", "50 to 249", "250 or more"]:
        print(f"  {b:12} {bands[b]:>8,}")
    flags = ", ".join(f"{v:,} with scale {k}" for k, v in sorted(scale_flags.items()))
    print(f"headcounts read as displayed despite a scale attribute: {flags or 'none'}")
    print(f"parsing: {unreadable:,} unreadable, {recovered:,} read after repairing malformed markup")
    print(f"skipped, not a filing: {', '.join(f'{v} .{k}' for k, v in sorted(skipped.items())) or 'none'}")


if __name__ == "__main__":
    main()
