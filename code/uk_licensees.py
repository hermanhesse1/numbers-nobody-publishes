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

CONTEXT = re.compile(r'<(?:xbrli:)?context[^>]*id="([^"]+)".*?</(?:xbrli:)?context>', re.S)
END = re.compile(r"<(?:xbrli:)?(?:endDate|instant)>([\d-]+)<")
DORMANT = re.compile(r'EntityDormantTruefalse"[^>]*>\s*true|RelatingToDormantCompanies"', re.I)
DIMENSIONED =re.compile(r"xbrldi:explicitMember|xbrldi:typedMember")
FACT = r'<ix:nonFraction([^>]*name="[\w-]+:{tag}"[^>]*)>(.*?)</ix:nonFraction>'
TAGS = {"employees": "AverageNumberEmployeesDuringPeriod", "turnover": "(?:TurnoverRevenue|Revenue)"}


def get(path):
    r = requests.get(BASE + path, headers={"User-Agent": "research-script"}, timeout=60)
    r.raise_for_status()
    time.sleep(1)
    return r.text


def contexts(doc):
    out = {}
    for m in CONTEXT.finditer(doc):
        if DIMENSIONED.search(m.group(0)):
            continue
        ends = END.findall(m.group(0))
        if ends:
            out[m.group(1)] = max(ends)
    return out


def latest_fact(doc, tag, ctx):
    best = None
    for attrs, raw in re.findall(FACT.format(tag=tag), doc, re.S):
        c = re.search(r'contextRef="([^"]+)"', attrs)
        if not c or c.group(1) not in ctx:
            continue
        digits = re.sub(r"[^\d.]", "", re.sub(r"<[^>]+>", "", raw))
        if not digits:
            continue
        scale = re.search(r'scale="(-?\d+)"', attrs)
        v = float(digits) * 10 ** int(scale.group(1) if scale else 0)
        if 'sign="-"' in attrs:
            v = -v
        end = ctx[c.group(1)]
        if best is None or end > best[1]:
            best = (v, end)
    return best


def status(number):
    page = get(f"/company/{number}")
    m = re.search(r'id="company-status"[^>]*>\s*([^<]+?)\s*<', page)
    return m.group(1) if m else "unknown"


def latest_accounts(number):
    page = get(f"/company/{number}/filing-history?category=accounts")
    links = re.findall(r'href="(/company/\w+/filing-history/\w+/document\?format=xhtml)', page)
    return links[0] if links else None


def main():
    rows = []
    for mid, name, number in LICENSEES:
        row = dict(id=mid, licensee_name=name, company_number=number, status=status(number),
                   period_end="", employees="", turnover_gbp_m="", note="")
        link = latest_accounts(number)
        if not link:
            row["note"] = "accounts filed as PDF only; read by hand"
        else:
            doc = get(link + "&download=1")
            ctx = contexts(doc)
            row["period_end"] = max(ctx.values(), default="")
            emp = latest_fact(doc, TAGS["employees"], ctx)
            turn = latest_fact(doc, TAGS["turnover"], ctx)
            if emp:
                row["employees"] = int(emp[0])
            if turn:
                row["turnover_gbp_m"] = round(turn[0] / 1e6, 3)
            if DORMANT.search(doc):
                row["note"] = "dormant accounts"
            else:
                row["note"] = ("headcount reported" if emp else "no headcount tag") + \
                              ("; turnover reported" if turn else "; turnover not disclosed")
        rows.append(row)
        print(row)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
