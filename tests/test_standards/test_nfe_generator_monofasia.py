"""IBS/CBS monofásico (`gIBSCBSMono`, `TMonofasia` v1.50) — BR-NFE-RTC-2.

XSD-validating tests against the bundled PL_010h_v1.03 schema (identical `TMonofasia`
definition to PL_010f_v1.04 / NT 2025.002 v1.50).
"""

from __future__ import annotations

import pytest
from lxml import etree
from pydantic import ValidationError

from mcp_nfe_br.models.invoice import BRGrupoCBS, BRGrupoIBSCBS, BRGrupoIBSCBSTot
from mcp_nfe_br.models.monofasia import (
    BRCbsBioDiferenca,
    BRCbsMonoAdRem,
    BRCbsMonoAdRemPadrao,
    BRCbsMonoAdRemReten,
    BRCbsMonoAdValorem,
    BRCbsMonoAdValoremPadrao,
    BRCbsMonoRet,
    BRGrupoIBSCBSMono,
    BRGrupoMonoTot,
    BRIbsBioDiferenca,
    BRIbsMonoAdRem,
    BRIbsMonoAdRemPadrao,
    BRIbsMonoAdRemReten,
    BRIbsMonoAdValorem,
    BRIbsMonoAdValoremPadrao,
    BRIbsMonoAdValoremReten,
    BRIbsMonoRet,
)
from mcp_nfe_br.standards.nfe_generator import NFeGenerator
from mcp_nfe_br.validators.nfe_xsd import NFeXSDValidator
from tests.conftest import make_line, make_nfe

_NS = {"n": "http://www.portalfiscal.inf.br/nfe"}


def _ad_rem_mono() -> BRGrupoIBSCBSMono:
    return BRGrupoIBSCBSMono(
        g_ibs_mono_ad_rem=BRIbsMonoAdRem(
            g_mono_padrao=BRIbsMonoAdRemPadrao(
                q_bc_mono="10.0000", ad_rem_ibs="0.5000", v_ibs_mono="5.00"
            ),
            g_mono_reten=BRIbsMonoAdRemReten(
                q_bc_mono_reten="2.5000", ad_rem_ibs_reten="0.5000", v_ibs_mono_reten="1.25"
            ),
            g_mono_ret=BRIbsMonoRet(v_ibs_mono_ret="0.50"),
            g_bio_diferenca=BRIbsBioDiferenca(q_bc_bio_comb="1.0000", v_ibs_diferenca="0.20"),
        ),
        g_cbs_mono_ad_rem=BRCbsMonoAdRem(
            g_mono_padrao=BRCbsMonoAdRemPadrao(
                q_bc_mono="10.0000", ad_rem_cbs="0.3000", v_cbs_mono="3.00"
            ),
            g_mono_reten=BRCbsMonoAdRemReten(
                q_bc_mono_reten="2.5000", ad_rem_cbs_reten="0.3000", v_cbs_mono_reten="0.75"
            ),
            g_mono_ret=BRCbsMonoRet(v_cbs_mono_ret="0.30"),
            g_bio_diferenca=BRCbsBioDiferenca(q_bc_bio_comb="1.0000", v_cbs_diferenca="0.10"),
        ),
        v_tot_ibs_mono_item="5.00",
        v_tot_cbs_mono_item="3.00",
    )


def _ad_valorem_mono() -> BRGrupoIBSCBSMono:
    return BRGrupoIBSCBSMono(
        g_ibs_mono_ad_valorem=BRIbsMonoAdValorem(
            g_mono_padrao=BRIbsMonoAdValoremPadrao(
                v_bc_mono="100.00",
                p_aliq_mono_uf="2.0000",
                v_ibs_mono_uf="2.00",
                p_aliq_mono_mun="1.0000",
                v_ibs_mono_mun="1.00",
                v_ibs_mono="3.00",
            ),
            g_mono_reten=BRIbsMonoAdValoremReten(
                v_bc_mono_reten="20.00", p_aliq_mono_reten="3.0000", v_ibs_mono_reten="0.60"
            ),
        ),
        g_cbs_mono_ad_valorem=BRCbsMonoAdValorem(
            g_mono_padrao=BRCbsMonoAdValoremPadrao(
                v_bc_mono="100.00", p_aliq_mono_cbs="9.0000", v_cbs_mono="9.00"
            ),
        ),
        v_tot_ibs_mono_item="3.00",
        v_tot_cbs_mono_item="9.00",
    )


def _generate(mono: BRGrupoIBSCBSMono, **invoice_overrides: object) -> str:
    ibscbs = BRGrupoIBSCBS(cst="620", c_class_trib="620001", g_ibscbs_mono=mono)
    return NFeGenerator().generate(make_nfe(lines=[make_line(ibs_cbs=ibscbs)], **invoice_overrides))


def _validate(xml: str) -> None:
    result = NFeXSDValidator().validate(xml)
    assert result.valid is True, result.errors


def test_ad_rem_with_all_subgroups_validates() -> None:
    _validate(_generate(_ad_rem_mono()))


def test_ad_valorem_validates() -> None:
    _validate(_generate(_ad_valorem_mono()))


def test_mono_replaces_gibscbs_and_keeps_schema_order() -> None:
    xml = _generate(_ad_rem_mono())
    root = etree.fromstring(xml.encode())
    node = root.find(".//n:det/n:imposto/n:IBSCBS", _NS)
    assert [etree.QName(c).localname for c in node] == ["CST", "cClassTrib", "gIBSCBSMono"]
    mono = node.find("n:gIBSCBSMono", _NS)
    assert [etree.QName(c).localname for c in mono] == [
        "gIBSMonoAdRem",
        "gCBSMonoAdRem",
        "vTotIBSMonoItem",
        "vTotCBSMonoItem",
    ]
    padrao = mono.find("n:gIBSMonoAdRem/n:gMonoPadrao", _NS)
    assert [etree.QName(c).localname for c in padrao] == ["qBCMono", "adRemIBS", "vIBSMono"]
    assert mono.find("n:gIBSMonoAdRem/n:gMonoPadrao/n:qBCMono", _NS).text == "10.0000"


def test_mono_totals_group_validates_and_follows_gcbs() -> None:
    tot = BRGrupoIBSCBSTot(
        v_bc_ibscbs="0.00",
        g_mono=BRGrupoMonoTot(
            v_ibs_mono="5.00",
            v_cbs_mono="3.00",
            v_ibs_mono_reten="1.25",
            v_cbs_mono_reten="0.75",
            v_ibs_mono_ret="0.50",
            v_cbs_mono_ret="0.30",
        ),
    )
    xml = _generate(_ad_rem_mono(), ibscbs_tot=tot)
    _validate(xml)
    root = etree.fromstring(xml.encode())
    names = [etree.QName(c).localname for c in root.find(".//n:total/n:IBSCBSTot", _NS)]
    assert names == ["vBCIBSCBS", "gMono"]


def test_mono_is_rejected_together_with_gibscbs_fields() -> None:
    with pytest.raises(ValidationError, match="alternativo"):
        BRGrupoIBSCBS(
            cst="620",
            c_class_trib="620001",
            v_bc="100.00",
            cbs=BRGrupoCBS(p_cbs="9.0000", v_cbs="9.00"),
            g_ibscbs_mono=_ad_rem_mono(),
        )


def test_ad_rem_and_ad_valorem_are_alternatives_per_tax() -> None:
    with pytest.raises(ValidationError, match="alternativos"):
        BRGrupoIBSCBSMono(
            g_ibs_mono_ad_rem=BRIbsMonoAdRem(),
            g_ibs_mono_ad_valorem=BRIbsMonoAdValorem(),
            v_tot_ibs_mono_item="0.00",
            v_tot_cbs_mono_item="0.00",
        )
