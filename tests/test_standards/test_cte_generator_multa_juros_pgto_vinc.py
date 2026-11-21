"""CT-e ICMS45, multa e juros (NT 2026.004 v1.01) and pgtoVinc (NT 2026.001).

XSD-validating tests against the bundled CT-e schema (`[Verified locally]`).
"""

from __future__ import annotations

import pytest
from lxml import etree
from pydantic import ValidationError

from mcp_nfe_br.models.cte import BRCteICMS45, BRCteImp, BRCteMultaJuros
from mcp_nfe_br.models.invoice import BRPgtoVinc
from mcp_nfe_br.standards.cte_generator import CTeGenerator
from mcp_nfe_br.utils.cte_access_key import build_cte_access_key
from mcp_nfe_br.validators.cte_xsd import CTeXSDValidator
from tests.conftest import make_cte

_NS = {"c": "http://www.portalfiscal.inf.br/cte"}
_EMIT_CNPJ = "11222333000181"
_OTHER_CNPJ = "11444777000161"


def _ref_key(cnpj: str = _EMIT_CNPJ, **overrides: str) -> str:
    data = {
        "cuf": "35",
        "dh_emi": "2026-06-01T10:00:00-03:00",
        "cnpj": cnpj,
        "serie": "1",
        "n_ct": "5",
        "tp_emis": "1",
        "c_ct": "12345678",
    }
    data.update(overrides)
    return build_cte_access_key(**data)


def _validate(xml: str) -> None:
    result = CTeXSDValidator().validate(xml)
    assert result.valid is True, result.errors


def _icms41() -> BRCteICMS45:
    return BRCteICMS45(cst="41")


def _pgto(**overrides: str) -> BRPgtoVinc:
    data = {
        "id_transacao": "TX-0001",
        "tp_meio_pgto": "01",
        "cnpj_receb": _EMIT_CNPJ,
        "cnpj_base_psp": "11222333",
    }
    data.update(overrides)
    return BRPgtoVinc(**data)


# --- ICMS45 ----------------------------------------------------------------


@pytest.mark.parametrize("cst", ["40", "41", "51"])
def test_icms45_validates(cst: str) -> None:
    xml = CTeGenerator().generate(make_cte(imp=BRCteImp(icms=BRCteICMS45(cst=cst))))
    _validate(xml)
    root = etree.fromstring(xml.encode())
    assert root.find(".//c:imp/c:ICMS/c:ICMS45/c:CST", _NS).text == cst


def test_icms45_with_desoneracao_pair_validates() -> None:
    icms = BRCteICMS45(cst="40", v_icms_deson="10.00", c_benef="SP123456")
    _validate(CTeGenerator().generate(make_cte(imp=BRCteImp(icms=icms))))


def test_icms45_deson_and_benef_must_come_together() -> None:
    with pytest.raises(ValidationError, match="em conjunto"):
        BRCteICMS45(cst="40", v_icms_deson="10.00")


def test_icms45_rejects_other_cst() -> None:
    with pytest.raises(ValidationError):
        BRCteICMS45(cst="00")


# --- gMultaJuros -----------------------------------------------------------


def _multa_juros_cte(key: str, **overrides: object):
    data = {
        "imp": BRCteImp(icms=_icms41()),
        "g_multa_juros": BRCteMultaJuros(ch_cte_ref=key),
    }
    data.update(overrides)
    return make_cte(**data)


def test_multa_juros_validates_and_is_last_child_of_ide() -> None:
    key = _ref_key()
    xml = CTeGenerator().generate(_multa_juros_cte(key))
    _validate(xml)
    root = etree.fromstring(xml.encode())
    ide = root.find(".//c:ide", _NS)
    assert etree.QName(ide[-1]).localname == "gMultaJuros"
    assert ide.find("c:gMultaJuros/c:chCTeRef", _NS).text == key


def test_multa_juros_requires_icms_cst_41_rv_1072() -> None:
    with pytest.raises(ValidationError, match="RV 1072"):
        _multa_juros_cte(_ref_key(), imp=BRCteImp(icms=BRCteICMS45(cst="40")))


def test_multa_juros_rejects_icms00_rv_1072() -> None:
    with pytest.raises(ValidationError, match="RV 1072"):
        make_cte(g_multa_juros=BRCteMultaJuros(ch_cte_ref=_ref_key()))


def test_multa_juros_rejects_wrong_check_digit_rv_1073() -> None:
    key = _ref_key()
    bad = key[:-1] + ("0" if key[-1] != "0" else "1")
    with pytest.raises(ValidationError, match="DV inválido"):
        _multa_juros_cte(bad)


def test_multa_juros_rejects_other_model_rv_1073() -> None:
    key = _ref_key()
    other_model = key[:20] + "67" + key[22:43]
    from mcp_nfe_br.utils.access_key import access_key_check_digit

    bad = other_model + access_key_check_digit(other_model)
    with pytest.raises(ValidationError, match="Modelo diferente de 57"):
        _multa_juros_cte(bad)


def test_multa_juros_rejects_other_emitter_rv_1078() -> None:
    with pytest.raises(ValidationError, match="RV 1078"):
        _multa_juros_cte(_ref_key(cnpj=_OTHER_CNPJ))


# --- pgtoVinc --------------------------------------------------------------


def test_pgto_vinc_validates_and_sits_between_imp_and_inf_cte_norm() -> None:
    xml = CTeGenerator().generate(
        make_cte(pgto_vinc=[_pgto(), _pgto(id_transacao="TX-0002", tp_meio_pgto="15")])
    )
    _validate(xml)
    root = etree.fromstring(xml.encode())
    names = [etree.QName(c).localname for c in root.find(".//c:infCte", _NS)]
    assert names.index("imp") + 1 == names.index("pgtoVinc") == names.index("infCTeNorm") - 1
    pgtos = root.findall(".//c:pgtoVinc/c:pgto", _NS)
    assert [p.get("nPag") for p in pgtos] == ["1", "2"]
    assert [p.get("idTransacao") for p in pgtos] == ["TX-0001", "TX-0002"]


def test_pgto_vinc_rejects_invalid_cnpj_receb_rule_01() -> None:
    with pytest.raises(ValidationError, match=r"1001"):
        make_cte(pgto_vinc=[_pgto(cnpj_receb="11222333000182")])


def test_pgto_vinc_rejects_repeated_id_transacao() -> None:
    with pytest.raises(ValidationError, match="idTransacao repetido"):
        make_cte(pgto_vinc=[_pgto(), _pgto()])


def test_pgto_vinc_limited_to_99_entries() -> None:
    items = [_pgto(id_transacao=f"TX-{n:04d}") for n in range(100)]
    with pytest.raises(ValidationError):
        make_cte(pgto_vinc=items)
