"""Part 2: size estimates for the Part 1 sample (detective route).

Every figure lives in this file as an input, a source and, for proxy rows,
the arithmetic that turns proxies into a number. Running it writes
output/sample_estimates.csv, so anyone can change an assumption and see
what moves.

Run from the repo root:  python3 code/estimates.py
"""
import csv
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATCH_FILE = ROOT / "data" / "sample_matching.csv"
OUT_FILE = ROOT / "output" / "sample_estimates.csv"

# Approximate average rates for 2024 and 2025, used ONLY for the usd_m column, which
# exists to sort rows into price tiers. They are rounded and unsourced: replace
# them with ECB reference rates for each row's own period before pricing on them.
USD_PER = {"USD": 1.0, "EUR": 1.10, "GBP": 1.28, "RON": 0.22, "SGD": 0.75}


# Ages are counted from this fixed date; update it on refresh.
REFERENCE_DATE = date(2026, 11, 20)
STALE_MONTHS = 18

# (revenue date, employees date); None means the source gives no date.
AS_OF = {
    "IN-007": (date(2025, 9, 30), date(2025, 9, 30)),
    "IN-008": (date(2025, 9, 30), date(2025, 9, 30)),
    "IN-011": (date(2025, 12, 31), date(2025, 12, 31)),
    "IN-015": (date(2024, 12, 31), date(2024, 12, 31)),
    "IN-016": (date(2024, 12, 31), date(2024, 12, 31)),
    "IN-028": (date(2024, 12, 28), date(2024, 12, 28)),
    "IN-039": (date(2026, 3, 31), None),
    "IN-046": (None, None),
    "IN-049": (None, date(2025, 2, 13)),
    "IN-055": (date(2025, 12, 31), date(2025, 12, 31)),
    "IN-061": (date(2025, 12, 31), date(2025, 12, 31)),
    "IN-064": (date(2025, 12, 31), date(2025, 12, 31)),
    "IN-076": (date(2025, 3, 31), date(2023, 12, 31)),
    "IN-093": (date(2024, 12, 31), None),
    "IN-099": (date(2025, 12, 31), None),
}


def months_old(d):
    return (REFERENCE_DATE.year - d.year) * 12 + REFERENCE_DATE.month - d.month


def band(mid, low, high):
    return {"mid": mid, "low": low, "high": high}


# ---------------------------------------------------------------- proxy maths
def msc_group_revenue():
    """MSC group revenue 2024, in USD bn, as container plus cruise plus everything else.

    Container: fleet capacity times revenue per TEU of capacity at other carriers.
      2024 revenue per TEU of capacity, from each carrier's results and Alphaliner:
        Hapag-Lloyd liner shipping: $20.3bn on 2.346m TEU, about $8,650.
        Maersk Ocean: $37.4bn on 4.31m TEU, about $8,675.
        CMA CGM shipping: $36.49bn on 3.85m TEU, about $9,485.
        COSCO container shipping: $31.1bn on 3.3m TEU, about $9,425.
        ONE, year to March 2025: $19.2bn on just over 2m TEU, about $9,600.
        Evergreen: $12.7bn on an undated 1.84m TEU, about $6,900.
      The first version used only Hapag-Lloyd and Maersk. Tested on the other
      four, it under-predicted the three with reliable capacity figures by 8% to
      10%, so the rate now uses the median of all six, about $9,050, and the band
      of $7,500 to $9,600 spans them, with Evergreen's weak capacity figure
      setting the floor.
      MSC had 6.3m TEU in January 2025 after adding 0.69m during 2024, so about
      5.95m on average.
    Cruise: 4.6m passengers in 2024 times revenue per passenger. Carnival took
      $25.0bn from 13.5m passengers, about $1,850 each, and Royal Caribbean $16.5bn
      from 8.56m, about $1,930. MSC sells cheaper European cruises, so the midpoint
      is set below both at $1,700, and the $1,500 floor is an assumption.
    Other: terminals, MEDLOG road and rail logistics, Africa Global Logistics and
      car carriers. Bolloré's African operations, the core of what MSC bought as
      AGL, turned over about EUR 3.1bn in 2021 according to inforMARE, a single
      source. The rest of the slice has no source, so the band of $3.5bn to $10bn
      is wide on purpose.
    """
    teu_avg = 5.95  # million TEU
    container = band(teu_avg * 9050 / 1000, teu_avg * 7500 / 1000, teu_avg * 9600 / 1000)
    cruise = band(4.6 * 1.70, 4.6 * 1.50, 4.6 * 1.93)
    other = band(6.0, 3.5, 10.0)
    return {k: container[k] + cruise[k] + other[k] for k in ("mid", "low", "high")}


def drury_revenue():
    """Drury revenue, in USD m, as hotels x rooms x 365 x occupancy x room rate, plus 3%.

    Hotels: 130 to 150. The company says more than 150, which may include hotels
      still being built; Lodging Magazine counts 130 operating.
    Rooms per hotel: 160 to 210. A sample of 50 properties on Lodging Development
      averages 208 rooms but leans towards the newer, larger Plaza hotels; the
      160 floor is an assumption.
    Occupancy: 61% to 72%. Upper-midscale hotels ran 61.4% in Colliers' Q4 2023
      brand report, all US hotels 63.0% in 2024 according to CoStar, and Hilton's
      system 72.1% in 2024. Drury's guest-satisfaction record suggests it sits
      above its segment, so the midpoint is 66%.
    Room rate: $128 to $159. Upper midscale averaged $128.26 in Colliers' Q4 2023
      report and all US hotels $158.67 in 2024 according to CoStar.
    """
    def rev(hotels, rooms_per_hotel, occ, adr):
        return hotels * rooms_per_hotel * 365 * occ * adr * 1.03 / 1e6

    return band(rev(140, 180, 0.66, 140), rev(130, 160, 0.61, 128), rev(150, 210, 0.72, 159))


def kedny_employees():
    """Brooklyn Union Gas headcount as customers divided by customers per employee.

    No longer used for the client file, because the utility's own filing reports
    its headcount. Kept as the record of a test: how well does the proxy do on a
    company whose real figure is known?

    Customers per employee at listed US gas utilities in 2024:
      Spire: 1.74m customers and 3,475 employees, about 500.
      Atmos Energy: 3.3m customers and 5,200 employees, about 635.
      Southwest Gas: 2.26m customers and 2,435 employees, about 927.
    Tested on two other utilities, the middle ratio of 635 predicts ONE Gas at
    3,620 staff against about 3,900, and NW Natural at 1,260 against about
    1,400: 7% and 10% too low. On Brooklyn Union Gas, with 1,274,648 average
    customers in 2023, it predicts about 2,000 staff against 1,464 reported, 37%
    too high. The utility runs at about 871 customers per employee because much
    of its work is done by National Grid's shared service company.
    """
    customers = 1_274_648
    return band(customers / 635, customers / 927, customers / 500)


def margot_revenue():
    """Margot Bakery revenue, in GBP m, as 13 employees x revenue per employee.

    The 13 average employees are reported in the FY2025 micro accounts under the
    tag AverageNumberEmployeesDuringPeriod. Greggs took GBP 2.01bn in 2024 with
    about 33,000 staff, roughly GBP 61,000 each, which sets the top of the band:
    a single artisan bakery has none of Greggs' scale. The floor of GBP 35,000 and
    the midpoint of GBP 48,000 are assumptions.
    """
    return band(13 * 0.048, 13 * 0.035, 13 * 0.061)


msc = msc_group_revenue()
drury = drury_revenue()
kedny = kedny_employees()
margot = margot_revenue()

# ---------------------------------------------------------------- the rows
# basis: REPORTED (from a filing or audited report) | REPORTED_SEGMENT
#        | SELF_DECLARED (company says so, no filing) | PROXY (derived here) | NONE
ROWS = [
    dict(id="IN-007", scope="Siemens Energy AG, consolidated group",
         rev_metric="Revenue", rev_basis="REPORTED", cur="EUR", period="FY to 30 Sep 2025",
         rev=band(39100, 39100, 39100),
         emp=band(102985, 102985, 102985), emp_basis="REPORTED", emp_period="30 Sep 2025",
         source="Siemens Energy Q4 FY2025 earnings release; headcount from the FY25 ESG data factsheet",
         derivation="Read directly from the group's own release.",
         how_wrong="Exact for the group. The real risk is scope: if a local Siemens Energy company signed, these figures overstate it by one to three orders of magnitude.",
         action="Confirm which Siemens Energy company signed, and do not add IN-008 on top, because it is already inside this figure."),
    dict(id="IN-008", scope="Siemens Gamesa segment of Siemens Energy",
         rev_metric="Segment revenue", rev_basis="REPORTED_SEGMENT", cur="EUR", period="FY to 30 Sep 2025",
         rev=band(10380, 10300, 10450),
         emp=band(27300, 26000, 29000), emp_basis="PROXY", emp_period="Sep 2025",
         source="Revenue from the segment table on stockanalysis.com, whose segments sum to the EUR 39.08bn group total; headcount from Revelio Labs, 27,346 in Sep 2025, and Statista, about 28,200 in 2024",
         derivation="The segment is the closest available stand-in for the Spanish company. Headcount comes from two LinkedIn-based trackers that agree within 3%.",
         how_wrong="Revenue is within about 1% if the company equals the segment, though its own Spanish accounts may differ. Headcount is good to about 7%, and the trackers are slow to reflect layoffs.",
         action="Pull the company's consolidated accounts from the Spanish Registro Mercantil to replace both estimates."),
    dict(id="IN-011", scope="Fastenal Company, consolidated group",
         rev_metric="Net sales", rev_basis="REPORTED", cur="USD", period="FY to 31 Dec 2025",
         rev=band(8200.5, 8200.5, 8200.5),
         emp=band(24489, 24489, 24489), emp_basis="REPORTED", emp_period="31 Dec 2025",
         source="Fastenal 2025 Annual Report and 10-K",
         derivation="Read directly from the filing. This is the control case.",
         how_wrong="Exact.",
         action="None."),
    dict(id="IN-015", scope="Google Ireland Limited as a single company",
         rev_metric="Turnover", rev_basis="REPORTED", cur="EUR", period="FY to 31 Dec 2024",
         rev=band(86600, 86600, 86600),
         emp=band(4882, 4882, 4882), emp_basis="REPORTED", emp_period="2024 average",
         source="Accounts filed with the Irish CRO, as reported by the Irish Times and Irish Examiner in November 2025",
         derivation="Taken from press coverage of the filed accounts; the filing itself was not opened.",
         how_wrong="Exact as filed, but revenue is the wrong measure of size here. It is ad sales booked for Europe, the Middle East and Africa, which works out at EUR 17.7m per employee.",
         action="Price on the 4,882 employees, not on revenue."),
    dict(id="IN-016", scope="Yazaki Romania SRL, CUI 15412557, as a single company",
         rev_metric="Turnover", rev_basis="REPORTED", cur="RON", period="FY to 31 Dec 2024",
         rev=band(1095.2, 1095.2, 1095.2),
         emp=band(3623, 3249, 3623), emp_basis="REPORTED", emp_period="2024; 3,249 in 2025",
         source="Balance sheet filed with the Ministry of Finance, as shown by termene.ro, totalfirme.ro and targetare.ro, which agree; 2025 figures from termene.ro only",
         derivation="Read from the filed balance sheet through several sites that copy it. Risco.ro shows only 644 to 719 employees, which every other source contradicts, so it was discarded.",
         how_wrong="Exact for 2024. The headcount range spans the 2024 and 2025 filings, and 2025 turnover was about RON 1.14bn.",
         action="None for this company. Yazaki's two sister companies in Romania are not included."),
    dict(id="IN-028", scope="WK Kellogg Co, now owned by Ferrero",
         rev_metric="Net sales", rev_basis="REPORTED", cur="USD", period="FY to 28 Dec 2024",
         rev=band(2708, 2708, 2708),
         emp=band(3280, 3280, 3280), emp_basis="REPORTED", emp_period="28 Dec 2024",
         source="WK Kellogg FY2024 10-K, SEC CIK 1959348, and its Q4 2024 earnings release",
         derivation="Read from the last standalone 10-K. The company stopped filing once Ferrero bought it in September 2025.",
         how_wrong="Exact for FY2024. A later amendment restated cost of goods sold but not net sales. The figures are now more than a year old.",
         action="The licence now sits inside Ferrero, so check who renews it."),
    dict(id="IN-039", scope="Temasek Holdings, counting its own staff only",
         rev_metric="Net portfolio value at market value", rev_basis="REPORTED", cur="SGD", period="31 Mar 2026",
         rev=band(518000, 518000, 518000),
         emp=band(960, 900, 1000), emp_basis="SELF_DECLARED", emp_period="2025 or 2026",
         source="Temasek Review 2026 media release; Temasek careers page, which gives about 960 people in 13 offices",
         derivation="Revenue means little for an investment company, so portfolio value is given instead. Revelio Labs shows 122,763 employees because it counts the staff of portfolio companies, so it was discarded.",
         how_wrong="Portfolio value is exact. The headcount comes from an undated page and is good to about 5%.",
         action="Agree with the client whether to price on portfolio value or on staff."),
    dict(id="IN-046", scope="Greater Glasgow Health Board",
         rev_metric="Annual budget", rev_basis="SELF_DECLARED", cur="GBP", period="about 2025, undated",
         rev=band(4500, 4200, 4800),
         emp=band(40000, 38000, 44000), emp_basis="SELF_DECLARED", emp_period="about 2025, undated",
         source="NHS Scotland recruitment portal myjobscotland, which states an annual budget of GBP 4.5bn and over 40,000 staff",
         derivation="A public body has no revenue in the commercial sense, so its budget is given instead. The audited 2024/25 accounts exist on Audit Scotland's site but were not opened.",
         how_wrong="The budget is rounded and undated, so it is good to about 7%. Over 40,000 staff is a floor rather than a point.",
         action="Replace both figures with the audited 2024/25 accounts from Audit Scotland."),
    dict(id="IN-049", scope="Blue Origin, LLC and its sister companies",
         rev_metric="none", rev_basis="NONE", cur="USD", period="",
         rev=None,
         emp=band(12600, 10000, 13000), emp_basis="PROXY", emp_period="after the Feb 2025 layoffs",
         source="Reuters, via Fortune and Space.com in February 2025, reported about 14,000 staff before a cut of about 1,400; the New York Times put it near 10,000 and PitchBook near 11,000",
         derivation="14,000 less 1,400 gives 12,600. The low end of the range follows the New York Times figure.",
         how_wrong="Good to about 20%. No revenue is given because NASA milestone payments, engine sales and Jeff Bezos's funding cannot be separated in any source, so headcount is the honest measure of size.",
         action="Price on headcount, or ask the client for the contract value."),
    dict(id="IN-055", scope="FINTECH OS SRL, the Romanian company only",
         rev_metric="Turnover", rev_basis="REPORTED", cur="RON", period="FY to 31 Dec 2025",
         rev=band(89.5, 89.15, 89.5),
         emp=band(148, 148, 148), emp_basis="REPORTED", emp_period="2025",
         source="Romanian 2025 balance sheet, as reported by ZF, Profit.ro and StartupCafe",
         derivation="Taken from press coverage of the filing; ZF and Profit.ro differ by RON 0.35m.",
         how_wrong="Exact for the Romanian company. The wider group, which sells in the US and UK, is larger and does not report.",
         action="If the group signed rather than the Romanian company, these figures understate it."),
    dict(id="IN-061", scope="MARGOT BAKERY LIMITED as a single company",
         rev_metric="Revenue", rev_basis="PROXY", cur="GBP", period="FY to 31 Dec 2025",
         rev=band(margot["mid"], margot["low"], margot["high"]),
         emp=band(13, 13, 13), emp_basis="REPORTED", emp_period="FY2025 average",
         source="Micro accounts filed at Companies House for FY2023 to FY2025, whose headcount tag reads 8, 13, 13 and 13 across the years shown",
         derivation="The accounts report a headcount even though they leave out turnover. Revenue is 13 employees at GBP 35,000 to 61,000 each. The top of that band is Greggs, which took GBP 2.01bn in 2024 with about 33,000 staff; the floor is an assumption.",
         how_wrong="Revenue could be about 25% either side of the midpoint. The company is registered for property letting and shows no stock and GBP 4 in cash, so the tills may run through a sister company and the 13 staff may be all of the bakery that sits here.",
         action="None needed for tiering: with 13 staff it is a micro business either way."),
    dict(id="IN-063", scope="ALIN PANIFICATIE SRL",
         rev_metric="none", rev_basis="NONE", cur="RON", period="",
         rev=None, emp=None, emp_basis="NONE", emp_period="",
         source="No accounts filed since registration in 2022",
         derivation="There is nothing to estimate because the company has never filed accounts.",
         how_wrong="Not applicable.",
         action="Ask the client whether this licence is in use."),
    dict(id="IN-064", scope="PANIFICATIE MOLDOVA SRL, Iasi",
         rev_metric="Turnover", rev_basis="REPORTED", cur="RON", period="FY to 31 Dec 2025",
         rev=band(0.424, 0.424, 0.424),
         emp=band(0, 0, 0), emp_basis="REPORTED", emp_period="2025",
         source="Balance sheet filed with the Ministry of Finance, as shown by termene.ro; taken from Part 1 and not re-checked",
         derivation="Read from the filing.",
         how_wrong="Exact if the match holds. With no staff and profit at 80% of turnover, the income is probably rent rather than bread.",
         action="Check whether the software is still used."),
    dict(id="IN-071", scope="Brand of The Procter & Gamble Company",
         rev_metric="none", rev_basis="NONE", cur="USD", period="",
         rev=None, emp=None, emp_basis="NONE", emp_period="",
         source="A Bernstein estimate of USD 564m in brand sales from 2013, reported by AP; P&G's FY2026 net sales of USD 87.0bn",
         derivation="A brand has no staff of its own. The only estimate of brand sales is 13 years old, and P&G's group totals would overstate it about 150 times.",
         how_wrong="Not applicable.",
         action="Ask which P&G company signed, then size that company."),
    dict(id="IN-076", scope="The Brooklyn Union Gas Company, trading as National Grid NY",
         rev_metric="Operating revenues", rev_basis="REPORTED", cur="USD", period="FY to 31 Mar 2025",
         rev=band(2376.9, 2376.9, 2376.9),
         emp=band(1464, 1464, 1464), emp_basis="REPORTED", emp_period="31 Dec 2023",
         source="Revenue from Brooklyn Union Gas financial statements published by National Grid; headcount from the company's 2023 annual report to the New York Public Service Commission, page 77, Number of Gas Department Employees",
         derivation="Both figures are read from filings. An earlier version estimated headcount from customers per employee at listed gas utilities and got about 2,000, 37% too high, because much of this utility's work is done by National Grid's shared service company.",
         how_wrong="Both are exact as filed, but they cover different periods: revenue to March 2025 and headcount at December 2023. The headcount leaves out National Grid staff who work on this network from the shared service company.",
         action="Confirm which company signed, because National Grid plc would be about ten times larger."),
    dict(id="IN-086", scope="STEYN HOLDING S.à r.l., RCS B31697",
         rev_metric="none", rev_basis="NONE", cur="EUR", period="",
         rev=None, emp=None, emp_basis="NONE", emp_period="",
         source="Luxembourg Business Register: struck off on 14 Jul 2020",
         derivation="The company was struck off in July 2020, and before that it was a holding company with no operations, so it has no revenue or staff to size.",
         how_wrong="Not applicable.",
         action="Ask the client who has paid under this licence since 2020, because the signing company no longer exists."),
    dict(id="IN-093", scope="The whole MSC group owned by the Aponte family, not only the Geneva company",
         rev_metric="Revenue", rev_basis="PROXY", cur="USD", period="CY2024",
         rev=band(round(msc["mid"] * 1000, -3), round(msc["low"] * 1000, -3), round(msc["high"] * 1000, -3)),
         emp=band(200000, 180000, 220000), emp_basis="SELF_DECLARED", emp_period="2025",
         source="Fleet size from Alphaliner via Kuehne+Nagel and TradeWinds; peer figures from the 2024 results of Hapag-Lloyd, Maersk, CMA CGM, COSCO, ONE and Evergreen, with capacities from Alphaliner; cruise passengers from MSC's 2024 sustainability report; revenue per passenger from Carnival and Royal Caribbean 2024 results; Bolloré's African turnover from inforMARE; headcount from MSC's own statement of over 200,000",
         derivation="About USD 54bn from container shipping, 8bn from cruises and 6bn from terminals, logistics and everything else. Container revenue uses the median revenue per TEU of six listed carriers, after a test on four of them showed the two-carrier rate ran 8% to 10% low. A EUR 86bn figure for 2022 cited on Wikipedia fits once 2024 freight rates, about 40% lower, are allowed for.",
         how_wrong="About 20% below to 12% above. Container and cruise rest on listed peers; of the other businesses only the African logistics arm, about EUR 3bn, has any source.",
         action="Agree whether the licence covers the whole group, because the Geneva company on its own cannot be sized."),
    dict(id="IN-099", scope="Drury Hotels Company, LLC and the whole chain",
         rev_metric="Revenue", rev_basis="PROXY", cur="USD", period="2025",
         rev=band(round(drury["mid"], -1), round(drury["low"], -1), round(drury["high"], -1)),
         emp=band(6500, 6000, 7000), emp_basis="SELF_DECLARED", emp_period="about 2025",
         source="Staff and the upper hotel count from the About page on druryhotels.com, which states more than 150 hotels and over 6,500 team members; 130 operating hotels from Lodging Magazine; rooms per hotel from a sample on Lodging Development; occupancy and room rates from Colliers, CoStar and Hilton's 2024 results",
         derivation="Revenue is hotels times rooms times 365 times occupancy times average room rate. RocketReach's USD 777m was kept as a cross-check; LeadIQ's USD 5bn was discarded because it implies over USD 500 a night with every room full, against segment rates of USD 128 to 159.",
         how_wrong="Somewhere between 30% below and 55% above. Occupancy and room rate come from segment and peer figures rather than Drury's own, and even the hotel count varies between 130 and 150 by source. About 46 staff per hotel is plausible for this kind of hotel.",
         action="None needed for tiering: the chain is large under any assumption."),
]

NONE_ROWS = {
    "IN-032": ("Ambiguous in Part 1: Credit Mutuel is four separate banking groups, so it cannot be sized until the client says which one signed.",
               "Ask which Credit Mutuel group signed: Alliance Fédérale, Arkéa, Maine-Anjou Basse-Normandie or Océan."),
    "IN-067": ("Not found in Part 1. It is probably an unregistered sole trader, which German registers do not list.",
               "Ask for the town or address on the contract, which would most likely settle the match."),
    "IN-078": ("Not found in Part 1, because the name is a single common word with nothing to choose between dozens of candidates.",
               "Ask for the full counterparty name from the contract."),
    "IN-082": ("Insolvent since 2020, and its 2017 and 2018 accounts were declared void, so no credible figures exist.",
               "Ask who has paid under this licence since 2020, since Wirecard itself no longer trades."),
    "IN-087": ("Dissolved in 2019 after only ever filing dormant accounts, so its true size is zero.",
               "Check whether anyone still pays under this licence, and remove it from the list if not."),
}

COLS = ["id", "licensee_name", "matched_entity", "outcome_bucket", "size_scope",
        "revenue_metric", "revenue_basis", "currency", "period",
        "revenue_m", "revenue_low_m", "revenue_high_m", "revenue_usd_m",
        "employees", "employees_low", "employees_high", "employees_basis", "employees_period",
        "revenue_as_of", "employees_as_of", "oldest_figure_months", "age_flag",
        "sources", "derivation", "how_wrong_could_this_be", "client_action"]


def fmt(x):
    # Plain numbers with no thousands separators, so spreadsheets read them as numbers.
    if x is None:
        return ""
    return f"{x:.0f}" if abs(x) >= 100 else f"{x:.4g}"


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
                "none", "Net portfolio value at market value", "Annual budget") else None
            base.update(
                size_scope=r["scope"], revenue_metric=r["rev_metric"], revenue_basis=r["rev_basis"],
                currency=r["cur"] if rev else "", period=r["period"],
                revenue_m=fmt(rev and rev["mid"]), revenue_low_m=fmt(rev and rev["low"]),
                revenue_high_m=fmt(rev and rev["high"]), revenue_usd_m=fmt(usd),
                employees=fmt(emp and emp["mid"]), employees_low=fmt(emp and emp["low"]),
                employees_high=fmt(emp and emp["high"]), employees_basis=r["emp_basis"],
                employees_period=r["emp_period"], sources=r["source"], derivation=r["derivation"],
                how_wrong_could_this_be=r["how_wrong"], client_action=r["action"])
            rev_d, emp_d = AS_OF.get(mid, (None, None))
            rev_d = rev_d if rev else None
            emp_d = emp_d if emp else None
            dated = [d for d in (rev_d, emp_d) if d]
            undated = (rev and not rev_d) or (emp and not emp_d)
            oldest = max(months_old(d) for d in dated) if dated else None
            flags = []
            if oldest is not None and oldest > STALE_MONTHS:
                flags.append(f"older than {STALE_MONTHS} months")
            if undated:
                flags.append("a figure has no date")
            base.update(revenue_as_of=rev_d.isoformat() if rev_d else "",
                        employees_as_of=emp_d.isoformat() if emp_d else "",
                        oldest_figure_months="" if oldest is None else oldest,
                        age_flag="; ".join(flags))
        else:
            derivation, action = NONE_ROWS.get(mid, ("Not estimated.", ""))
            base.update(revenue_basis="NONE", employees_basis="NONE",
                        derivation=derivation, client_action=action)
        out.append(base)

    OUT_FILE.parent.mkdir(exist_ok=True)
    with open(OUT_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        for row in sorted(out, key=lambda r: r["id"]):
            w.writerow({c: row.get(c, "") for c in COLS})

    print(f"wrote {len(out)} rows -> {OUT_FILE.relative_to(ROOT)}")
    print(f"MSC revenue USD bn: {msc}")
    print(f"Drury revenue USD m: {drury}")
    print(f"KEDNY employees: {kedny}")
    print(f"Margot revenue GBP m: {margot}")


if __name__ == "__main__":
    main()
