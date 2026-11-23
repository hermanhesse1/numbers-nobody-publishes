"""How often do the proxy ranges contain the true figure on companies that report?

Each proxy is rebuilt the way Part 2 builds it, applied to a company whose real
figure is known, and scored on whether the range holds the truth and how far
the point is off. Inputs come from data/proxy_inputs.csv and data/proxy_tests.csv.

Run from the repo root:  python3 code/backtest.py
"""
import csv
from pathlib import Path
from statistics import median

from estimates import load_inputs
from validate import require_columns

ROOT = Path(__file__).resolve().parents[1]
TESTS_FILE = ROOT / "data" / "proxy_tests.csv"


def load_tests(path=TESTS_FILE):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        require_columns(reader.fieldnames, ["proxy", "company", "driver", "actual", "source"], path.name)
        out = {}
        for r in reader:
            out.setdefault(r["proxy"], {})[r["company"]] = (float(r["driver"]), float(r["actual"]))
    return out


TESTS = load_tests()
P = load_inputs()
CARRIERS = TESTS["shipping"]
UTILITIES = TESTS["gas"]
HOTELS = TESTS["hotels"]
GAS = P["kedny", "customers_per_employee"]
GAS_RATIOS = (GAS["low"], GAS["mid"], GAS["high"])
HOTEL_INPUTS = {k: (P["drury", "occupancy"][k], P["drury", "room_rate"][k]) for k in ("low", "mid", "high")}
OTHER_SHARE = P["drury", "other_revenue_share"]["mid"]


def shipping():
    out = []
    rates = {k: rev / teu for k, (teu, rev) in CARRIERS.items()}
    for name, (teu, rev) in CARRIERS.items():
        others = [r for k, r in rates.items() if k != name]
        out.append(("Shipping, revenue per TEU", name, median(others) * teu,
                    min(others) * teu, max(others) * teu, rev))
    return out


def gas():
    lo_r, mid_r, hi_r = GAS_RATIOS
    return [("Gas, customers per employee", name, c / mid_r, c / hi_r, c / lo_r, staff)
            for name, (c, staff) in UTILITIES.items()]


def hotels():
    def rev(rooms, occ, adr):
        return rooms * 365 * occ * adr * (1 + OTHER_SHARE) / 1e6
    return [("Hotels, rooms x occupancy x rate", name, rev(rooms, *HOTEL_INPUTS["mid"]),
             rev(rooms, *HOTEL_INPUTS["low"]), rev(rooms, *HOTEL_INPUTS["high"]), actual)
            for name, (rooms, actual) in HOTELS.items()]


def main():
    cases = shipping() + gas() + hotels()
    inside = 0
    errors = []
    print(f"{'proxy':34} {'company':20} {'low':>9} {'point':>9} {'high':>9} {'actual':>9}  error  in range")
    for proxy, name, point, low, high, actual in cases:
        ok = low <= actual <= high
        inside += ok
        err = point / actual - 1
        errors.append(abs(err))
        print(f"{proxy:34} {name:20} {low:9,.1f} {point:9,.1f} {high:9,.1f} {actual:9,.1f}  {err:+5.0%}  {'yes' if ok else 'no'}")
    print(f"\nranges holding the true figure: {inside} of {len(cases)} = {inside / len(cases):.0%}")
    print(f"median absolute error of the point: {median(errors):.0%}")


if __name__ == "__main__":
    main()
