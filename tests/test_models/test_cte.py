"""Tests for CT-e (modelo 57) models (roadmap BR-CTE-2..4, 7)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from mcp_nfe_br.models.cte import (
    BRCteALCZFMCBS,
    BRCteCBS,
    BRCteDevTrib,
    BRCteGCBSSN,
    BRCteGIBSSN,
    BRCteIBSCBS,
    BRCteIBSMun,
    BRCteIBSUF,
    BRCteImp,
    BRCteImpIBSCBS,
    BRCteInfModal,
    BRCteParty,
    BRCteTomador,
    BRCteTribSN,
    BRCteVPrest,
    CTeModal,
    CTeModelo,
    CTeTomadorPapel,
)
from tests.conftest import make_cte, make_cte_emitente, make_cte_remetente, make_endereco

_ZFM_ENDERECO = make_endereco(c_mun="1302603", x_mun="Manaus", uf="AM")


def _make_ibscbs(**overrides: object) -> BRCteImpIBSCBS:
    data: dict[str, object] = {
        "cst": "000",
        "c_class_trib": "000001",
        "g_ibscbs": BRCteIBSCBS(
            v_bc="100.00",
            g_ibsuf=BRCteIBSUF(p_ibsuf="0.10", v_ibsuf="0.10"),
            g_ibsmun=BRCteIBSMun(p_ibsmun="0.00", v_ibsmun="0.00"),
            v_ibs="0.10",
            g_cbs=BRCteCBS(p_cbs="0.90", v_cbs="0.90"),
        ),
    }
    data.update(overrides)
    return BRCteImpIBSCBS.model_validate(data)


def test_make_cte_round_trips() -> None:
    cte = make_cte()
    assert cte.mod == CTeModelo.CTE
    assert cte.modal == CTeModal.RODOVIARIO
    assert cte.buyer is None
    assert cte.lines == []


def test_cte_party_requires_exactly_one_of_cnpj_cpf() -> None:
    with pytest.raises(ValidationError, match="CNPJ ou CPF"):
        BRCteParty(x_nome="Teste", endereco=make_endereco())
    with pytest.raises(ValidationError, match="CNPJ ou CPF"):
        BRCteParty(
            x_nome="Teste", endereco=make_endereco(), cnpj="11222333000181", cpf="11144477735"
        )


def test_cte_party_rejects_invalid_cnpj() -> None:
    with pytest.raises(ValidationError, match="CNPJ inválido"):
        make_cte_emitente(cnpj="00000000000000")


def test_cte_party_rejects_alphanumeric_cnpj() -> None:
    """BR-CTE-T1 (decided): CT-e's TCnpj (tiposGeralCTe_v4.00.xsd) is all-numeric,
    unlike NF-e's PL_010d schema — reject alphanumeric CNPJ at the party layer."""
    with pytest.raises(ValidationError, match="CNPJ numérico de 14 dígitos"):
        make_cte_emitente(cnpj="12ABC34501DE35")


def test_cte_party_accepts_numeric_cnpj() -> None:
    party = make_cte_emitente(cnpj="11222333000181")
    assert party.cnpj == "11222333000181"


def test_cte_tomador_requires_exactly_one_choice() -> None:
    with pytest.raises(ValidationError, match="papel.*ou.*outros"):
        BRCteTomador(ind_ie_toma="1")
    with pytest.raises(ValidationError, match="papel.*ou.*outros"):
        BRCteTomador(papel=CTeTomadorPapel.REMETENTE, outros=make_cte_remetente(), ind_ie_toma="1")


def test_cte_tomador_toma3_accepts_papel_only() -> None:
    tomador = BRCteTomador(papel=CTeTomadorPapel.DESTINATARIO, ind_ie_toma="9")
    assert tomador.papel == CTeTomadorPapel.DESTINATARIO
    assert tomador.outros is None


def test_cte_modal_consistency_enforced() -> None:
    with pytest.raises(ValidationError, match="inf_modal.modal"):
        make_cte(inf_modal=BRCteInfModal(modal=CTeModal.AEREO))


def test_cte_v_prest_comp_defaults_empty() -> None:
    v_prest = BRCteVPrest(v_tprest="100.00", v_rec="100.00")
    assert v_prest.comp == []


def test_cte_chave_acesso_format_validation() -> None:
    # First 6 chars must be numeric (cUF+AAMM), so a leading letter is rejected.
    with pytest.raises(ValidationError, match="TChDFe"):
        make_cte(chave_acesso="X" * 44)


def test_cte_chave_acesso_accepts_alphanumeric_cnpj() -> None:
    # TChDFe (BR-CTE-23): 6 numeric + 12 alphanumeric CNPJ root+branch + 26 numeric.
    key = "352508" + "12ABC345DE01" + "0" * 26
    assert len(key) == 44
    cte = make_cte(chave_acesso=key)
    assert cte.chave_acesso == key


def test_cte_chave_acesso_accepts_legacy_all_numeric() -> None:
    # All-numeric keys remain valid (backward-compatible with the old [0-9]{44}).
    key = "0" * 44
    cte = make_cte(chave_acesso=key)
    assert cte.chave_acesso == key


# --- Reforma Tributária do Consumo (NT 2026.002) — closes GitHub issue cmendezs/mcp-nfe-br#5 ---


def test_cte_accepts_ibscbs_when_route_and_parties_in_zfm() -> None:
    cte = make_cte(
        c_mun_ini="1302603",
        x_mun_ini="Manaus",
        uf_ini="AM",
        c_mun_fim="1302603",
        x_mun_fim="Manaus",
        uf_fim="AM",
        emitente=make_cte_emitente(isuf_emit="12345678", endereco=_ZFM_ENDERECO),
        remetente=make_cte_remetente(endereco=_ZFM_ENDERECO),
        tomador=BRCteTomador(papel=CTeTomadorPapel.REMETENTE, ind_ie_toma="1"),
        imp=BRCteImp(
            icms=make_cte().imp.icms,
            ibscbs=_make_ibscbs(
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
                )
            ),
        ),
    )
    assert cte.imp.ibscbs is not None
    assert cte.imp.ibscbs.g_ibscbs.g_cbs.g_alczfmcbs.v_trib_reg_cbs == "0.90"


def test_cte_rejects_isuf_emit_outside_zfm_alc() -> None:
    """NT 2026.002 RV 4.001 — default fixture emitente is in São Paulo."""
    with pytest.raises(ValidationError, match="RV 4.001"):
        make_cte(emitente=make_cte_emitente(isuf_emit="12345678"))


def test_cte_rejects_devolucao_group_for_cte() -> None:
    """NT 2026.002 RV 5.001-003 — gDevTrib is never valid for CT-e."""
    with pytest.raises(ValidationError, match="RV 5.001-003"):
        make_cte(
            imp=BRCteImp(
                icms=make_cte().imp.icms,
                ibscbs=_make_ibscbs(
                    g_ibscbs=BRCteIBSCBS(
                        v_bc="100.00",
                        g_ibsuf=BRCteIBSUF(
                            p_ibsuf="0.10",
                            v_ibsuf="0.10",
                            g_dev_trib=BRCteDevTrib(v_dev_trib="1.00"),
                        ),
                        g_ibsmun=BRCteIBSMun(p_ibsmun="0.00", v_ibsmun="0.00"),
                        v_ibs="0.10",
                        g_cbs=BRCteCBS(p_cbs="0.90", v_cbs="0.90"),
                    )
                ),
            )
        )


def test_cte_rejects_alczfmcbs_without_suframa() -> None:
    """NT 2026.002 RV 6.003."""
    with pytest.raises(ValidationError, match="RV 6.003"):
        make_cte(
            c_mun_ini="1302603",
            x_mun_ini="Manaus",
            uf_ini="AM",
            c_mun_fim="1302603",
            x_mun_fim="Manaus",
            uf_fim="AM",
            emitente=make_cte_emitente(endereco=_ZFM_ENDERECO),  # no isuf_emit
            imp=BRCteImp(
                icms=make_cte().imp.icms,
                ibscbs=_make_ibscbs(
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
                    )
                ),
            ),
        )


def test_cte_rejects_alczfmcbs_route_outside_incentivized_area() -> None:
    """NT 2026.002 RV 6.004 — default fixture route is São Paulo -> Rio de Janeiro."""
    with pytest.raises(ValidationError, match="RV 6.004"):
        make_cte(
            emitente=make_cte_emitente(isuf_emit="12345678", endereco=_ZFM_ENDERECO),
            imp=BRCteImp(
                icms=make_cte().imp.icms,
                ibscbs=_make_ibscbs(
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
                    )
                ),
            ),
        )


def test_cte_rejects_v_trib_reg_cbs_arithmetic_mismatch() -> None:
    """NT 2026.002 RV 6.005 — vTribRegCBS must equal vBC x pAliqEfetRegCBS / 100."""
    with pytest.raises(ValidationError, match="RV 6.005"):
        make_cte(
            c_mun_ini="1302603",
            x_mun_ini="Manaus",
            uf_ini="AM",
            c_mun_fim="1302603",
            x_mun_fim="Manaus",
            uf_fim="AM",
            emitente=make_cte_emitente(isuf_emit="12345678", endereco=_ZFM_ENDERECO),
            remetente=make_cte_remetente(endereco=_ZFM_ENDERECO),
            tomador=BRCteTomador(papel=CTeTomadorPapel.REMETENTE, ind_ie_toma="1"),
            imp=BRCteImp(
                icms=make_cte().imp.icms,
                ibscbs=_make_ibscbs(
                    g_ibscbs=BRCteIBSCBS(
                        v_bc="100.00",
                        g_ibsuf=BRCteIBSUF(p_ibsuf="0.10", v_ibsuf="0.10"),
                        g_ibsmun=BRCteIBSMun(p_ibsmun="0.00", v_ibsmun="0.00"),
                        v_ibs="0.10",
                        g_cbs=BRCteCBS(
                            p_cbs="0.00",
                            g_alczfmcbs=BRCteALCZFMCBS(
                                p_aliq_efet_reg_cbs="0.90", v_trib_reg_cbs="99.99"
                            ),
                            v_cbs="0.00",
                        ),
                    )
                ),
            ),
        )


def test_cte_pag_antecipado_requires_tp_pag_ant_3() -> None:
    """NT 2026.002 RV 7.001/002."""
    key = "35070111222333000181000012300000000123456789012"[:44]
    with pytest.raises(ValidationError, match="RV 7.001"):
        make_cte(pag_antecipado=[key])
    with pytest.raises(ValidationError, match="RV 7.002"):
        make_cte(tp_pag_ant="3")


def test_cte_pag_antecipado_rejects_duplicates() -> None:
    """NT 2026.002 RV 7.011."""
    emit = make_cte_emitente(cnpj="11222333000181")
    key = "35070111222333" + "0" * 30  # cUF+AAMM(6) + CNPJ-Base(8) + resto
    assert len(key) == 44
    with pytest.raises(ValidationError, match="RV 7.011"):
        make_cte(tp_pag_ant="3", emitente=emit, pag_antecipado=[key, key])


def test_cte_pag_antecipado_rejects_cnpj_base_mismatch() -> None:
    """NT 2026.002 RV 7.010 — chCTePagAnt's embedded CNPJ-Base must match the emitente's."""
    emit = make_cte_emitente(cnpj="11222333000181")
    mismatched_key = "35070199999999" + "0" * 30
    assert len(mismatched_key) == 44
    with pytest.raises(ValidationError, match="RV 7.010"):
        make_cte(tp_pag_ant="3", emitente=emit, pag_antecipado=[mismatched_key])


def test_cte_pag_antecipado_accepts_matching_cnpj_base() -> None:
    emit = make_cte_emitente(cnpj="11222333000181")
    key = "35070111222333" + "0" * 30
    cte = make_cte(tp_pag_ant="3", emitente=emit, pag_antecipado=[key])
    assert cte.pag_antecipado == [key]


def test_cte_pag_antecipado_rejects_bad_format() -> None:
    with pytest.raises(ValidationError, match="44 caracteres"):
        make_cte(tp_pag_ant="3", pag_antecipado=["too-short"])


# --- NT 2026.004 v1.01 / NT 2026.005 v1.00 --------------------------------


def test_cte_emitente_tp_regime_ibscbs_rv_1090_1091() -> None:
    """NT 2026.005 RV 1090: CRT 1/2 requires '1'. RV 1091: CRT 3 requires 2, 3 or 4."""
    with pytest.raises(ValidationError, match="RV 1090"):
        make_cte_emitente(crt="1", tp_regime_ibscbs="2")
    with pytest.raises(ValidationError, match="RV 1091"):
        make_cte_emitente(crt="3", tp_regime_ibscbs="1")
    assert make_cte_emitente(crt="1", tp_regime_ibscbs="1").tp_regime_ibscbs == "1"
    assert make_cte_emitente(crt="3", tp_regime_ibscbs="4").tp_regime_ibscbs == "4"
    assert make_cte_emitente(crt="3").tp_regime_ibscbs is None


def _sn(*, ibs: bool, cbs: bool) -> BRCteTribSN:
    return BRCteTribSN(
        g_ibssn=BRCteGIBSSN(p_ibssn="0.10", v_ibssn="0.10") if ibs else None,
        g_cbssn=BRCteGCBSSN(p_cbssn="0.90", v_cbssn="0.90") if cbs else None,
    )


def _imp_sn(sn: BRCteTribSN | None, *, gibscbs: BRCteIBSCBS | None = None) -> BRCteImp:
    return BRCteImp(
        icms=make_cte().imp.icms,
        ibscbs=BRCteImpIBSCBS(cst="000", c_class_trib="000001", g_ibscbs=gibscbs, g_trib_sn=sn),
    )


def test_cte_simples_nacional_without_regular_regime_requires_both_sn_groups() -> None:
    emit = make_cte_emitente(crt="1")
    with pytest.raises(ValidationError, match="RV 1101"):
        make_cte(emitente=emit, imp=_imp_sn(_sn(ibs=False, cbs=True)))
    cte = make_cte(emitente=emit, imp=_imp_sn(_sn(ibs=True, cbs=True)))
    assert cte.imp.ibscbs is not None and cte.imp.ibscbs.g_trib_sn is not None


def test_cte_excesso_sublimite_without_regular_regime_cbs_only() -> None:
    emit = make_cte_emitente(crt="2")
    with pytest.raises(ValidationError, match="RV 1103"):
        make_cte(emitente=emit, imp=_imp_sn(_sn(ibs=True, cbs=False)))
    with pytest.raises(ValidationError, match="RV 1104"):
        make_cte(emitente=emit, imp=_imp_sn(_sn(ibs=True, cbs=True)))
    make_cte(emitente=emit, imp=_imp_sn(_sn(ibs=False, cbs=True)))


def test_cte_regular_regime_forbids_gtribsn() -> None:
    emit = make_cte_emitente(crt="1", tp_regime_ibscbs="1")
    with pytest.raises(ValidationError, match="RV 1102"):
        make_cte(emitente=emit, imp=_imp_sn(_sn(ibs=True, cbs=True)))


def test_cte_pending_option_regimes_rv_1105_1106() -> None:
    emit2 = make_cte_emitente(crt="3", tp_regime_ibscbs="2")
    with pytest.raises(ValidationError, match="RV 1105"):
        make_cte(emitente=emit2, imp=_imp_sn(_sn(ibs=False, cbs=True)))
    emit3 = make_cte_emitente(crt="3", tp_regime_ibscbs="3")
    with pytest.raises(ValidationError, match="RV 1106"):
        make_cte(emitente=emit3, imp=_imp_sn(_sn(ibs=True, cbs=True)))
    make_cte(emitente=emit3, imp=_imp_sn(_sn(ibs=False, cbs=True)))


def test_cte_v_tot_dfe_rv_365_2026_repeats_vtprest() -> None:
    cte = make_cte(imp=BRCteImp(icms=make_cte().imp.icms, v_tot_dfe="100.00"))
    assert cte.imp.v_tot_dfe == "100.00"
    with pytest.raises(ValidationError, match="RV 365"):
        make_cte(imp=BRCteImp(icms=make_cte().imp.icms, v_tot_dfe="101.00"))
