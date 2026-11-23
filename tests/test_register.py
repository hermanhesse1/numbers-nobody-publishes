import pytest

pd = pytest.importorskip("pandas")
import register
import validate


def test_changed_register_layout_is_rejected(tmp_path, monkeypatch):
    (tmp_path / "od_firme.csv").write_text("DENUMIRE^COD_INMATRICULARE\nX^J1\n", encoding="utf-8")
    monkeypatch.setattr(register, "D", tmp_path)
    with pytest.raises(validate.SchemaError, match="CUI"):
        register.read("od_firme.csv", usecols=["COD_INMATRICULARE", "CUI"])


def test_register_file_with_expected_layout_is_read(tmp_path, monkeypatch):
    (tmp_path / "od_firme.csv").write_text("﻿DENUMIRE^CUI^COD_INMATRICULARE\nX^123^J1\n", encoding="utf-8")
    monkeypatch.setattr(register, "D", tmp_path)
    df = register.read("od_firme.csv", usecols=["COD_INMATRICULARE", "CUI"])
    assert df.loc[0, "CUI"] == "123"


def test_changed_tourism_layout_is_rejected(tmp_path, monkeypatch):
    p = tmp_path / "situr.csv"
    p.write_text("TITLE\nTip unitate,Nume unitate,Rooms,CUI\nA,B,3,123\n", encoding="utf-8")
    monkeypatch.setattr(register, "SITUR", p)
    with pytest.raises(validate.SchemaError):
        register.check_rooms(pd.DataFrame(columns=["COD_INMATRICULARE", "CUI"]), set(), set(), pd.Series(dtype=str))
