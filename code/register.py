"""Part 5: how many Romanian register companies would the best Part 2 proxy reach?

The proxy is physical capacity times revenue per unit of capacity at listed
peers. Part 2 used it for MSC, with container slots, and for Drury, with hotel
rooms. It only works where a company's size is a countable asset that the
public can see, so the line is drawn on activity codes.

The line, step by step:
  1. Living: the company carries status 1048, "funcţiune" or operating, and no
     status meaning dead, dying or dormant, matched by keyword against the
     official list of status codes.
  2. Capacity activity: the authorised CAEN codes in CAPACITY below, each with
     the unit that would be counted.
  3. Inside the line: capacity codes make up at least half of the company's
     authorised codes. The register lists authorised activities with no main
     activity flag, so this is the stand-in for "this is what the company does".
     Two bounds are printed alongside: companies with a single code that is a
     capacity code, and companies with a capacity code anywhere in their list.
  4. Industry: the capacity group holding most of the company's capacity codes.

Inputs, not committed, downloaded from data.gov.ro into big_data/register/:
  od_firme.csv, od_stare_firma.csv, od_caen_autorizat.csv,
  nomenclator_stari_firma.csv

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

# Capacity groups: CAEN codes from the 2008 and 2025 revisions, the unit counted,
# and where that unit could be observed. Only accommodation and shipping were
# tested in Part 2; the other groups extend the same recipe untested.
GROUPS = {
    "Accommodation": (["5510", "5520", "5530", "5590"], "rooms or beds"),
    "Restaurants and bars": (["5610", "5611", "5630"], "seats or tables"),
    "Road transport": (["4931", "4932", "4933", "4939", "4941"], "licensed vehicles"),
    "Rail transport": (["4910", "4911", "4912", "4920"], "rolling stock"),
    "Water transport": (["5010", "5020", "5030", "5040"], "vessels"),
    "Air transport": (["5110", "5121"], "aircraft"),
    "Warehousing": (["5210"], "floor area"),
    "Hospitals": (["8610"], "beds"),
}
CAPACITY = {code: group for group, (codes, _) in GROUPS.items() for code in codes}


def read(name, **kw):
    return pd.read_csv(D / name, sep="^", dtype=str, encoding="utf-8-sig",
                       keep_default_na=False, on_bad_lines="skip", **kw)


def main():
    # --- living companies --------------------------------------------------
    nom = pd.read_csv(D / "nomenclator_stari_firma.csv", sep="|", dtype=str, encoding="cp1250")
    dead_codes = set(nom.loc[nom["DENUMIRE"].str.lower().apply(
        lambda s: any(w in s for w in DEAD_WORDS)), "COD"])

    st = read("od_stare_firma.csv")
    by_co = st.groupby("COD_INMATRICULARE")["COD"].agg(set)
    living_mask = by_co.apply(lambda s: OPERATING in s and not s & dead_codes)
    doubtful = by_co.apply(lambda s: bool(s & set(DOUBTFUL)))

    firme = read("od_firme.csv", usecols=["COD_INMATRICULARE"])
    in_firme = set(firme["COD_INMATRICULARE"])
    living = set(by_co.index[living_mask]) & in_firme
    n_living = len(living)

    # --- authorised activities --------------------------------------------
    # Rev.2 codes where a company has them; companies with only Rev.3 (2025)
    # codes are read from those instead.
    caen = read("od_caen_autorizat.csv")
    caen = caen[caen["COD_INMATRICULARE"].isin(living) & caen["VER_CAEN_AUTORIZAT"].isin(["2", "3"])]
    has_rev2 = set(caen.loc[caen["VER_CAEN_AUTORIZAT"] == "2", "COD_INMATRICULARE"])
    caen = caen[(caen["VER_CAEN_AUTORIZAT"] == "2") | ~caen["COD_INMATRICULARE"].isin(has_rev2)].copy()
    caen["group"] = caen["COD_CAEN_AUTORIZAT"].map(CAPACITY)

    per_co = caen.groupby("COD_INMATRICULARE").agg(
        n_codes=("COD_CAEN_AUTORIZAT", "size"), n_cap=("group", "count"))
    any_cap = per_co[per_co["n_cap"] > 0]
    single = per_co[(per_co["n_codes"] == 1) & (per_co["n_cap"] == 1)]
    inside = per_co[per_co["n_cap"] / per_co["n_codes"] >= 0.5]

    # Industry: the capacity group holding most of the company's capacity codes.
    cap = caen[caen["COD_INMATRICULARE"].isin(inside.index) & caen["group"].notna()]
    main_group = (cap.groupby(["COD_INMATRICULARE", "group"]).size()
                  .reset_index(name="n").sort_values(["COD_INMATRICULARE", "n"], ascending=[True, False])
                  .drop_duplicates("COD_INMATRICULARE").set_index("COD_INMATRICULARE")["group"])
    top = main_group.value_counts()

    n_in = len(inside)
    n_doubt = int(doubtful.reindex(inside.index).fillna(False).sum())
    print(f"register companies with a status:           {len(by_co):,}")
    print(f"living, operating with no dead status:      {n_living:,}")
    print(f"  with at least one authorised activity:    {len(per_co):,}")
    print(f"inside the line, capacity >= half of codes: {n_in:,} = {n_in / n_living:.1%} of living")
    print(f"  lower bound, single capacity code only:   {len(single):,} = {len(single) / n_living:.1%}")
    print(f"  upper bound, any capacity code:           {len(any_cap):,} = {len(any_cap) / n_living:.1%}")
    print(f"  inside but flagged doubtful (2069/2065):  {n_doubt:,} -> without them {n_in - n_doubt:,}")
    print("industries inside the line, by main capacity group:")
    for g, n in top.items():
        print(f"  {g:22} {n:>8,}  {n / n_in:5.1%}  counted in {GROUPS[g][1]}")


if __name__ == "__main__":
    main()
