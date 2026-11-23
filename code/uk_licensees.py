"""Read headcount and turnover for the UK licensees from their latest iXBRL accounts.

Company numbers were matched by hand on Companies House. The script fetches each
company's status and newest electronic accounts from the public site, no API key.

Run from the repo root:  python3 code/uk_licensees.py
"""
import csv
import re
import time
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import ixbrl
from validate import check_uk_company_number

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "uk_licensees.csv"
BASE = "https://find-and-update.company-information.service.gov.uk"

LICENSEES = [
    ("IN-005", "SIEMENS MOBILITY LIMITED", "00016033"),
    ("IN-023", "Toyota Motor Manufacturing (UK) Limited", "02352348"),
    ("IN-060", "OLIVIER'S BAKERY LTD", "07675953"),
    ("IN-061", "MARGOT BAKERY LIMITED", "09689240"),
    ("IN-062", "ZAITUN BAKERY LTD", "14331415"),
    ("IN-072", "Currys PC World", "07105905"),
    ("IN-083", "LEVE BAKERY LTD", "13943554"),
    ("IN-087", "BAKERY BAKERY LTD", "09222489"),
]

TURNOVER = ("TurnoverRevenue", "Revenue")


SESSION = requests.Session()
SESSION.headers["User-Agent"] = "research-script"
SESSION.mount("https://", HTTPAdapter(max_retries=Retry(total=4, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])))


def get(path, binary=False):
    r = SESSION.get(BASE + path, timeout=60)
    r.raise_for_status()
    time.sleep(1)
    return r.content if binary else r.text


def summarise(filing):
    """Headcount, turnover in GBP m, period end and a note from one parsed filing."""
    emp = filing.latest("AverageNumberEmployeesDuringPeriod")
    turn = filing.latest(*TURNOVER)
    end = filing.period_end()
    if filing.is_dormant():
        note = "dormant accounts"
    else:
        note = ("headcount reported" if emp else "no headcount tag") + \
               ("; turnover reported" if turn else "; turnover not disclosed")
        if emp and emp.scale:
            note += f"; headcount tagged with scale {emp.scale}, read as displayed"
    return dict(period_end=end.isoformat() if end else "",
                employees=int(emp.shown) if emp else "",
                turnover_gbp_m=round(turn.value / 1e6, 3) if turn else "",
                note=note)


def status(number):
    page = get(f"/company/{number}")
    m = re.search(r'id="company-status"[^>]*>\s*([^<]+?)\s*<', page)
    if not m:
        raise RuntimeError(f"company page for {number} has no status field; the site layout may have changed")
    return m.group(1)


def latest_accounts(number):
    page = get(f"/company/{number}/filing-history?category=accounts")
    if "filing-history" not in page:
        raise RuntimeError(f"filing history for {number} not recognised; the site layout may have changed")
    links = re.findall(r'href="(/company/\w+/filing-history/\w+/document\?format=xhtml)', page)
    return links[0] if links else None


def main():
    rows = []
    for mid, name, number in LICENSEES:
        check_uk_company_number(number)
        row = dict(id=mid, licensee_name=name, company_number=number, status=status(number),
                   period_end="", employees="", turnover_gbp_m="", note="")
        link = latest_accounts(number)
        if not link:
            row["note"] = "accounts filed as PDF only; read by hand"
        else:
            try:
                row.update(summarise(ixbrl.parse(get(link + "&download=1", binary=True))))
            except ixbrl.FilingFormatError as e:
                row["note"] = f"electronic accounts not readable: {e}"
        rows.append(row)
        print(row)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
