"""Input checks shared by the scripts. Each raises ValueError with the offending value."""
import re
from datetime import date

CUI_KEY = "753217532"
UK_COMPANY = re.compile(r"^(\d{8}|(SC|NI|OC|SO|NC|R0|FC|BR|LP|SL|NL|SE|GE|IP|RS)\d{6})$")
ID_PATTERNS = {
    "CUI": re.compile(r"\bCUI (\d{2,10})\b"),
    "Companies House": re.compile(r"\bCompanies House (\w{8})\b"),
    "LEI": re.compile(r"\bLEI (\w{20})\b"),
    "SEC CIK": re.compile(r"\bSEC CIK (\d+)\b"),
    "UID": re.compile(r"\bUID (CHE-\d{3}\.\d{3}\.\d{3})\b"),
}


class SchemaError(ValueError):
    pass


def check_currency(code, known):
    if code not in known:
        raise ValueError(f"unknown currency {code!r}; add a rate for it first")


def check_band(mid, low, high, what="value"):
    if None in (mid, low, high):
        raise ValueError(f"{what}: range has a missing value {low}, {mid}, {high}")
    if min(mid, low, high) < 0:
        raise ValueError(f"{what}: negative value in {low}, {mid}, {high}")
    if not low <= mid <= high:
        raise ValueError(f"{what}: range out of order {low}, {mid}, {high}")


# Revenue per employee runs from about USD 0.06m at a Romanian plant to 19.5m at Google
# Ireland, a regional booking hub. A thousands-for-millions slip moves a figure 1,000 times.
USD_M_RANGE = (0.001, 1_000_000)
USD_M_PER_EMPLOYEE = (0.005, 50)


def check_revenue_scale(usd_m, employees=None, what="revenue"):
    """Reject revenue that is implausible in size, which catches figures in the wrong unit."""
    if usd_m is None or usd_m == 0:
        return
    lo, hi = USD_M_RANGE
    if not lo <= usd_m <= hi:
        raise ValueError(f"{what}: USD {usd_m}m is outside {lo} to {hi}m; check the unit")
    if employees:
        per_head = usd_m / employees
        lo, hi = USD_M_PER_EMPLOYEE
        if not lo <= per_head <= hi:
            raise ValueError(f"{what}: USD {per_head:.4f}m per employee is outside {lo} to {hi}m; "
                             "check whether revenue is in thousands or millions")


def check_as_of(d, reference, earliest=date(2000, 1, 1)):
    if d is None:
        return
    if not isinstance(d, date):
        raise ValueError(f"as-of date {d!r} is not a date")
    if d > reference:
        raise ValueError(f"as-of date {d} is after the reference date {reference}")
    if d < earliest:
        raise ValueError(f"as-of date {d} is before {earliest}")


def check_licensee_id(mid):
    if not re.fullmatch(r"IN-\d{3}", mid or ""):
        raise ValueError(f"licensee id {mid!r} is not of the form IN-000")


def check_uk_company_number(number):
    if not UK_COMPANY.match(number or ""):
        raise ValueError(f"UK company number {number!r} is not valid")


def check_cui(cui):
    """Romanian fiscal code: the last digit is a check digit over the key 753217532."""
    s = str(cui).strip().upper().removeprefix("RO")
    if not s.isdigit() or not 2 <= len(s) <= 10:
        raise ValueError(f"CUI {cui!r} is not 2 to 10 digits")
    body, control = s[:-1].zfill(9), int(s[-1])
    total = sum(int(a) * int(b) for a, b in zip(body, CUI_KEY))
    if total * 10 % 11 % 10 != control:
        raise ValueError(f"CUI {cui!r} fails its check digit")


def check_lei(lei):
    """ISO 17442: 20 characters whose mod 97 value, letters as numbers, is 1."""
    s = (lei or "").upper()
    if not re.fullmatch(r"[0-9A-Z]{18}\d{2}", s):
        raise ValueError(f"LEI {lei!r} is not 20 characters ending in two digits")
    if int("".join(str(int(ch, 36)) for ch in s)) % 97 != 1:
        raise ValueError(f"LEI {lei!r} fails its checksum")


def check_cik(cik):
    if not re.fullmatch(r"\d{1,10}", cik or ""):
        raise ValueError(f"SEC CIK {cik!r} is not up to 10 digits")


def check_swiss_uid(uid):
    digits = re.sub(r"\D", "", uid or "")
    if len(digits) != 9:
        raise ValueError(f"UID {uid!r} does not have 9 digits")
    check = 11 - sum(int(d) * w for d, w in zip(digits[:8], (5, 4, 3, 2, 7, 6, 5, 4))) % 11
    if check == 10 or check % 11 != int(digits[8]):
        raise ValueError(f"UID {uid!r} fails its check digit")


CHECKERS = {"CUI": check_cui, "Companies House": check_uk_company_number, "LEI": check_lei,
            "SEC CIK": check_cik, "UID": check_swiss_uid}


def check_registration_ids(text):
    """Validate every identifier of a known type in a registration_id cell; returns the count checked."""
    n = 0
    for kind, pattern in ID_PATTERNS.items():
        for value in pattern.findall(text or ""):
            CHECKERS[kind](value)
            n += 1
    return n


def require_columns(columns, expected, source):
    missing = [c for c in expected if c not in set(columns)]
    if missing:
        raise SchemaError(f"{source} is missing columns {missing}; the publisher may have changed its format")
