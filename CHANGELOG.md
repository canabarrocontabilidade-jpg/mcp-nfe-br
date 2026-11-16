# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- CT-e: `vPrest/vTPrestLiq` (`v_tprest_liq`) and `imp/vTotDFe` (`v_tot_dfe`, rule 365) from Nota Técnica 2026.004 v1.01 (Valor Líquido).
- CT-e: `emit/tpRegimeIBSCBS` (`tp_regime_ibscbs`, rules 1090/1091) and `imp/IBSCBS/gTribSN` (`g_trib_sn`, rules 1100-1106) from Nota Técnica 2026.005 v1.00 (Simples Nacional).

### Changed
- CT-e schema package upgraded to `PL_CTe_400_NT2026.005 RTC SN_1.00_corr.zip` (includes the NT 2026.004 v1.01 changes). Adds the `CTeSimp`, vinculação de pagamento, apropriação de crédito presumido and Simples Nacional event schemas to the bundle; none of these document types or events is generated yet.
- CT-e: `ide/gPagAntecipado/chCTePagAnt` is now emitted as `chDFePagAnt`, matching the renamed element in the new schema.

### Not implemented
- CT-e `ide/gMultaJuros` (requires ICMS CST 41, not modeled) and `imp/ICMS/gICMSPrevistoPagtoAntecip` (declared as a sibling alternative of `ICMS00` in the schema; production enforcement 2027-03-01).

---

## [0.9.1] - 2026-09-12

### Changed
- Lower-bound pin on `mcp-einvoicing-core` raised to `>=1.34.1` (was `>=1.33.0`). This package's own CI now runs `CHECK_PUBLIC_HYGIENE`, the pre-publish audit check that blocks accidental citations of the private orchestration repo.

---

## [0.7.0] - 2026-08-22

### Added
- Initial changelog. Prior release history is recorded in the Git tags and
  GitHub Releases for this repository.
