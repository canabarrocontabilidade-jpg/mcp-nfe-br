"""Tests for CT-e (modelo 57) XML generation (roadmap BR-CTE-8)."""

from __future__ import annotations

import pytest
from lxml import etree
from mcp_einvoicing_core import DocumentGenerationError

from mcp_nfe_br.models.cte import (
    BRCteALCZFMCBS,
    BRCteCBS,
    BRCteIBSCBS,
    BRCteIBSMun,
    BRCteIBSUF,
    BRCteImp,
    BRCteImpIBSCBS,
    BRCteInfModal,
    BRCteTomador,
    CTeModal,
    CTeTomadorPapel,
)
from mcp_nfe_br.standards.cte_generator import CTeGenerator
from mcp_nfe_br.validators.cte_xsd import CTeXSDValidator
from tests.conftest import make_cte, make_cte_emitente, make_cte_remetente, make_endereco

_NAMESPACE = "http://www.portalfiscal.inf.br/cte"


def test_generate_produces_infcte_with_id() -> None:
    xml = CTeGenerator().generate(make_cte())
    root = etree.fromstring(xml.encode("utf-8"))
    assert root.tag == f"{{{_NAMESPACE}}}CTe"
    inf_cte = root[0]
    assert inf_cte.tag == f"{{{_NAMESPACE}}}infCte"
    assert inf_cte.get("Id").startswith("CTe")
    assert len(inf_cte.get("Id")) == len("CTe") + 44


def test_generate_unsigned_document_validates_against_xsd() -> None:
    xml = CTeGenerator().generate(make_cte())
    result = CTeXSDValidator().validate(xml)
    assert result.valid is True, result.errors
    assert "unsigned variant" in result.metadata["schema_version"]


def test_generate_rejects_non_cte_document() -> None:
    with pytest.raises(DocumentGenerationError, match="BRCTeDocument"):
        CTeGenerator().generate(object())  # type: ignore[arg-type]


def test_generate_rejects_unsupported_modal() -> None:
    cte = make_cte(
        modal=CTeModal.AEREO,
        inf_modal=BRCteInfModal(modal=CTeModal.AEREO, rntrc=None),
    )
    with pytest.raises(DocumentGenerationError, match="rodoviário"):
        CTeGenerator().generate(cte)


def test_generate_rejects_mismatched_chave_acesso() -> None:
    cte = make_cte(chave_acesso="0" * 44)
    with pytest.raises(DocumentGenerationError, match="chave de acesso"):
        CTeGenerator().generate(cte)


def test_generate_ibscbs_and_pag_antecipado_validate_against_xsd() -> None:
    """Reforma Tributária do Consumo, NT 2026.002 (closes GitHub issue
    cmendezs/mcp-nfe-br#5) — `imp/IBSCBS`, `emit/ISUFEmit`, and
    `ide/tpPagAnt`+`gPagAntecipado` validate against the schema package
    upgraded to `PL_CTe_400_NT2026.002 RTC_1.00.zip`."""
    zfm = make_endereco(c_mun="1302603", x_mun="Manaus", uf="AM")
    cte = make_cte(
        c_mun_ini="1302603",
        x_mun_ini="Manaus",
        uf_ini="AM",
        c_mun_fim="1302603",
        x_mun_fim="Manaus",
        uf_fim="AM",
        emitente=make_cte_emitente(isuf_emit="12345678", endereco=zfm),
        remetente=make_cte_remetente(endereco=zfm),
        tomador=BRCteTomador(papel=CTeTomadorPapel.REMETENTE, ind_ie_toma="1"),
        imp=BRCteImp(
            icms=make_cte().imp.icms,
            ibscbs=BRCteImpIBSCBS(
                cst="000",
                c_class_trib="000001",
                g_ibscbs=BRCteIBSCBS(
                    v_bc="100.00",
                    g_ibsuf=BRCteIBSUF(p_ibsuf="0.10", v_ibsuf="0.10"),
                    g_ibsmun=BRCteIBSMun(p_ibsmun="0.00", v_ibsmun="0.00"),
                    v_ibs="0.10",
                    g_cbs=BRCteCBS(
                        p_cbs="0.00",
                        g_alczfmcbs=BRCteALCZFMCBS(
                            p_aliq_efet_reg_cbs="0.90", v_trib_reg_cbs="0.90"
                        ),
                        v_cbs="0.00",
                    ),
                ),
            ),
        ),
        tp_pag_ant="3",
        pag_antecipado=["35070111222333" + "0" * 30],
    )
    xml = CTeGenerator().generate(cte)
    assert "<ISUFEmit>12345678</ISUFEmit>" in xml
    assert "<IBSCBS>" in xml
    assert "<gPagAntecipado>" in xml

    result = CTeXSDValidator().validate(xml)
    assert result.valid is True, result.errors


def test_generate_nt_2026_004_005_fields_validate_against_xsd() -> None:
    """NT 2026.004 v1.01 (`vTPrestLiq`, `vTotDFe`, `chDFePagAnt`) and NT 2026.005 v1.00
    (`emit/tpRegimeIBSCBS`, `imp/IBSCBS/gTribSN`) validate against the schema package
    `PL_CTe_400_NT2026.005 RTC SN_1.00_corr.zip`."""
    from mcp_nfe_br.models.cte import BRCteGCBSSN, BRCteGIBSSN, BRCteTribSN, BRCteVPrest

    key = "35070111222333" + "0" * 30
    cte = make_cte(
        emitente=make_cte_emitente(crt="1"),
        v_prest=BRCteVPrest(v_tprest="100.00", v_tprest_liq="90.00", v_rec="100.00"),
        imp=BRCteImp(
            icms=make_cte().imp.icms,
            v_tot_dfe="100.00",
            ibscbs=BRCteImpIBSCBS(
                cst="000",
                c_class_trib="000001",
                g_trib_sn=BRCteTribSN(
                    g_ibssn=BRCteGIBSSN(p_ibssn="0.10", v_ibssn="0.10"),
                    g_cbssn=BRCteGCBSSN(p_cbssn="0.90", v_cbssn="0.90"),
                ),
            ),
        ),
        tp_pag_ant="3",
        pag_antecipado=[key],
    )
    xml = CTeGenerator().generate(cte)
    assert "<vTPrestLiq>90.00</vTPrestLiq>" in xml
    assert "<chDFePagAnt>" in xml and "chCTePagAnt" not in xml
    assert "<gTribSN><gIBSSN>" in xml
    result = CTeXSDValidator().validate(xml)
    assert result.valid is True, result.errors


def test_generate_tp_regime_ibscbs_validates_against_xsd() -> None:
    cte = make_cte(emitente=make_cte_emitente(crt="3", tp_regime_ibscbs="4"))
    xml = CTeGenerator().generate(cte)
    assert "<tpRegimeIBSCBS>4</tpRegimeIBSCBS>" in xml
    result = CTeXSDValidator().validate(xml)
    assert result.valid is True, result.errors
