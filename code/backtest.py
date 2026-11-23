"""How often do the proxy ranges contain the true figure on companies that report?

Each proxy is rebuilt the way Part 2 builds it, applied to a company whose real
figure is known, and scored on whether the range holds the truth and how far
the point is off. Inputs are the ones documented in code/estimates.py.

Run from the repo root:  python3 code/backtest.py
"""
from statistics import median

# Shipping: 2024 revenue in USD bn and fleet capacity in million TEU.
CARRIERS = {
    "Hapag-Lloyd": (20.3, 2.346),
    "Maersk": (37.4, 4.31),
    "CMA CGM": (36.49, 3.85),
    "COSCO": (31.1, 3.3),
    "ONE": (19.2, 2.0),
    "Evergreen": (12.7, 1.84),
}

# Gas utilities: customers and reported staff; ratio band from Spire, Atmos and Southwest Gas.
GAS_RATIOS = (500, 635, 927)
UTILITIES = {
    "ONE Gas": (2_300_000, 3900),
    "NW Natural": (800_000, 1400),
    "Brooklyn Union Gas": (1_274_648, 1464),
}

# Hotels: rooms and 2024 revenue in USD m, priced with Drury's occupancy and rate band.
HOTEL_INPUTS = {"low": (0.61, 128), "mid": (0.66, 140), "high": (0.75, 159)}
HOTELS = {
    "Apple Hospitality": (29_764, 1430),
    "Summit": (14_553, 732),
}


def shipping():
    out = []
    rates = {k: rev / teu for k, (rev, teu) in CARRIERS.items()}
    for name, (rev, teu) in CARRIERS.items():
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
        return rooms * 365 * occ * adr * 1.11 / 1e6
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
