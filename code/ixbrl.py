"""Minimal inline XBRL reader for UK Companies House accounts, built on lxml."""
from dataclasses import dataclass, field
from datetime import date

from lxml import etree

IX_NAMESPACES = {"http://www.xbrl.org/2013/inlineXBRL", "http://www.xbrl.org/2008/inlineXBRL"}
XBRLI = "http://www.xbrl.org/2003/instance"
XBRLDI = "http://xbrl.org/2006/xbrldi"
XSI_NIL = "{http://www.w3.org/2001/XMLSchema-instance}nil"
ZERO_FORMATS = ("zerodash", "fixed-zero", "numdash")
COMMA_DECIMAL = ("commadecimal", "comma-decimal", "numdotcomma", "numspacecomma")


class FilingFormatError(ValueError):
    pass


@dataclass
class Fact:
    name: str
    context: str
    value: object
    numeric: bool
    shown: object = None
    scale: int = 0


@dataclass
class Filing:
    facts: list = field(default_factory=list)
    contexts: dict = field(default_factory=dict)
    recovered: bool = False

    def values(self, *names):
        return [f for f in self.facts if f.name in names]

    def first(self, *names):
        found = self.values(*names)
        return found[0] if found else None

    def latest(self, *names):
        """The fact for the latest undimensioned period, or None."""
        best = None
        for f in self.values(*names):
            ctx = self.contexts.get(f.context)
            if not ctx or ctx["dimensioned"] or ctx["end"] is None or f.value is None:
                continue
            if best is None or ctx["end"] > self.contexts[best.context]["end"]:
                best = f
        return best

    def period_end(self):
        ends = [c["end"] for c in self.contexts.values() if c["end"] and not c["dimensioned"]]
        return max(ends) if ends else None

    def is_dormant(self):
        for f in self.facts:
            if f.name == "EntityDormantTruefalse" and str(f.value).strip().lower() == "true":
                return True
            if f.name.endswith("RelatingToDormantCompanies"):
                return True
        return False


def local(tag):
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def namespace(tag):
    return tag[1:].split("}", 1)[0] if isinstance(tag, str) and tag.startswith("{") else ""


def parse_number(text, fmt="", scale=None, sign=None, nil=False):
    if nil:
        return None
    fmt = (fmt or "").lower()
    text = (text or "").strip()
    if any(z in fmt for z in ZERO_FORMATS) or text in ("-", "\u2013", "\u2014"):
        return 0.0
    decimal = "," if any(k in fmt for k in COMMA_DECIMAL) else "."
    keep = "".join(ch for ch in text if ch.isdigit() or ch == decimal)
    if not any(ch.isdigit() for ch in keep):
        raise ValueError(f"no digits in numeric fact {text!r}")
    value = float(keep.replace(decimal, ".")) * 10 ** int(scale or 0)
    return -value if sign == "-" else value


def parse_date(text):
    try:
        return date.fromisoformat(text.strip()[:10])
    except (AttributeError, ValueError):
        return None


def parse(data):
    """Parse one iXBRL document from bytes. Raises FilingFormatError if it is not iXBRL."""
    if not data or not data.lstrip()[:1] == b"<":
        raise FilingFormatError("not an XML or HTML document")
    parser = etree.XMLParser(recover=True, huge_tree=True, resolve_entities=False, no_network=True)
    root = etree.fromstring(data, parser)
    if root is None:
        raise FilingFormatError("document could not be parsed")
    filing = Filing(recovered=bool(parser.error_log))
    if not any(ns in IX_NAMESPACES for ns in root.nsmap.values()):
        raise FilingFormatError("no inline XBRL namespace")

    for ctx in root.iter(f"{{{XBRLI}}}context"):
        ends = [parse_date(e.text) for e in ctx.iter(f"{{{XBRLI}}}endDate", f"{{{XBRLI}}}instant")]
        ends = [e for e in ends if e]
        dims = any(namespace(e.tag) == XBRLDI for e in ctx.iter())
        filing.contexts[ctx.get("id")] = {"end": max(ends) if ends else None, "dimensioned": dims}

    for el in root.iter():
        if namespace(el.tag) not in IX_NAMESPACES or local(el.tag) not in ("nonFraction", "nonNumeric"):
            continue
        name = el.get("name", "").split(":")[-1]
        text = "".join(el.itertext())
        if local(el.tag) == "nonFraction":
            nil = el.get(XSI_NIL) == "true"
            try:
                scale = int(el.get("scale") or 0)
                value = parse_number(text, el.get("format"), scale, el.get("sign"), nil)
                shown = parse_number(text, el.get("format"), 0, el.get("sign"), nil)
            except ValueError:
                scale, value, shown = 0, None, None
            filing.facts.append(Fact(name, el.get("contextRef"), value, True, shown, scale))
        else:
            filing.facts.append(Fact(name, el.get("contextRef"), text.strip(), False))
    return filing
