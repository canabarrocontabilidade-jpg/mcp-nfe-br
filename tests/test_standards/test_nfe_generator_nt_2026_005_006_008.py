"""NF-e/NFC-e: NT 2026.005 (Simples Nacional), NT 2026.006 (vinculação de pagamento) and
NT 2026.008 (valor líquido), schema package PL_010h_v1.03."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from mcp_nfe_br.models.invoice import (
    BRGrupoCBSSN,
    BRGrupoIBSCBS,
    BRGrupoIBSCBSTot,
    BRGrupoIBSSN,
    BRGrupoTribSN,
    BRGrupoTribSNTot,
    BRPgtoVinc,
)
from mcp_nfe_br.standards.nfe_generator import NFeGenerator
from mcp_nfe_br.validators.nfe_xsd import NFeXSDValidator
from tests.conftest import make_emitente, make_line, make_nfe


def _valid(xml: str) -> None:
    result = NFeXSDValidator().validate(xml)
    assert result.valid is True, result.errors


def test_valor_liquido_validates_against_xsd() -> None:
    nfe = make_nfe(
        lines=[make_line(v_un_com_liq="90.00", v_prod_liq="90.00")],
        v_prod_liq_tot="90.00",
    )
    xml = NFeGenerator().generate(nfe)
    assert "<vUnComLiq>90</vUnComLiq><vProdLiq>90.00</vProdLiq>" in xml
    assert xml.index("<vProdLiqTot>") < xml.index("<ICMSTot>")
    _valid(xml)


def test_valor_liquido_rules() -> None:
    with pytest.raises(ValidationError, match="I11a"):
        make_nfe(lines=[make_line(v_prod_liq="90.00")], v_prod_liq_tot="90.00")
    with pytest.raises(ValidationError, match="1279"):
        make_nfe(
            lines=[make_line(v_un_com_liq="90.00", v_prod_liq="80.00")], v_prod_liq_tot="80.00"
        )
    with pytest.raises(ValidationError, match="1282"):
        make_nfe(lines=[make_line(v_un_com_liq="90.00", v_prod_liq="90.00")])
    with pytest.raises(ValidationError, match="1283"):
        make_nfe(
            lines=[make_line(v_un_com_liq="90.00", v_prod_liq="90.00")], v_prod_liq_tot="95.00"
        )


def test_tp_regime_ibscbs_and_cativsn_validate_against_xsd() -> None:
    nfe = make_nfe(
        emitente=make_emitente(crt="3", tp_regime_ibscbs="4"),
        lines=[make_line(c_ativ_sn="01")],
    )
    xml = NFeGenerator().generate(nfe)
    assert "<CRT>3</CRT><tpRegimeIBSCBS>4</tpRegimeIBSCBS>" in xml
    assert "<indTot>1</indTot><cAtivSN>01</cAtivSN>" in xml
    _valid(xml)


def test_tp_regime_ibscbs_vs_crt() -> None:
    with pytest.raises(ValidationError, match="2026.005"):
        make_emitente(crt="1", tp_regime_ibscbs="3")
    with pytest.raises(ValidationError, match="2026.005"):
        make_emitente(crt="3", tp_regime_ibscbs="1")
    with pytest.raises(ValidationError):
        make_line(c_ativ_sn="07")


def _sn_group() -> BRGrupoTribSN:
    return BRGrupoTribSN(
        g_ibssn=BRGrupoIBSSN(p_ibssn="0.10", v_ibssn="0.10"),
        g_cbssn=BRGrupoCBSSN(p_cbssn="0.90", v_cbssn="0.90"),
    )


def test_trib_sn_totals_rules_and_serialization() -> None:
    line = make_line(ibs_cbs=BRGrupoIBSCBS(cst="000", c_class_trib="000001", g_trib_sn=_sn_group()))
    tot = BRGrupoIBSCBSTot(g_trib_sn=BRGrupoTribSNTot(v_ibssn="0.10", v_cbssn="0.90"))
    nfe = make_nfe(lines=[line], ibscbs_tot=tot)
    xml = NFeGenerator().generate(nfe)
    assert "<gTribSN><gIBSSN><pIBSSN>0.1000</pIBSSN><vIBSSN>0.10</vIBSSN></gIBSSN>" in xml
    assert "<gCBSSN><pCBSSN>0.9000</pCBSSN><vCBSSN>0.90</vCBSSN></gCBSSN></gTribSN>" in xml

    with pytest.raises(ValidationError, match="1275"):
        make_nfe(lines=[line])
    with pytest.raises(ValidationError, match="1276"):
        make_nfe(ibscbs_tot=tot)
    with pytest.raises(ValidationError, match="1277"):
        make_nfe(
            lines=[line],
            ibscbs_tot=BRGrupoIBSCBSTot(g_trib_sn=BRGrupoTribSNTot(v_ibssn="0.20", v_cbssn="0.90")),
        )
    with pytest.raises(ValidationError, match="1284"):
        make_nfe(
            lines=[line],
            ibscbs_tot=BRGrupoIBSCBSTot(g_trib_sn=BRGrupoTribSNTot(v_ibssn="0.10", v_cbssn="1.00")),
        )


def test_pgto_vinc_validates_against_xsd() -> None:
    nfe = make_nfe(
        g_pgto_vinc=[
            BRPgtoVinc(
                id_transacao="TX-0001",
                tp_meio_pgto="17",
                cnpj_receb="11222333000181",
                cnpj_base_psp="11222333",
            ),
            BRPgtoVinc(
                id_transacao="TX-0002",
                tp_meio_pgto="15",
                cnpj_receb="11222333000181",
                cnpj_base_psp="11222333",
            ),
        ]
    )
    xml = NFeGenerator().generate(nfe)
    assert '<gPgto nPag="1" idTransacao="TX-0001">' in xml
    assert xml.index("</pag>") < xml.index("<gPgtoVinc>")
    _valid(xml)


def test_pgto_vinc_rejects_duplicate_transaction_id() -> None:
    p = BRPgtoVinc(
        id_transacao="TX-0001",
        tp_meio_pgto="17",
        cnpj_receb="11222333000181",
        cnpj_base_psp="11222333",
    )
    with pytest.raises(ValidationError, match="YC04-20"):
        make_nfe(g_pgto_vinc=[p, p])
