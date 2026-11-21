"""How often do UK electronic accounts carry a reported headcount?

Reads Companies House daily bulk accounts zips from big_data/ch/ and counts
filings that contain AverageNumberEmployeesDuringPeriod.

Run from the repo root:  python3 code/uk_accounts.py
"""
import re
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CH = ROOT / "big_data" / "ch"

EMP = re.compile(rb'name="[\w-]+:AverageNumberEmployeesDuringPeriod"[^>]*>(.*?)</ix:nonFraction>', re.S | re.I)
TURNOVER = re.compile(rb'name="[\w-]+:(TurnoverRevenue|Turnover)"', re.I)
DORMANT = re.compile(rb'name="[\w-]+:EntityDormantTruefalse"[^>]*>\s*true|RelatingToDormantCompanies"', re.I)
TAGS = re.compile(rb"<[^>]+>")


def value(raw):
    digits = re.sub(rb"[^\d]", b"", TAGS.sub(b"", raw))
    return int(digits) if digits else None


def main():
    zips = sorted(CH.glob("Accounts_Bulk_Data-*.zip"))
    n = has_emp = emp_pos = has_turn = dormant = 0
    bands = Counter()
    for z in zips:
        with zipfile.ZipFile(z) as zf:
            for name in zf.namelist():
                if not name.lower().endswith((".html", ".xhtml", ".xml")):
                    continue
                doc = zf.read(name)
                n += 1
                is_dormant = bool(DORMANT.search(doc))
                dormant += is_dormant
                has_turn += bool(TURNOVER.search(doc))
                m = EMP.search(doc)
                if m:
                    has_emp += 1
                    v = value(m.group(1))
                    if v:
                        emp_pos += 1
                        bands["1 to 9" if v < 10 else "10 to 49" if v < 50 else "50 to 249" if v < 250 else "250 or more"] += 1
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


if __name__ == "__main__":
    main()
