"""XSD-validating tests for the IBS/CBS emission paths (BR-NFE-RTC-3).

The bundled schema is identical to the official PL_010h_v1.03 package, so
`NFeXSDValidator` is the authority here, not substring assertions.
"""

from __future__ import annotations

from lxml import etree

from mcp_nfe_br.models.invoice import (
    BRGrupoCBS,
    BRGrupoCBSSN,
    BRGrupoCBSTot,
    BRGrupoIBSCBS,
    BRGrupoIBSCBSTot,
    BRGrupoIBSMun,
    BRGrupoIBSMunTot,
    BRGrupoIBSSN,
    BRGrupoIBSTot,
    BRGrupoIBSUF,
    BRGrupoIBSUFTot,
    BRGrupoTribSN,
    BRGrupoTribSNTot,
)
from mcp_nfe_br.standards.nfe_generator import NFeGenerator
from mcp_nfe_br.validators.nfe_xsd import NFeXSDValidator
from tests.conftest import make_line, make_nfe

_NS = {"n": "http://www.portalfiscal.inf.br/nfe"}


def _full_ibscbs() -> BRGrupoIBSCBS:
    return BRGrupoIBSCBS(
        cst="000",
        c_class_trib="000001",
        v_bc="100.00",
        ibs_uf=BRGrupoIBSUF(p_ibs_uf="2.0000", v_ibs_uf="2.00"),
        ibs_mun=BRGrupoIBSMun(p_ibs_mun="1.0000", v_ibs_mun="1.00"),
        v_ibs="3.00",
        cbs=BRGrupoCBS(p_cbs="9.0000", v_cbs="9.00"),
    )


def _validate(xml: str) -> None:
    result = NFeXSDValidator().validate(xml)
    assert result.valid is True, result.errors


def test_item_ibscbs_validates_against_schema() -> None:
    xml = NFeGenerator().generate(make_nfe(lines=[make_line(ibs_cbs=_full_ibscbs())]))
    _validate(xml)


def test_item_ibscbs_uses_uppercase_cst_and_gibscbs_wrapper() -> None:
    xml = NFeGenerator().generate(make_nfe(lines=[make_line(ibs_cbs=_full_ibscbs())]))
    root = etree.fromstring(xml.encode())
    node = root.find(".//n:det/n:imposto/n:IBSCBS", _NS)
    assert node is not None
    children = [etree.QName(c).localname for c in node]
    assert children[:3] == ["CST", "cClassTrib", "gIBSCBS"]
    wrapper = node.find("n:gIBSCBS", _NS)
    assert [etree.QName(c).localname for c in wrapper] == [
        "vBC",
        "gIBSUF",
        "gIBSMun",
        "vIBS",
        "gCBS",
    ]


def test_item_gtribsn_is_sibling_of_gibscbs() -> None:
    sn = BRGrupoTribSN(
        g_ibssn=BRGrupoIBSSN(p_ibssn="0.1000", v_ibssn="0.10"),
        g_cbssn=BRGrupoCBSSN(p_cbssn="0.9000", v_cbssn="0.90"),
    )
    ibscbs = BRGrupoIBSCBS(cst="000", c_class_trib="000001", g_trib_sn=sn)
    tot = BRGrupoIBSCBSTot(
        v_bc_ibscbs="0.00", g_trib_sn=BRGrupoTribSNTot(v_ibssn="0.10", v_cbssn="0.90")
    )
    xml = NFeGenerator().generate(make_nfe(lines=[make_line(ibs_cbs=ibscbs)], ibscbs_tot=tot))
    _validate(xml)
    root = etree.fromstring(xml.encode())
    node = root.find(".//n:det/n:imposto/n:IBSCBS", _NS)
    assert [etree.QName(c).localname for c in node] == ["CST", "cClassTrib", "gTribSN"]


def _tot() -> BRGrupoIBSCBSTot:
    return BRGrupoIBSCBSTot(
        v_bc_ibscbs="100.00",
        ibs=BRGrupoIBSTot(
            ibs_uf=BRGrupoIBSUFTot(v_dif="0.00", v_dev_trib="0.00", v_ibs_uf="2.00"),
            ibs_mun=BRGrupoIBSMunTot(v_dif="0.00", v_dev_trib="0.00", v_ibs_mun="1.00"),
            v_ibs="3.00",
            v_cred_pres="0.00",
            v_cred_pres_cond_sus="0.00",
        ),
        cbs=BRGrupoCBSTot(
            v_dif="0.00",
            v_dev_trib="0.00",
            v_cbs="9.00",
            v_cred_pres="0.00",
            v_cred_pres_cond_sus="0.00",
        ),
    )


def test_ibscbs_tot_validates_and_is_sibling_of_icms_tot() -> None:
    xml = NFeGenerator().generate(make_nfe(ibscbs_tot=_tot()))
    _validate(xml)
    root = etree.fromstring(xml.encode())
    total = root.find(".//n:total", _NS)
    assert "IBSCBSTot" in [etree.QName(c).localname for c in total]
    assert root.find(".//n:ICMSTot/n:IBSCBSTot", _NS) is None


def test_is_tot_is_a_sibling_group_with_vis() -> None:
    xml = NFeGenerator().generate(make_nfe(v_is_tot="10.00"))
    _validate(xml)
    root = etree.fromstring(xml.encode())
    assert root.find(".//n:total/n:ISTot/n:vIS", _NS).text == "10.00"
    assert root.find(".//n:ICMSTot/n:vISTot", _NS) is None


def test_total_children_follow_schema_order() -> None:
    xml = NFeGenerator().generate(make_nfe(v_is_tot="10.00", ibscbs_tot=_tot(), v_nf_tot="1010.00"))
    _validate(xml)
    root = etree.fromstring(xml.encode())
    names = [etree.QName(c).localname for c in root.find(".//n:total", _NS)]
    assert names == ["ICMSTot", "ISTot", "IBSCBSTot", "vNFTot"]
