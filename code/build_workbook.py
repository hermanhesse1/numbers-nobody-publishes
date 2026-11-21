"""Build the client workbook from output/sample_estimates.csv.

Run from the repo root after code/estimates.py:  python3 code/build_workbook.py
"""
import csv
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "output" / "sample_estimates.csv"
OUT = ROOT / "output" / "licensee_sizes.xlsx"

FONT = "Arial"
HEAD = PatternFill("solid", fgColor="1F3864")
TIERS = ["Micro", "Small", "Medium", "Large", "Enterprise"]
STAFF_EDGES = [10, 50, 250, 5000]
USD_M_EDGES = [2, 10, 50, 1500]
FIRM = {"REPORTED", "REPORTED_SEGMENT"}


def num(s):
    return float(s) if s not in ("", None) else None


def tier(v, edges):
    if v is None:
        return None
    for name, edge in zip(TIERS, edges):
        if v < edge:
            return name
    return TIERS[-1]


def size(r):
    if r["outcome_bucket"] == "MATCHED_INACTIVE":
        return "Not operating", "", "None"
    staff = [num(r[k]) for k in ("employees", "employees_low", "employees_high")]
    if staff[0] is not None:
        basis, vals, b = "Headcount", staff, r["employees_basis"]
    elif num(r["revenue_usd_m"]) is not None:
        usd = num(r["revenue_usd_m"])
        f = usd / num(r["revenue_m"]) if num(r["revenue_m"]) else 1
        vals = [usd, num(r["revenue_low_m"]) * f, num(r["revenue_high_m"]) * f]
        basis, b = "Revenue", r["revenue_basis"]
        return finish(basis, [tier(v, USD_M_EDGES) for v in vals], b)
    else:
        return "Cannot size", "", "None"
    return finish(basis, [tier(v, STAFF_EDGES) for v in vals], b)


def finish(basis, tiers, b):
    mid, low, high = tiers
    if low != high:
        return f"{low} to {high}", basis, "Low"
    return mid, basis, "High" if b in FIRM else "Medium"


def style_header(ws, row, ncols):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.font = Font(name=FONT, bold=True, color="FFFFFF")
        cell.fill = HEAD
        cell.alignment = Alignment(wrap_text=True, vertical="top")


def body(ws, widths, wrap_cols=()):
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.font = Font(name=FONT)
            cell.alignment = Alignment(wrap_text=cell.column in wrap_cols, vertical="top")
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "C2"


def main():
    rows = list(csv.DictReader(open(SRC, encoding="utf-8")))
    wb = Workbook()

    ws = wb.active
    ws.title = "Summary"
    head = ["ID", "Licensee as written", "Matched entity", "Match outcome", "Size tier", "Tier based on",
            "Confidence", "Headcount", "Revenue, USD m", "Data age warning", "Action for the client"]
    ws.append(head)
    for r in rows:
        t, basis, conf = size(r)
        ws.append([r["id"], r["licensee_name"], r["matched_entity"] or "No match",
                   r["outcome_bucket"].replace("_", " ").capitalize(), t, basis, conf,
                   num(r["employees"]), num(r["revenue_usd_m"]), r["age_flag"], r["client_action"]])
    style_header(ws, 1, len(head))
    body(ws, [8, 30, 34, 18, 18, 13, 11, 12, 14, 26, 60], wrap_cols={2, 3, 10, 11})
    for row in ws.iter_rows(min_row=2):
        row[7].number_format = "#,##0"
        row[8].number_format = "#,##0.0"

    wd = wb.create_sheet("Full data")
    cols = list(rows[0].keys())
    numeric = {"revenue_m", "revenue_low_m", "revenue_high_m", "revenue_usd_m", "employees",
               "employees_low", "employees_high", "oldest_figure_months"}
    wd.append([c.replace("_", " ").capitalize() for c in cols])
    for r in rows:
        wd.append([num(r[c]) if c in numeric else r[c] for c in cols])
    style_header(wd, 1, len(cols))
    widths = [16 if c in numeric else 40 if c in ("sources", "derivation", "how_wrong_could_this_be", "client_action") else 20 for c in cols]
    body(wd, widths, wrap_cols={i + 1 for i, c in enumerate(cols) if c not in numeric})
    for row in wd.iter_rows(min_row=2):
        for cell, c in zip(row, cols):
            if c in numeric:
                cell.number_format = "#,##0.###"

    wh = wb.create_sheet("How to read")
    text = [
        ("How to read this workbook", True),
        ("", False),
        ("Summary gives one line per licensee: its size tier, how sure we are, and what to do next. Full data holds every figure with its range, sources, derivation and dates.", False),
        ("", False),
        ("Size tiers", True),
        ("Tiers use headcount where we have it, following the EU SME bands: Micro under 10 staff, Small 10 to 49, Medium 50 to 249. Above that, Large is 250 to 4,999 staff and Enterprise is 5,000 or more, a split we added.", False),
        ("Where there is no headcount, tiers use revenue in US dollars: Micro under $2m, Small under $10m, Medium under $50m, Large under $1.5bn, Enterprise above.", False),
        ("A tier such as \"Large to Enterprise\" means the range around the figure crosses a tier boundary.", False),
        ("", False),
        ("Confidence", True),
        ("High: read from a filing, and the whole range sits in one tier.", False),
        ("Medium: an estimate or a figure the company states about itself, with the whole range in one tier.", False),
        ("Low: the range crosses a tier boundary.", False),
        ("None: we could not size the licensee, or it no longer operates; the action column says what to do.", False),
        ("", False),
        ("Figures and dates", True),
        ("Revenue is in millions of the currency shown; the USD column uses rounded average rates and is for ranking only. Each figure has an as-of date, and a warning appears when a figure is more than 18 months old or undated.", False),
        ("A size describes the matched entity named in each row. If a different company signed the contract, the size may not apply, which is why several actions ask which entity signed.", False),
    ]
    for line, bold in text:
        wh.append([line])
        wh.cell(row=wh.max_row, column=1).font = Font(name=FONT, bold=bold, size=12 if bold else 11)
        wh.cell(row=wh.max_row, column=1).alignment = Alignment(wrap_text=True, vertical="top")
    wh.column_dimensions["A"].width = 110

    wb.move_sheet("How to read", offset=-2)
    wb.active = 1
    wb.save(OUT)
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
