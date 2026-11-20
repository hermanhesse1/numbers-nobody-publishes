"""Part 5: how many Romanian register companies would the best Part 2 proxy reach?

The proxy is the average headcount a company reports in its annual accounts
(Part 2: UK iXBRL `AverageNumberEmployeesDuringPeriod`; the Romanian equivalent
is the employee line on the balance sheet filed with the Ministry of Finance).

The line, step by step:
  1. Living: the company carries status 1048 ("funcţiune", operating) and no
     status that means dead, dying or dormant (keyword list below).
  2. Inside the proxy: its legal form is one that must file annual accounts with
     an employee count. Sole traders and family businesses (PFA, II, IF, PF, AF)
     file a personal tax return instead, so they sit outside the line.
  3. Industry: the division (first two digits) of the company's first-listed
     CAEN Rev.2 authorised activity. The register lists authorised activities,
     not a declared main activity, so this is an approximation.

Inputs (not committed; download from data.gov.ro into big_data/register/):
  od_firme.csv, od_stare_firma.csv, od_caen_autorizat.csv,
  nomenclator_stari_firma.csv, nomenclator_caen.csv

Run from the repo root:  python3 code/register.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "big_data" / "register"

OPERATING = "1048"
# A status whose description contains any of these words disqualifies the company.
DEAD_WORDS = ["radiat", "dizolv", "lichid", "faliment", "insolv", "întrerupere temporară",
              "suspendare activ", "nulitate", "perimat", "respins", "tribunal",
              "85/2014", "85/2006", "64/1995", "fuziune prin absorb", "divizare totală",
              "radiere", "încetat activitatea", "dispărut", "organe statutare",
              "interzicere desfăşurare", "înmatriculare suspendată", "în curs de înmatriculare",
              "rezerv", "nu funcţionează la sediu"]
DOUBTFUL = {"2069": "registered office expired", "2065": "directors' mandate expired"}

FILES_ACCOUNTS = {"SRL", "SA", "SNC", "SCS", "SCA", "SC", "CA", "RA", "GIE", "GEIE",
                  "SE", "SCE", "INCD", "OC", "OC1", "OC2", "OC3", "OC5", "OC7",
                  "OCC", "OCM", "OCR"}
TAX_RETURN_ONLY = {"PFA", "II", "IF", "PF", "AF"}

# CAEN Rev.2 division names, only for the divisions printed in the results.
DIVISION_NAMES = {
    "01": "Crop and animal production", "41": "Construction of buildings",
    "43": "Specialised construction", "45": "Motor vehicle trade and repair",
    "46": "Wholesale trade", "47": "Retail trade", "49": "Land transport",
    "56": "Food and beverage service", "62": "Computer programming and consultancy",
    "68": "Real estate", "69": "Legal and accounting", "70": "Head offices and management consultancy",
    "71": "Architecture and engineering", "73": "Advertising and market research",
    "74": "Other professional activities", "82": "Office and business support",
    "86": "Human health", "96": "Other personal services",
}


def read(name, **kw):
    return pd.read_csv(D / name, sep="^", dtype=str, encoding="utf-8-sig",
                       keep_default_na=False, on_bad_lines="skip", **kw)


def main():
    # --- statuses ---------------------------------------------------------
    nom = pd.read_csv(D / "nomenclator_stari_firma.csv", sep="|", dtype=str, encoding="cp1250")
    nom["dead"] = nom["DENUMIRE"].str.lower().apply(lambda s: any(w in s for w in DEAD_WORDS))
    dead_codes = set(nom.loc[nom["dead"], "COD"])

    st = read("od_stare_firma.csv")
    by_co = st.groupby("COD_INMATRICULARE")["COD"].agg(set)
    operating = by_co.apply(lambda s: OPERATING in s)
    blocked = by_co.apply(lambda s: bool(s & dead_codes))
    doubtful = by_co.apply(lambda s: bool(s & set(DOUBTFUL)))
    living = by_co.index[operating & ~blocked]

    # --- legal form -------------------------------------------------------
    firme = read("od_firme.csv", usecols=["COD_INMATRICULARE", "FORMA_JURIDICA"])
    firme = firme.drop_duplicates("COD_INMATRICULARE")
    total_register = len(by_co)
    alive = firme[firme["COD_INMATRICULARE"].isin(living)]
    inside = alive[alive["FORMA_JURIDICA"].isin(FILES_ACCOUNTS)]
    excluded_forms = alive["FORMA_JURIDICA"].value_counts()

    # --- industry ---------------------------------------------------------
    # Codes are stored in ascending order and there is no "main activity" flag,
    # so a company is counted in every division where it holds an authorised
    # activity. Rev.2 codes are used; companies with only Rev.3 (2025) codes fall
    # back to those (the two revisions share most 2-digit divisions).
    caen = read("od_caen_autorizat.csv")
    caen = caen[caen["COD_INMATRICULARE"].isin(set(inside["COD_INMATRICULARE"]))]
    caen = caen[caen["VER_CAEN_AUTORIZAT"].isin(["2", "3"])].copy()
    caen["div"] = caen["COD_CAEN_AUTORIZAT"].str[:2]
    has_rev2 = set(caen.loc[caen["VER_CAEN_AUTORIZAT"] == "2", "COD_INMATRICULARE"])
    use = caen[(caen["VER_CAEN_AUTORIZAT"] == "2") | ~caen["COD_INMATRICULARE"].isin(has_rev2)]
    pairs = use[["COD_INMATRICULARE", "div"]].drop_duplicates()
    top = pairs["div"].value_counts()
    n_coded = pairs["COD_INMATRICULARE"].nunique()
    n_rev3_only = n_coded - len(has_rev2)

    n_alive, n_in = len(alive), len(inside)
    n_doubt = int(doubtful[inside["COD_INMATRICULARE"]].sum())
    print(f"register companies (with a status row):  {total_register:,}")
    print(f"living (1048 and no dead/dormant status): {n_alive:,} "
          f"(of which {len(living) - n_alive:,} living codes missing from od_firme)")
    print(f"inside the proxy line:                    {n_in:,} = {n_in / n_alive:.1%} of living")
    print(f"  of which flagged doubtful (2069/2065):  {n_doubt:,}  -> without them {n_in - n_doubt:,}")
    print("living companies by legal form (top 10):")
    for form, n in excluded_forms.head(10).items():
        tag = "inside" if form in FILES_ACCOUNTS else ("tax return only" if form in TAX_RETURN_ONLY else "outside")
        print(f"  {form or '(blank)':6} {n:>9,}  {tag}")
    print(f"companies inside the line with an authorised activity: {n_coded:,} "
          f"({n_rev3_only:,} Rev.3 only); with none: {n_in - n_coded:,}")
    print("top industries inside the line (companies authorised in each division; one company can count in several):")
    for d, n in top.head(6).items():
        print(f"  {d} {DIVISION_NAMES.get(d, '?'):42} {n:>9,}  {n / n_in:.1%} of inside")


if __name__ == "__main__":
    main()
