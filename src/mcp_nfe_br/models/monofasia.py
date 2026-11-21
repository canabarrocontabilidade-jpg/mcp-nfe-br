"""IBS/CBS monofásico (`gIBSCBSMono`, tipo `TMonofasia`) — NF-e item level and totals.

`[Verified locally]` field names, order and occurrence against `TMonofasia` and
`TIBSCBSMonoTot` in `DFeTiposBasicos_v1.00.xsd` (PL_010h_v1.03, identical to the
PL_010f_v1.04 definition: NT 2025.002 v1.50, unchanged through v1.53).

Layout (v1.50): per tax (IBS, CBS) an optional choice between an *Ad Rem* group
(quantity x rate) and an *Ad Valorem* group (base x rate), each with up to four
subgroups: padrão (`gMonoPadrao`), retenção (`gMonoReten`), retido anteriormente
(`gMonoRet`) and diferimento de biocombustível (`gpBioDiferenca`). The item total
fields `vTotIBSMonoItem` / `vTotCBSMonoItem` are mandatory.

Every field is a decimal string, formatted by the generator: `q` = 4 decimals
(`TDec1104RTC`), `pct` = 2-4 decimals (`TDec_0302_04RTC`), `d2` = 2 decimals
(`TDec1302RTC`). Each leaf class lists its XML tags in schema order in `XML_FIELDS`
as ``(attribute, tag, format)``. Whether the amounts are arithmetically consistent
is not checked here (the NT's calculation rules are SEFAZ-side).
"""

from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel, Field, model_validator

XmlFields = tuple[tuple[str, str, str], ...]


class MonoLeaf(BaseModel):
    """A schema group whose children are all mandatory decimals."""

    XML_FIELDS: ClassVar[XmlFields] = ()


# ---------------------------------------------------------------------------
# IBS — Ad Rem
# ---------------------------------------------------------------------------


class BRIbsMonoAdRemPadrao(MonoLeaf):
    """`gIBSMonoAdRem/gMonoPadrao`."""

    XML_FIELDS: ClassVar[XmlFields] = (
        ("q_bc_mono", "qBCMono", "q"),
        ("ad_rem_ibs", "adRemIBS", "pct"),
        ("v_ibs_mono", "vIBSMono", "d2"),
    )
    q_bc_mono: str = Field(..., description="Quantidade tributada na monofasia (qBCMono)")
    ad_rem_ibs: str = Field(..., description="Alíquota ad rem do IBS (adRemIBS)")
    v_ibs_mono: str = Field(..., description="Valor do IBS monofásico (vIBSMono)")


class BRIbsMonoAdRemReten(MonoLeaf):
    """`gIBSMonoAdRem/gMonoReten`."""

    XML_FIELDS: ClassVar[XmlFields] = (
        ("q_bc_mono_reten", "qBCMonoReten", "q"),
        ("ad_rem_ibs_reten", "adRemIBSReten", "pct"),
        ("v_ibs_mono_reten", "vIBSMonoReten", "d2"),
    )
    q_bc_mono_reten: str = Field(..., description="Quantidade sujeita a retenção (qBCMonoReten)")
    ad_rem_ibs_reten: str = Field(..., description="Alíquota ad rem do IBS retido (adRemIBSReten)")
    v_ibs_mono_reten: str = Field(
        ..., description="Valor do IBS sujeito a retenção (vIBSMonoReten)"
    )


class BRIbsMonoRet(MonoLeaf):
    """`gMonoRet` (IBS), shared by Ad Rem and Ad Valorem."""

    XML_FIELDS: ClassVar[XmlFields] = (("v_ibs_mono_ret", "vIBSMonoRet", "d2"),)
    v_ibs_mono_ret: str = Field(..., description="Valor do IBS retido anteriormente (vIBSMonoRet)")


class BRIbsBioDiferenca(MonoLeaf):
    """`gpBioDiferenca` (IBS), shared by Ad Rem and Ad Valorem."""

    XML_FIELDS: ClassVar[XmlFields] = (
        ("q_bc_bio_comb", "qBCBioComb", "q"),
        ("v_ibs_diferenca", "vIBSDiferenca", "d2"),
    )
    q_bc_bio_comb: str = Field(..., description="Quantidade de biocombustível (qBCBioComb)")
    v_ibs_diferenca: str = Field(..., description="Valor do IBS diferido (vIBSDiferenca)")


class BRIbsMonoAdRem(BaseModel):
    """`gIBSMonoAdRem` — IBS monofásico ad rem."""

    g_mono_padrao: BRIbsMonoAdRemPadrao | None = None
    g_mono_reten: BRIbsMonoAdRemReten | None = None
    g_mono_ret: BRIbsMonoRet | None = None
    g_bio_diferenca: BRIbsBioDiferenca | None = None


# ---------------------------------------------------------------------------
# IBS — Ad Valorem
# ---------------------------------------------------------------------------


class BRIbsMonoAdValoremPadrao(MonoLeaf):
    """`gIBSMonoAdValorem/gMonoPadrao`."""

    XML_FIELDS: ClassVar[XmlFields] = (
        ("v_bc_mono", "vBCMono", "d2"),
        ("p_aliq_mono_uf", "pAliqMonoUF", "pct"),
        ("v_ibs_mono_uf", "vIBSMonoUF", "d2"),
        ("p_aliq_mono_mun", "pAliqMonoMun", "pct"),
        ("v_ibs_mono_mun", "vIBSMonoMun", "d2"),
        ("v_ibs_mono", "vIBSMono", "d2"),
    )
    v_bc_mono: str = Field(..., description="Base de cálculo da monofasia (vBCMono)")
    p_aliq_mono_uf: str = Field(..., description="Alíquota do IBS da UF (pAliqMonoUF)")
    v_ibs_mono_uf: str = Field(..., description="Valor do IBS monofásico da UF (vIBSMonoUF)")
    p_aliq_mono_mun: str = Field(..., description="Alíquota do IBS do município (pAliqMonoMun)")
    v_ibs_mono_mun: str = Field(
        ..., description="Valor do IBS monofásico do município (vIBSMonoMun)"
    )
    v_ibs_mono: str = Field(..., description="Valor total do IBS monofásico (vIBSMono)")


class BRIbsMonoAdValoremReten(MonoLeaf):
    """`gIBSMonoAdValorem/gMonoReten`."""

    XML_FIELDS: ClassVar[XmlFields] = (
        ("v_bc_mono_reten", "vBCMonoReten", "d2"),
        ("p_aliq_mono_reten", "pAliqMonoReten", "pct"),
        ("v_ibs_mono_reten", "vIBSMonoReten", "d2"),
    )
    v_bc_mono_reten: str = Field(..., description="Base sujeita a retenção (vBCMonoReten)")
    p_aliq_mono_reten: str = Field(..., description="Alíquota da retenção (pAliqMonoReten)")
    v_ibs_mono_reten: str = Field(
        ..., description="Valor do IBS sujeito a retenção (vIBSMonoReten)"
    )


class BRIbsMonoAdValorem(BaseModel):
    """`gIBSMonoAdValorem` — IBS monofásico ad valorem."""

    g_mono_padrao: BRIbsMonoAdValoremPadrao | None = None
    g_mono_reten: BRIbsMonoAdValoremReten | None = None
    g_mono_ret: BRIbsMonoRet | None = None
    g_bio_diferenca: BRIbsBioDiferenca | None = None


# ---------------------------------------------------------------------------
# CBS — Ad Rem
# ---------------------------------------------------------------------------


class BRCbsMonoAdRemPadrao(MonoLeaf):
    """`gCBSMonoAdRem/gMonoPadrao`."""

    XML_FIELDS: ClassVar[XmlFields] = (
        ("q_bc_mono", "qBCMono", "q"),
        ("ad_rem_cbs", "adRemCBS", "pct"),
        ("v_cbs_mono", "vCBSMono", "d2"),
    )
    q_bc_mono: str = Field(..., description="Quantidade tributada na monofasia (qBCMono)")
    ad_rem_cbs: str = Field(..., description="Alíquota ad rem da CBS (adRemCBS)")
    v_cbs_mono: str = Field(..., description="Valor da CBS monofásica (vCBSMono)")


class BRCbsMonoAdRemReten(MonoLeaf):
    """`gCBSMonoAdRem/gMonoReten`."""

    XML_FIELDS: ClassVar[XmlFields] = (
        ("q_bc_mono_reten", "qBCMonoReten", "q"),
        ("ad_rem_cbs_reten", "adRemCBSReten", "pct"),
        ("v_cbs_mono_reten", "vCBSMonoReten", "d2"),
    )
    q_bc_mono_reten: str = Field(..., description="Quantidade sujeita a retenção (qBCMonoReten)")
    ad_rem_cbs_reten: str = Field(..., description="Alíquota ad rem da CBS retida (adRemCBSReten)")
    v_cbs_mono_reten: str = Field(
        ..., description="Valor da CBS sujeita a retenção (vCBSMonoReten)"
    )


class BRCbsMonoRet(MonoLeaf):
    """`gMonoRet` (CBS), shared by Ad Rem and Ad Valorem."""

    XML_FIELDS: ClassVar[XmlFields] = (("v_cbs_mono_ret", "vCBSMonoRet", "d2"),)
    v_cbs_mono_ret: str = Field(..., description="Valor da CBS retida anteriormente (vCBSMonoRet)")


class BRCbsBioDiferenca(MonoLeaf):
    """`gpBioDiferenca` (CBS), shared by Ad Rem and Ad Valorem."""

    XML_FIELDS: ClassVar[XmlFields] = (
        ("q_bc_bio_comb", "qBCBioComb", "q"),
        ("v_cbs_diferenca", "vCBSDiferenca", "d2"),
    )
    q_bc_bio_comb: str = Field(..., description="Quantidade de biocombustível (qBCBioComb)")
    v_cbs_diferenca: str = Field(..., description="Valor da CBS diferida (vCBSDiferenca)")


class BRCbsMonoAdRem(BaseModel):
    """`gCBSMonoAdRem` — CBS monofásica ad rem."""

    g_mono_padrao: BRCbsMonoAdRemPadrao | None = None
    g_mono_reten: BRCbsMonoAdRemReten | None = None
    g_mono_ret: BRCbsMonoRet | None = None
    g_bio_diferenca: BRCbsBioDiferenca | None = None


# ---------------------------------------------------------------------------
# CBS — Ad Valorem
# ---------------------------------------------------------------------------


class BRCbsMonoAdValoremPadrao(MonoLeaf):
    """`gCBSMonoAdValorem/gMonoPadrao`."""

    XML_FIELDS: ClassVar[XmlFields] = (
        ("v_bc_mono", "vBCMono", "d2"),
        ("p_aliq_mono_cbs", "pAliqMonoCBS", "pct"),
        ("v_cbs_mono", "vCBSMono", "d2"),
    )
    v_bc_mono: str = Field(..., description="Base de cálculo da monofasia (vBCMono)")
    p_aliq_mono_cbs: str = Field(..., description="Alíquota da CBS (pAliqMonoCBS)")
    v_cbs_mono: str = Field(..., description="Valor da CBS monofásica (vCBSMono)")


class BRCbsMonoAdValoremReten(MonoLeaf):
    """`gCBSMonoAdValorem/gMonoReten`."""

    XML_FIELDS: ClassVar[XmlFields] = (
        ("v_bc_mono_reten", "vBCMonoReten", "d2"),
        ("p_aliq_mono_reten", "pAliqMonoReten", "pct"),
        ("v_cbs_mono_reten", "vCBSMonoReten", "d2"),
    )
    v_bc_mono_reten: str = Field(..., description="Base sujeita a retenção (vBCMonoReten)")
    p_aliq_mono_reten: str = Field(..., description="Alíquota da retenção (pAliqMonoReten)")
    v_cbs_mono_reten: str = Field(
        ..., description="Valor da CBS sujeita a retenção (vCBSMonoReten)"
    )


class BRCbsMonoAdValorem(BaseModel):
    """`gCBSMonoAdValorem` — CBS monofásica ad valorem."""

    g_mono_padrao: BRCbsMonoAdValoremPadrao | None = None
    g_mono_reten: BRCbsMonoAdValoremReten | None = None
    g_mono_ret: BRCbsMonoRet | None = None
    g_bio_diferenca: BRCbsBioDiferenca | None = None


# ---------------------------------------------------------------------------
# Top-level group and totals
# ---------------------------------------------------------------------------


class BRGrupoIBSCBSMono(BaseModel):
    """`gIBSCBSMono` (`TMonofasia`): IBS/CBS monofásico of one item.

    Per tax, Ad Rem and Ad Valorem are alternatives (XSD `choice`); at most one is
    informed. `vTotIBSMonoItem` and `vTotCBSMonoItem` are mandatory.
    """

    g_ibs_mono_ad_rem: BRIbsMonoAdRem | None = None
    g_ibs_mono_ad_valorem: BRIbsMonoAdValorem | None = None
    g_cbs_mono_ad_rem: BRCbsMonoAdRem | None = None
    g_cbs_mono_ad_valorem: BRCbsMonoAdValorem | None = None
    v_tot_ibs_mono_item: str = Field(..., description="Total do IBS monofásico do item")
    v_tot_cbs_mono_item: str = Field(..., description="Total da CBS monofásica do item")

    @model_validator(mode="after")
    def check_choice(self) -> BRGrupoIBSCBSMono:
        if self.g_ibs_mono_ad_rem is not None and self.g_ibs_mono_ad_valorem is not None:
            raise ValueError("gIBSMonoAdRem e gIBSMonoAdValorem são alternativos (escolha 0-1).")
        if self.g_cbs_mono_ad_rem is not None and self.g_cbs_mono_ad_valorem is not None:
            raise ValueError("gCBSMonoAdRem e gCBSMonoAdValorem são alternativos (escolha 0-1).")
        return self


class BRGrupoMonoTot(MonoLeaf):
    """`total/IBSCBSTot/gMono` (`TIBSCBSMonoTot`): totals of the monofásico amounts."""

    XML_FIELDS: ClassVar[XmlFields] = (
        ("v_ibs_mono", "vIBSMono", "d2"),
        ("v_cbs_mono", "vCBSMono", "d2"),
        ("v_ibs_mono_reten", "vIBSMonoReten", "d2"),
        ("v_cbs_mono_reten", "vCBSMonoReten", "d2"),
        ("v_ibs_mono_ret", "vIBSMonoRet", "d2"),
        ("v_cbs_mono_ret", "vCBSMonoRet", "d2"),
    )
    v_ibs_mono: str = Field(..., description="Total do IBS monofásico (vIBSMono)")
    v_cbs_mono: str = Field(..., description="Total da CBS monofásica (vCBSMono)")
    v_ibs_mono_reten: str = Field(..., description="Total do IBS sujeito a retenção")
    v_cbs_mono_reten: str = Field(..., description="Total da CBS sujeita a retenção")
    v_ibs_mono_ret: str = Field(..., description="Total do IBS retido anteriormente")
    v_cbs_mono_ret: str = Field(..., description="Total da CBS retida anteriormente")
