"""Part 2: size estimates for the Part 1 sample (detective route).

Every figure lives in this file as an input, a source and, for proxy rows,
the arithmetic that turns proxies into a number. Running it writes
output/sample_estimates.csv, so anyone can change an assumption and see
what moves.

Run from the repo root:  python3 code/estimates.py
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATCH_FILE = ROOT / "data" / "sample_matching.csv"
OUT_FILE = ROOT / "output" / "sample_estimates.csv"

# Approximate average rates for 2024-25, used ONLY for the usd_m column, which
# exists to sort rows into price tiers. They are rounded and unsourced: replace
# them with ECB reference rates for each row's own period before pricing on them.
USD_PER = {"USD": 1.0, "EUR": 1.10, "GBP": 1.28, "RON": 0.22, "SGD": 0.75}


def band(mid, low, high):
    return {"mid": mid, "low": low, "high": high}


# ---------------------------------------------------------------- proxy maths
def msc_group_revenue():
    """MSC group revenue 2024 (USD bn) = container + cruise + everything else.

    Container: fleet capacity x revenue per TEU of capacity at listed peers.
      Hapag-Lloyd liner 2024: $20.3bn on 2.346m TEU  -> $8,650/TEU
      Maersk Ocean 2024:      $37.4bn on ~4.3m TEU   -> ~$8,700/TEU (capacity approx.)
      MSC: 6.3m TEU in Jan 2025 after adding 0.69m during 2024 -> ~5.95m average.
      Band $7,500-9,500/TEU: MSC charters more and its rate mix is unknown.
    Cruise: 4.6m passengers (2024) x $1,500-2,200 per passenger
      (mass-market pricing, below Carnival's ~$1,850; Carnival guest count recalled, unverified).
    Other (terminals, MEDLOG, AGL Africa logistics, car carriers): $5-15bn.
      Pure assumption, and the weakest piece of the sum.
    """
    teu_avg = 5.95  # million TEU
    container = band(teu_avg * 8650 / 1000, teu_avg * 7500 / 1000, teu_avg * 9500 / 1000)
    cruise = band(4.6 * 1.80, 4.6 * 1.50, 4.6 * 2.20)
    other = band(9.0, 5.0, 15.0)
    return {k: container[k] + cruise[k] + other[k] for k in ("mid", "low", "high")}


def drury_revenue():
    """Drury revenue (USD m) = rooms x 365 x occupancy x ADR, plus ~3% other.

    Hotels: 150 ("more than 150", company About page).
    Rooms per hotel: 160-210. A partial sample of 50 properties averages 208
      rooms (Lodging Development), biased towards the newer, larger Plaza hotels.
    Occupancy 70-80%, ADR $125-155: upper-midscale segment norms. These are
      assumptions to be checked against STR data, not sourced figures.
    """
    def rev(rooms_per_hotel, occ, adr):
        return 150 * rooms_per_hotel * 365 * occ * adr * 1.03 / 1e6

    return band(rev(180, 0.75, 140), rev(160, 0.70, 125), rev(210, 0.80, 155))


def kedny_employees():
    """Brooklyn Union Gas headcount = customers / customers-per-employee.

    Customers: 1.20-1.30m, our assumed share of the 1.9m that the NY PSC reports
      for KEDNY and KEDLI together. The split is not sourced.
    Customers per employee: 450-950, the range at US gas utilities (Spire, Atmos,
      Southwest Gas). Peer ratios are recalled and need checking in their 10-Ks.
      A dense, unionised urban network sits at the low (more staff) end.
    """
    return band(1.25e6 / 650, 1.20e6 / 950, 1.30e6 / 450)


def margot_revenue():
    """Margot Bakery revenue (GBP m) = 13 employees x revenue per employee.

    13 average employees is REPORTED in the FY2025 micro accounts (iXBRL tag
    AverageNumberEmployeesDuringPeriod). Revenue per employee for a UK artisan
    bakery-cafe is assumed at GBP 35-70k (mid 50k); check against ONS ABS for
    SIC 10.71 / 56.10.
    """
    return band(13 * 0.050, 13 * 0.035, 13 * 0.070)


msc = msc_group_revenue()
drury = drury_revenue()
kedny = kedny_employees()
margot = margot_revenue()

# ---------------------------------------------------------------- the rows
# basis: REPORTED (from a filing or audited report) | REPORTED_SEGMENT
#        | SELF_DECLARED (company says so, no filing) | PROXY (derived here) | NONE
ROWS = [
    dict(id="IN-007", scope="Group (Siemens Energy AG, consolidated)",
         rev_metric="Revenue", rev_basis="REPORTED", cur="EUR", period="FY to 30 Sep 2025",
         rev=band(39100, 39100, 39100),
         emp=band(102985, 102985, 102985), emp_basis="REPORTED", emp_period="30 Sep 2025",
         source="Siemens Energy Q4 FY2025 earnings release; FY25 ESG data factsheet (headcount)",
         derivation="Read from the group's own release.",
         how_wrong="Exact for the group. The real risk is scope: if a local Siemens Energy company signed, group figures overstate it by 1-3 orders of magnitude.",
         action="Confirm which Siemens Energy company signed. Do not add IN-008 on top: it is inside this figure."),
    dict(id="IN-008", scope="Siemens Gamesa segment of Siemens Energy",
         rev_metric="Segment revenue", rev_basis="REPORTED_SEGMENT", cur="EUR", period="FY to 30 Sep 2025",
         rev=band(10380, 10300, 10450),
         emp=band(27300, 26000, 29000), emp_basis="PROXY", emp_period="Sep 2025",
         source="Revenue: segment table via stockanalysis.com (segments sum to the EUR 39.08bn group total). Employees: Revelio Labs 27,346 (Sep 2025); Statista ~28,200 (2024)",
         derivation="The segment is the closest proxy for the S.A. Headcount comes from two LinkedIn-based trackers that agree within 3%.",
         how_wrong="Revenue: within 1% if the S.A. equals the segment, but the S.A.'s own Spanish accounts may differ. Employees: +/-7%; the trackers lag layoffs.",
         action="Pull the S.A.'s consolidated accounts from the Registro Mercantil to replace both proxies."),
    dict(id="IN-011", scope="Group (Fastenal Company)",
         rev_metric="Net sales", rev_basis="REPORTED", cur="USD", period="FY to 31 Dec 2025",
         rev=band(8200.5, 8200.5, 8200.5),
         emp=band(24489, 24489, 24489), emp_basis="REPORTED", emp_period="31 Dec 2025",
         source="Fastenal 2025 Annual Report and 10-K",
         derivation="Read from the filing. Control case.",
         how_wrong="Exact.",
         action="None."),
    dict(id="IN-015", scope="Entity (Google Ireland Limited)",
         rev_metric="Turnover", rev_basis="REPORTED", cur="EUR", period="FY to 31 Dec 2024",
         rev=band(86600, 86600, 86600),
         emp=band(4882, 4882, 4882), emp_basis="REPORTED", emp_period="2024 average",
         source="CRO accounts as reported by the Irish Times and Irish Examiner (Nov 2025)",
         derivation="Read from press coverage of the filed accounts; the CRO document itself was not opened.",
         how_wrong="Exact as filed, but revenue is the wrong size measure: it is ad sales booked for all of EMEA (EUR 17.7m per employee). Use headcount.",
         action="Price on employees (4,882), not revenue."),
    dict(id="IN-016", scope="Entity (Yazaki Romania SRL, CUI 15412557)",
         rev_metric="Turnover", rev_basis="REPORTED", cur="RON", period="FY to 31 Dec 2024",
         rev=band(1095.2, 1095.2, 1095.2),
         emp=band(3623, 3249, 3623), emp_basis="REPORTED", emp_period="2024 (3,249 in 2025)",
         source="Ministry of Finance balance sheet via termene.ro, totalfirme.ro and targetare.ro (agree); 2025 from termene.ro only",
         derivation="Read from the filed balance sheet, mirrored by several aggregators. Risco.ro shows 644-719 employees; discarded as an outlier that every other source contradicts.",
         how_wrong="Exact for 2024. The employee range spans the 2024 and 2025 filings (2025 turnover ~RON 1.14bn).",
         action="None for this entity. The two sister Yazaki companies in Romania are not included."),
    dict(id="IN-028", scope="Entity (WK Kellogg Co, now owned by Ferrero)",
         rev_metric="Net sales", rev_basis="REPORTED", cur="USD", period="FY to 28 Dec 2024",
         rev=band(2708, 2708, 2708),
         emp=band(3280, 3280, 3280), emp_basis="REPORTED", emp_period="28 Dec 2024",
         source="WK Kellogg FY2024 10-K (SEC CIK 1959348) and Q4 2024 earnings release",
         derivation="Read from the last standalone 10-K. The company stopped filing after Ferrero bought it (Sep 2025).",
         how_wrong="Exact for FY2024. A 10-K/A restated cost of goods sold, not net sales. Figures are more than a year old.",
         action="Licence now sits inside Ferrero: check who renews it."),
    dict(id="IN-039", scope="Entity (Temasek Holdings), own staff only",
         rev_metric="Net portfolio value (mark-to-market)", rev_basis="REPORTED", cur="SGD", period="31 Mar 2026",
         rev=band(518000, 518000, 518000),
         emp=band(960, 900, 1000), emp_basis="SELF_DECLARED", emp_period="2025-26",
         source="Temasek Review 2026 media release; Temasek careers page (~960 people, 13 offices)",
         derivation="Revenue is not meaningful for an investment company, so portfolio value is reported instead. Revelio Labs shows 122,763 'employees': discarded, because it counts portfolio-company staff as Temasek staff.",
         how_wrong="Portfolio value is exact. Headcount is +/-5% (an undated page).",
         action="Agree with the client whether to price on portfolio value or staff."),
    dict(id="IN-046", scope="Health board (Greater Glasgow Health Board)",
         rev_metric="Annual budget", rev_basis="SELF_DECLARED", cur="GBP", period="c. 2025 (undated)",
         rev=band(4500, 4200, 4800),
         emp=band(40000, 38000, 44000), emp_basis="SELF_DECLARED", emp_period="c. 2025 (undated)",
         source="NHS Scotland recruitment portal (myjobscotland): 'annual budget of GBP 4.5bn and over 40,000 staff'",
         derivation="A public body has no revenue, so its budget is reported instead. The 2024/25 audited accounts exist (Audit Scotland) but were not opened.",
         how_wrong="Budget +/-7%: the figure is rounded and undated. Headcount: 'over 40,000' gives a floor, not a point.",
         action="Replace with the 2024/25 audited accounts (Audit Scotland)."),
    dict(id="IN-049", scope="Blue Origin, LLC (and the group's sister LLCs)",
         rev_metric="none", rev_basis="NONE", cur="USD", period="",
         rev=None,
         emp=band(12600, 10000, 13000), emp_basis="PROXY", emp_period="after Feb 2025 layoffs",
         source="Reuters via Fortune/Space.com (Feb 2025): ~14,000 staff before a ~1,400 cut. NYT ~10,000; PitchBook ~11,000",
         derivation="14,000 - 1,400 = 12,600. The low end of the range takes the NYT figure.",
         how_wrong="+/-20%. No revenue is given: what exists is NASA milestone payments, engine sales and Bezos funding, and no source separates them. Headcount is the honest size measure.",
         action="Price on headcount, or ask the client for contract value."),
    dict(id="IN-055", scope="Entity (FINTECH OS SRL, Romania) only",
         rev_metric="Turnover", rev_basis="REPORTED", cur="RON", period="FY to 31 Dec 2025",
         rev=band(89.5, 89.15, 89.5),
         emp=band(148, 148, 148), emp_basis="REPORTED", emp_period="2025",
         source="Romanian 2025 balance sheet as reported by ZF, Profit.ro and StartupCafe",
         derivation="Read from press coverage of the filing. The two outlets differ by RON 0.35m.",
         how_wrong="Exact for the Romanian company. The group (US and UK sales) is larger and unreported.",
         action="If the group signed, the Romanian figures understate it."),
    dict(id="IN-061", scope="Entity (MARGOT BAKERY LIMITED)",
         rev_metric="Revenue", rev_basis="PROXY", cur="GBP", period="FY to 31 Dec 2025",
         rev=band(margot["mid"], margot["low"], margot["high"]),
         emp=band(13, 13, 13), emp_basis="REPORTED", emp_period="FY2025 average",
         source="Companies House iXBRL micro accounts FY2023-25 (tag AverageNumberEmployeesDuringPeriod: 8 -> 13 -> 13 -> 13)",
         derivation="Headcount is filed even though turnover is not. Revenue = 13 x GBP 35-70k per employee.",
         how_wrong="Revenue +/-40%. Caveat: SIC code is property letting, there is no stock, and cash is GBP 4. The tills may run through a sister company, so the 13 staff may be the only part of the bakery in this entity.",
         action="None needed for tiering: 13 staff is micro either way."),
    dict(id="IN-063", scope="Entity (ALIN PANIFICATIE SRL)",
         rev_metric="none", rev_basis="NONE", cur="RON", period="",
         rev=None, emp=None, emp_basis="NONE", emp_period="",
         source="No accounts filed since registration (2022)",
         derivation="Nothing to estimate: the company has never filed accounts.",
         how_wrong="n/a",
         action="Ask the client whether this licence is in use."),
    dict(id="IN-064", scope="Entity (PANIFICATIE MOLDOVA SRL, Iasi)",
         rev_metric="Turnover", rev_basis="REPORTED", cur="RON", period="FY to 31 Dec 2025",
         rev=band(0.424, 0.424, 0.424),
         emp=band(0, 0, 0), emp_basis="REPORTED", emp_period="2025",
         source="Ministry of Finance balance sheet via termene.ro (from Part 1; not re-checked in this pass)",
         derivation="Read from the filing.",
         how_wrong="Exact if the match holds. With 0 staff and profit at 80% of turnover, this is probably rental income, not bread.",
         action="Check whether the software is still used."),
    dict(id="IN-071", scope="Brand of The Procter & Gamble Company",
         rev_metric="none", rev_basis="NONE", cur="USD", period="",
         rev=None, emp=None, emp_basis="NONE", emp_period="",
         source="Bernstein estimate of USD 564m brand sales (2013, via AP); P&G FY2026 net sales USD 87.0bn",
         derivation="A brand has no staff. The only brand-sales estimate is 13 years old, and P&G group totals would overstate it ~150x.",
         how_wrong="n/a",
         action="Ask which P&G company signed, then size that company."),
    dict(id="IN-076", scope="Entity (The Brooklyn Union Gas Company, d/b/a National Grid NY)",
         rev_metric="Operating revenues", rev_basis="REPORTED", cur="USD", period="FY to 31 Mar 2025",
         rev=band(2376.9, 2376.9, 2376.9),
         emp=band(round(kedny["mid"], -1), round(kedny["low"], -1), round(kedny["high"], -1)), emp_basis="PROXY", emp_period="2025",
         source="Revenue: Brooklyn Union Gas financial statements published by National Grid. Employees: derived (see code)",
         derivation="Employees = 1.20-1.30m customers / 450-950 customers per employee. The only published headcount (3,651) is decades old: discarded.",
         how_wrong="Revenue exact. Employees: the range is roughly 0.65-1.5x the midpoint, and both inputs are assumptions.",
         action="Confirm the signing entity. National Grid plc would be ~10x larger."),
    dict(id="IN-086", scope="Entity (STEYN HOLDING S.a r.l., RCS B31697)",
         rev_metric="none", rev_basis="NONE", cur="EUR", period="",
         rev=None, emp=None, emp_basis="NONE", emp_period="",
         source="Eulerpool lists the status as 'lapsed' (last update Dec 2020)",
         derivation="A holding company with no operations has no meaningful revenue or staff. New finding: it may also no longer exist, which contradicts the Part 1 status 'Unknown'.",
         how_wrong="n/a",
         action="Check the RCS status; if active, size it by total assets from the LBR filings."),
    dict(id="IN-093", scope="MSC group (all companies under the Aponte family), not just the Geneva SA",
         rev_metric="Revenue", rev_basis="PROXY", cur="USD", period="CY2024",
         rev=band(round(msc["mid"] * 1000, -3), round(msc["low"] * 1000, -3), round(msc["high"] * 1000, -3)),
         emp=band(200000, 180000, 220000), emp_basis="SELF_DECLARED", emp_period="2025",
         source="Fleet: Alphaliner via Kuehne+Nagel and TradeWinds. Peers: Hapag-Lloyd and Maersk 2024 reports. Cruise passengers: MSC 2024 sustainability report. Employees: MSC ('200,000+')",
         derivation="Container (~$51bn) + cruise (~$8bn) + other (~$9bn). Cross-check: a Wikipedia-cited EUR 86bn for 2022, a peak-freight year, fits once 2024 rates are about 40% lower.",
         how_wrong="About -20% to +20%. The 'other' slice is a pure assumption.",
         action="Agree whether the licence covers the group. The Geneva SA alone is unknowable."),
    dict(id="IN-099", scope="Drury Hotels Company, LLC (whole chain)",
         rev_metric="Revenue", rev_basis="PROXY", cur="USD", period="2025",
         rev=band(round(drury["mid"], -1), round(drury["low"], -1), round(drury["high"], -1)),
         emp=band(6500, 6000, 7000), emp_basis="SELF_DECLARED", emp_period="c. 2025",
         source="Hotels and staff: druryhotels.com About page ('more than 150 hotels', 'over 6,500 team members'); rooms sample: Lodging Development",
         derivation="Revenue = hotels x rooms x 365 x occupancy x ADR. Database estimates: RocketReach $777m (kept as a sanity check); LeadIQ $5bn discarded, because it implies ~$500k per room per year.",
         how_wrong="About -25% to +35%. Occupancy and ADR are assumptions; the hotel count is firm. 43 staff per hotel is plausible for this format.",
         action="None for tiering: large under any assumption."),
]

NONE_ROWS = {
    "IN-032": "AMBIGUOUS in Part 1: four separate Credit Mutuel banking groups. Cannot size until the client names one.",
    "IN-067": "NO_MATCH in Part 1.",
    "IN-078": "NO_MATCH in Part 1: a single common word.",
    "IN-082": "Insolvent since 2020; the 2017-18 accounts were declared void. No credible figures exist.",
    "IN-087": "Dissolved in 2019 after filing only dormant accounts. True size is zero.",
}

COLS = ["id", "licensee_name", "matched_entity", "outcome_bucket", "size_scope",
        "revenue_metric", "revenue_basis", "currency", "period",
        "revenue_m", "revenue_low_m", "revenue_high_m", "revenue_usd_m",
        "employees", "employees_low", "employees_high", "employees_basis", "employees_period",
        "sources", "derivation", "how_wrong_could_this_be", "client_action"]


def fmt(x):
    if x is None:
        return ""
    return f"{x:,.0f}" if abs(x) >= 100 else f"{x:,.3g}"


def main():
    with open(MATCH_FILE, newline="", encoding="utf-8") as f:
        matches = {r["id"]: r for r in csv.DictReader(f)}

    out = []
    by_id = {r["id"]: r for r in ROWS}
    for mid, m in matches.items():
        base = dict(id=mid, licensee_name=m["licensee_name"],
                    matched_entity=m["matched_entity"], outcome_bucket=m["outcome_bucket"])
        if mid in by_id:
            r = by_id[mid]
            rev, emp = r["rev"], r["emp"]
            usd = rev["mid"] * USD_PER[r["cur"]] if rev and r["rev_metric"] not in (
                "none", "Net portfolio value (mark-to-market)", "Annual budget") else None
            base.update(
                size_scope=r["scope"], revenue_metric=r["rev_metric"], revenue_basis=r["rev_basis"],
                currency=r["cur"] if rev else "", period=r["period"],
                revenue_m=fmt(rev and rev["mid"]), revenue_low_m=fmt(rev and rev["low"]),
                revenue_high_m=fmt(rev and rev["high"]), revenue_usd_m=fmt(usd),
                employees=fmt(emp and emp["mid"]), employees_low=fmt(emp and emp["low"]),
                employees_high=fmt(emp and emp["high"]), employees_basis=r["emp_basis"],
                employees_period=r["emp_period"], sources=r["source"], derivation=r["derivation"],
                how_wrong_could_this_be=r["how_wrong"], client_action=r["action"])
        else:
            base.update(revenue_basis="NONE", employees_basis="NONE",
                        derivation=NONE_ROWS.get(mid, "Not estimated."))
        out.append(base)

    OUT_FILE.parent.mkdir(exist_ok=True)
    with open(OUT_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        for row in out:
            w.writerow({c: row.get(c, "") for c in COLS})

    print(f"wrote {len(out)} rows -> {OUT_FILE.relative_to(ROOT)}")
    print(f"MSC revenue USD bn: {msc}")
    print(f"Drury revenue USD m: {drury}")
    print(f"KEDNY employees: {kedny}")
    print(f"Margot revenue GBP m: {margot}")


if __name__ == "__main__":
    main()
