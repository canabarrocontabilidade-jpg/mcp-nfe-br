# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Fixed
- NF-e/NFC-e: IBS/CBS emission now validates against the official PL_010h_v1.03 schema. Item `IBSCBS` emits `CST` (was `cst`), wraps `vBC`/`gIBSUF`/`gIBSMun`/`vIBS`/`gCBS` in the `gIBSCBS` group, and places `gTribSN` as its sibling. `ISTot` (`vIS`) and `IBSCBSTot` are emitted as children of `total` after `ICMSTot` instead of inside it, and `vNFTot` (`v_nf_tot`) is now emitted. XSD-validating tests cover the item group, the totals and `gTribSN`.

### Added
- CT-e: `ide/gMultaJuros` (CT-e de multa e juros, NT 2026.004 v1.01, production 2026-12-14) as `BRCTeDocument.g_multa_juros`. The model enforces the stateless rules: ICMS must be CST 41 (RV 1072), the referenced key must be valid (RV 1073: UF, year, month, CNPJ, model 57, number, `tpEmis`, check digit) and the referenced CT-e must have the same emitter (RV 1078, read from the CNPJ in the key). The cross-document rules (RV 1074-1077, 1079-1083) need SEFAZ data and are not checked.
- CT-e: `ICMS45` (CST 40, 41, 51, with the optional `vICMSDeson` + `cBenef` pair) as an alternative to `ICMS00` in `BRCteImp.icms`. `BRCteICMS00.cst` is now restricted to `00`.
- CT-e: `pgtoVinc` (vinculação com a transação de pagamento, NT 2026.001, split payment preparatory for 2027) as `BRCTeDocument.pgto_vinc`, up to 99 entries reusing `BRPgtoVinc`, emitted between `imp` and `infCTeNorm`; validates the receiver CNPJ (rule 01) and unique `idTransacao`. The events 110300 and 110301 are not implemented.
- NF-e: emitter without `emit/IE` (contribuinte exclusivo do IBS/CBS, NT 2026.007 v1.11, production 2026-11-16). `BREmitente.ie` is now optional and `is_contribuinte_exclusivo_ibs_cbs` reports its absence. The model enforces the stateless rules: NFC-e forbidden (C17-42), CNPJ required (C17-43), no IEST (C18-50), no ICMS group except `finNFe=4` (N01-10), IBS/CBS group on every item (UB12-11). The generator omits `IE` and the ICMS group. CCC/LCC-RFB lookups, the `indExcIBSCBS` CFOP table and the `tpNFCredito=03` exception are SEFAZ-side or not modeled.
- NF-e: authorization routing for such documents. `get_endpoint(..., contribuinte_exclusivo_ibs_cbs=True)` and `SefazClient(..., contribuinte_exclusivo_ibs_cbs=True)` use the SVRS web service whatever the emitter's UF (C17-11); `br__submit_nfe` detects a model 55 document without `emit/IE` automatically, and `br__consult_sefaz_status` gains the same flag.
- NF-e: IBS/CBS monofásico (`gIBSCBSMono`, `TMonofasia` of NT 2025.002 v1.50) at item level (`BRGrupoIBSCBS.g_ibscbs_mono`) and `IBSCBSTot/gMono` totals (`BRGrupoIBSCBSTot.g_mono`), with Ad Rem / Ad Valorem choices per tax, padrão, retenção, retido and biocombustível subgroups. XSD-validated against PL_010h_v1.03; the monofásico group is exclusive with the `gIBSCBS` fields, as in the schema.
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
