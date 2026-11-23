from datetime import date
from pathlib import Path

import pytest

import ixbrl

FIXTURES = Path(__file__).parent / "fixtures"
HEAD = (b'<html xmlns="http://www.w3.org/1999/xhtml" xmlns:ix="http://www.xbrl.org/2013/inlineXBRL" '
        b'xmlns:xbrli="http://www.xbrl.org/2003/instance" xmlns:core="urn:core" xmlns:bus="urn:bus">'
        b'<xbrli:context id="c"><xbrli:period><xbrli:instant>2025-03-31</xbrli:instant></xbrli:period></xbrli:context>')


def doc(body):
    return HEAD + body + b"</html>"


def micro():
    return ixbrl.parse((FIXTURES / "micro.html").read_bytes())


def test_latest_period_headcount_wins_over_prior_year():
    assert micro().latest("AverageNumberEmployeesDuringPeriod").value == 13


def test_dimensioned_context_is_ignored():
    f = micro()
    assert f.period_end() == date(2025, 12, 31)
    assert f.latest("AverageNumberEmployeesDuringPeriod").context == "cur"


def test_scale_sign_and_zero_formats():
    f = micro()
    assert f.first("Creditors").value == pytest.approx(1_234_500)
    assert f.first("ProfitLoss").value == -2000
    assert f.first("Provisions").value == 0


def test_not_dormant():
    assert micro().is_dormant() is False


def test_dormant_flag():
    f = ixbrl.parse(doc(b'<ix:nonNumeric name="bus:EntityDormantTruefalse" contextRef="c">true</ix:nonNumeric>'))
    assert f.is_dormant()


def test_negative_scale_on_headcount_is_kept_as_displayed():
    f = ixbrl.parse(doc(b'<ix:nonFraction name="core:AverageNumberEmployeesDuringPeriod" contextRef="c" '
                        b'unitRef="pure" scale="-2">52</ix:nonFraction>'))
    fact = f.first("AverageNumberEmployeesDuringPeriod")
    assert fact.value == pytest.approx(0.52)
    assert fact.shown == 52 and fact.scale == -2


def test_single_quotes_and_unprefixed_elements():
    body = (b"<ix:nonFraction name='core:AverageNumberEmployeesDuringPeriod' contextRef='c' unitRef='pure'>4</ix:nonFraction>"
            b'<nonFraction xmlns="http://www.xbrl.org/2013/inlineXBRL" name="core:Turnover" contextRef="c" unitRef="GBP">900</nonFraction>')
    f = ixbrl.parse(doc(body))
    assert f.first("AverageNumberEmployeesDuringPeriod").value == 4
    assert f.first("Turnover").value == 900


def test_decimal_text_is_not_inflated():
    f = ixbrl.parse(doc(b'<ix:nonFraction name="core:AverageNumberEmployeesDuringPeriod" contextRef="c" '
                        b'format="ixt:numdotdecimal">1.00</ix:nonFraction>'))
    assert f.first("AverageNumberEmployeesDuringPeriod").value == 1


def test_comma_decimal_format():
    assert ixbrl.parse_number("1.234,5", "ixt:numcommadecimal") == 1234.5
    assert ixbrl.parse_number("1,234.5", "ixt2:numdotdecimal") == 1234.5


def test_nil_value_is_missing_not_zero():
    f = ixbrl.parse(doc(b'<ix:nonFraction xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" '
                        b'name="core:Turnover" contextRef="c"></ix:nonFraction>'))
    assert f.first("Turnover").value is None
    assert f.latest("Turnover") is None


def test_text_without_digits_is_missing():
    f = ixbrl.parse(doc(b'<ix:nonFraction name="core:Turnover" contextRef="c">n/a</ix:nonFraction>'))
    assert f.first("Turnover").value is None


def test_malformed_markup_is_recovered():
    f = ixbrl.parse(doc(b'<p><b>unclosed<ix:nonFraction name="core:AverageNumberEmployeesDuringPeriod" '
                        b'contextRef="c">7</ix:nonFraction></p>'))
    assert f.recovered
    assert f.first("AverageNumberEmployeesDuringPeriod").value == 7


@pytest.mark.parametrize("data", [b"%PDF-1.7 binary", b"", b"<html><body>Plain page</body></html>",
                                  b'<xbrl xmlns="http://www.xbrl.org/2003/instance"></xbrl>'])
def test_unexpected_formats_raise(data):
    with pytest.raises(ixbrl.FilingFormatError):
        ixbrl.parse(data)


def test_2008_namespace_is_read():
    data = (b'<html xmlns:ix="http://www.xbrl.org/2008/inlineXBRL" xmlns:xbrli="http://www.xbrl.org/2003/instance">'
            b'<xbrli:context id="c"><xbrli:period><xbrli:instant>2016-03-31</xbrli:instant></xbrli:period></xbrli:context>'
            b'<ix:nonFraction name="uk-gaap:AverageNumberEmployeesDuringPeriod" contextRef="c">3</ix:nonFraction></html>')
    assert ixbrl.parse(data).first("AverageNumberEmployeesDuringPeriod").value == 3
