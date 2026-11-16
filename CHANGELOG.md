# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- NF-e/NFC-e: `prod/vUnComLiq` + `vProdLiq` (`v_un_com_liq`, `v_prod_liq`) and `total/vProdLiqTot` (`v_prod_liq_tot`) from Nota Técnica 2026.008 v1.01, with rules I11c-20, W01a-10 and W01a-20.
- NF-e/NFC-e: `emit/tpRegimeIBSCBS` (`tp_regime_ibscbs`), `prod/cAtivSN` (`c_ativ_sn`), item `gTribSN` and total `gTribSN` from Nota Técnica 2026.005 v1.00, with the total rules W59h-10, W59h-20, W59i-10 and W59j-10.
- NF-e/NFC-e: group YC `gPgtoVinc` (`g_pgto_vinc`, split-payment linkage) from Nota Técnica 2026.006 v1.01.

### Changed
- NF-e/NFC-e schema package upgraded to `PL_010h_v1.03` (bundles NT 2026.005, 2026.006 and 2026.008 on top of `PL_010f`). The bundled `leiauteNFe`, `DFeTiposBasicos` and `tiposBasico` schemas are now the official files.

### Known limitations
- The existing item-level `IBSCBS` and total `IBSCBSTot` emission does not validate against the official schema (element name casing and `IBSCBSTot` placement inside `ICMSTot`). New `gTribSN` output follows the schema element order but sits inside that structure; fixing the surrounding IBS/CBS emission is tracked separately.
- `ICMSPrevistoPagtoAntecip` (NT 2026.008, enforcement from 2027-03-01) and the new events (110300, 412140) are not implemented.

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
