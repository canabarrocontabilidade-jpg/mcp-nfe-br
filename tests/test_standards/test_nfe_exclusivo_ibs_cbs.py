"""Emitter without `emit/IE` — contribuinte exclusivo do IBS/CBS (BR-NFE-IE-OPT-1).

`[Verified locally]` against NFe_NT2026.007_v1.11 (rules C17-11/42/43, C18-50, N01-10,
UB12-11). Production date in v1.11: 2026-11-16.
"""

from __future__ import annotations

import pytest
from lxml import etree
from pydantic import ValidationError

from mcp_nfe_br.models.invoice import (
    BRGrupoCBS,
    BRGrupoIBSCBS,
    BRGrupoIBSMun,
    BRGrupoIBSUF,
    TipoAmbiente,
)
from mcp_nfe_br.standards.nfe_generator import NFeGenerator
from mcp_nfe_br.standards.sefaz_client import get_endpoint
from mcp_nfe_br.tools.sefaz import _emitente_sem_ie
from mcp_nfe_br.validators.nfe_xsd import NFeXSDValidator
from tests.conftest import make_emitente, make_line, make_nfce, make_nfe

_NS = {"n": "http://www.portalfiscal.inf.br/nfe"}


def _ibscbs() -> BRGrupoIBSCBS:
    return BRGrupoIBSCBS(
        cst="000",
        c_class_trib="000001",
        v_bc="100.00",
        ibs_uf=BRGrupoIBSUF(p_ibs_uf="2.0000", v_ibs_uf="2.00"),
        ibs_mun=BRGrupoIBSMun(p_ibs_mun="1.0000", v_ibs_mun="1.00"),
        v_ibs="3.00",
        cbs=BRGrupoCBS(p_cbs="9.0000", v_cbs="9.00"),
    )


def _exclusivo_line(**overrides: object):
    data = {"icms_cst": None, "icms_rate": None, "icms_amount": None, "ibs_cbs": _ibscbs()}
    data.update(overrides)
    return make_line(**data)


def _exclusivo(**overrides: object):
    data = {"emitente": make_emitente(ie=None), "lines": [_exclusivo_line()]}
    data.update(overrides)
    return make_nfe(**data)


def test_emitente_without_ie_is_exclusivo() -> None:
    assert make_emitente(ie=None).is_contribuinte_exclusivo_ibs_cbs is True
    assert make_emitente().is_contribuinte_exclusivo_ibs_cbs is False


def test_exclusivo_document_has_no_ie_and_no_icms_and_validates() -> None:
    xml = NFeGenerator().generate(_exclusivo())
    result = NFeXSDValidator().validate(xml)
    assert result.valid is True, result.errors
    root = etree.fromstring(xml.encode())
    assert root.find(".//n:emit/n:IE", _NS) is None
    assert root.find(".//n:det/n:imposto/n:ICMS", _NS) is None
    assert root.find(".//n:det/n:imposto/n:IBSCBS", _NS) is not None


def test_ordinary_document_still_emits_ie() -> None:
    xml = NFeGenerator().generate(make_nfe())
    assert "<IE>123456789</IE>" in xml


def test_nfce_is_rejected_for_exclusivo() -> None:
    with pytest.raises(ValidationError, match="C17-42"):
        make_nfce(emitente=make_emitente(ie=None))


def test_cpf_emitente_is_rejected_for_exclusivo() -> None:
    emit = make_emitente(ie=None, cnpj=None, cpf="52998224725")
    with pytest.raises(ValidationError, match="C17-43"):
        _exclusivo(emitente=emit)


def test_iest_is_rejected_for_exclusivo() -> None:
    with pytest.raises(ValidationError, match="C18-50"):
        _exclusivo(emitente=make_emitente(ie=None, ie_st="987654321"))


def test_missing_ibs_cbs_group_is_rejected() -> None:
    with pytest.raises(ValidationError, match="UB12-11"):
        _exclusivo(lines=[_exclusivo_line(ibs_cbs=None)])


def test_icms_is_rejected_for_exclusivo() -> None:
    line = _exclusivo_line(icms_cst="00", icms_rate="18", icms_amount="18.00")
    with pytest.raises(ValidationError, match="N01-10"):
        _exclusivo(lines=[line])


def test_icms_allowed_when_finalidade_is_devolucao() -> None:
    line = _exclusivo_line(icms_cst="00", icms_rate="18", icms_amount="18.00")
    invoice = _exclusivo(lines=[line], fin_nfe="4")
    assert invoice.fin_nfe == "4"


def test_endpoint_routes_exclusivo_to_svrs_regardless_of_uf() -> None:
    # cUF 35 (SP) has its own autorizador; the flag must override it (rule C17-11).
    normal = get_endpoint("autorizacao", "35", TipoAmbiente.HOMOLOGACAO)
    exclusivo = get_endpoint(
        "autorizacao", "35", TipoAmbiente.HOMOLOGACAO, contribuinte_exclusivo_ibs_cbs=True
    )
    assert "svrs.rs.gov.br" not in normal
    assert "nfe-homologacao.svrs.rs.gov.br" in exclusivo


def test_distribuicao_dfe_ignores_exclusivo_flag() -> None:
    assert get_endpoint(
        "distribuicao_dfe", "35", TipoAmbiente.PRODUCAO, contribuinte_exclusivo_ibs_cbs=True
    ) == get_endpoint("distribuicao_dfe", "35", TipoAmbiente.PRODUCAO)


def test_submit_helper_detects_missing_ie_on_model_55() -> None:
    assert _emitente_sem_ie(NFeGenerator().generate(_exclusivo()).encode()) is True
    assert _emitente_sem_ie(NFeGenerator().generate(make_nfe()).encode()) is False
    assert _emitente_sem_ie(b"not xml") is False
