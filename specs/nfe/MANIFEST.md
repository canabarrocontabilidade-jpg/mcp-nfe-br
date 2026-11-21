# NF-e / NFC-e specs — inventory

Normative source material for NF-e (modelo 55) and NFC-e (modelo 65), schema 4.00.
PDFs and ZIPs are gitignored (large binaries, not published) — this manifest is the
checked-in index. Source: user-supplied bundle from `nfe.fazenda.gov.br` /
`portalfiscal.inf.br`, retrieved 2026-06-12.

## XSD schema packages

| Directory | Package | Status | Notes |
|---|---|---|---|
| `xsd/` | PL_010c (NT2022.002 v1.30) | **Current production schema** | Namespace `http://www.portalfiscal.inf.br/nfe`, schema 4.00. `TCnpj` = `[0-9]{14}`, `TCpf` = `[0-9]{11}`. |
| `xsd_pl010d_cnpj_alfa/` | PL_010d (NT 2026.004 v1.01) | Superseded by `xsd_pl010d_v1.03/` | `TCnpj` becomes `[0-9A-Z]{12}[0-9]{2}`; `TChNFe` (access key) becomes `[0-9]{6}[0-9A-Z]{12}[0-9]{26}`. |
| `xsd_pl010d_v1.03/` | PL_010d_v1.03 (CNPJ Alfanumérico point release, 10/07/2026, official) | CNPJ-alfa track — separate lineage from 010e, no DANFE Tipo 2 content | Full package: `NFe/`, `Evento/`, `CadConsultaCadastro/` folders. Diffed against `010e_v1.02` (2026-08-14): identical except 010e's DANFE-Tipo-2-specific delta is absent here — confirms the two lineages have not yet merged. |
| `xsd_pl010e_v1.02/` | PL_010e_v.1.02 (released 2026-07-10, official) — bundles NT 2025.002 v1.40, NT 2026.002 v1.0, NT 2026.003 v1.0 | Superseded by `xsd_pl010f_v1.04/` | `[Verified locally — 2026-08-14, BR-NFE-2026-08]`. Delta vs. `PL_010d`: `tpImp` gains enum `6`; `tpEmis`/`indPres` documentation broadened (same enum values); new optional elements `cIndOp` (`ide` group, `[0-9]{6}`) and `ISUFEmit` (`emit` group, `[0-9]{8,9}`); `protNFe/infProt` gains a `maxOccurs="5"` `cMsg`/`xMsg` alert-message sequence (was effectively 0-1); `infNFeSupl/qrCode`'s V3-OFFLINE pattern widens the destinatário-ID segment to alphanumeric-CNPJ-or-CPF; `TTpNFCredito` gains enum `06`. This delta was hand-applied to `src/mcp_nfe_br/schemas/nfe/leiauteNFe_v4.00.xsd` and `leiauteNFe_v4.00_unsigned.xsd`, cited inline per element. |
| `xsd_pl010f_v1.04/` | **PL_010f_v1.04 (released 2026-08-31, official)** (superseded by `xsd_pl010h_v1.03/`) — bundles NT 2026.007 v1.00 + NT 2025.002 v1.50 | **Current schema** — regulatory-update, closes `regulatory-update` issue mcp-nfe-br#6 | `[Verified locally — 2026-09-07]`. Diffed the 5 supplied XSDs against `xsd_pl010e_v1.02/`; the only substantive change in `leiauteNFe_v4.00.xsd` is NT 2026.007's IE-optional issuance path: `emit/IE` gains `minOccurs="0"` (was required) — for taxpayers exclusively subject to IBS/CBS; homologação 2026-09-01, produção 2026-11-03 in v1.00 (moved to 2026-11-16 by v1.11). Cosmetic: `vNFTot`'s declared type renamed `TDec_1302Opc` → `TDec_1302` (the type definitions themselves are byte-identical between packages; `vNFTot` already carries `minOccurs="0"`, so no functional impact). This delta was hand-applied to `src/mcp_nfe_br/schemas/nfe/leiauteNFe_v4.00.xsd` and `leiauteNFe_v4.00_unsigned.xsd`, cited inline per element — same pattern as the 010e delta above. The rest of the `PL_010f` package's diff against `010e` is entirely inside `DFeTiposBasicos_v1.00.xsd`'s `TMonofasia` (IBS/CBS single-phase-taxation) group — a full restructuring, **modeled in v0.12.0 (BR-NFE-RTC-2)**. `[Verified locally — 2026-11-21]` delta, `PL_010e` (NT 2025.002 v1.40) to `PL_010f` (v1.50), identical in `PL_010h`: v1.40 `TMonofasia` was flat (`gMonoPadrao` with both `adRemIBS`/`adRemCBS`, `gMonoReten`, `gMonoRet` with `qBCMonoRet`/`adRemIBSRet`/`adRemCBSRet`, `gMonoDif` with `pDifIBS`/`pDifCBS`, then `vTotIBSMonoItem`/`vTotCBSMonoItem`). v1.50 splits it per tax: an optional choice `gIBSMonoAdRem` | `gIBSMonoAdValorem`, then `gCBSMonoAdRem` | `gCBSMonoAdValorem`, each with `gMonoPadrao`, `gMonoReten`, `gMonoRet` (now only the retained amount) and `gpBioDiferenca` (`qBCBioComb` + `vIBSDiferenca`/`vCBSDiferenca`, replaces `gMonoDif`); Ad Valorem adds `vBCMono`, `pAliqMonoUF`/`pAliqMonoMun`/`pAliqMonoCBS`/`pAliqMonoReten`. `vTotIBSMonoItem`/`vTotCBSMonoItem` stay mandatory. Modeled in `src/mcp_nfe_br/models/monofasia.py`, emitted by `NFeGenerator`, XSD-tested in `tests/test_standards/test_nfe_generator_monofasia.py`. Still `[NEED]`: the `xsd_eventos_rtc/` event review. **Implemented in v0.12.0 (BR-NFE-IE-OPT-1):** the invoice model's `IE` is now optional; an emitter without `emit/IE` is a contribuinte exclusivo do IBS/CBS per NT 2026.007 v1.11 (production 2026-11-16, superseding the 2026-11-03 date of v1.00), with its stateless rules enforced in the model and SVRS routing in `SefazClient`. |
| `xsd_pl010h_v1.03/` | **PL_010h_v1.03 (official, supplied 2026-11-16)** — bundles NT 2026.005 v1.00 (Simples Nacional), NT 2026.006 v1.01 (vinculação de pagamento) and NT 2026.008 v1.01 (valor líquido) on top of `PL_010f` | **Current schema** | `[Verified locally — 2026-11-16]`. Folders `NFe/` and `Evento/`. Delta vs `PL_010f`: `emit/tpRegimeIBSCBS`, `prod/cAtivSN`, `prod/vUnComLiq`+`vProdLiq`, `total/vProdLiqTot`, `infNFe/gPgtoVinc` (`TPgtoVinc`), `gTribSN` (item `TTribNFe` and `TIBSCBSMonoTot`), `ICMSPrevistoPagtoAntecip` + `vICMSPrevisto` as an alternative inside the ICMS choice, `gIBSCBS` becoming optional in `TTribNFe`. New event schemas: `e110300` (vinculação de pagamento), `e412140` (tributação do Simples Nacional), `e110001` (cancelamento de evento). The bundled runtime `leiauteNFe_v4.00.xsd`, `DFeTiposBasicos_v1.00.xsd` and `tiposBasico_v4.00.xsd` were replaced wholesale with the official files (LF line endings); the `_unsigned` derivative patches only the `ds:Signature` of `TNFe`. |
| `xsd_distdfe_v1.04/` | PL_NFeDistDFe_104 (distribution webservice release, 03/07/2026, official) | No code change needed | `distDFeInt_v1.01.xsd` payload shape (`tpAmb`/`cUFAutor`/`CNPJ`|`CPF`/`distNSU`|`consNSU`|`consChNFe`) is byte-identical in substance to what `SefazClient`'s `NFeDistribuicaoDFe` builder already implements (`[Verified locally — 2026-08-14]`). |
| `xsd_eventos_rtc/` | Eventos_RTC (17 event XSDs, NT 2025.002-RTC) | `[NEED: not yet reviewed]` | Sourced 2026-08-14 but belongs to the separately-tracked IBS/CBS effort, not this item — deferred with the rest of the RTC event modeling. |

`cIndOp`/`ISUFEmit` are **not documented anywhere in NT 2026.002 or NT 2026.003** — they
were found only by diffing the official XSD directly against `PL_010d`. Working
hypothesis: they belong to NT 2025.002-RTC (IBS/CBS place-of-supply / Zona Franca de
Manaus) and were bundled into the 010e release opportunistically, not because they are
DANFE-Tipo-2-specific. `[NEED: confirm against NT 2025.002 v1.50+ text — not yet
cross-checked]`.

## PDFs (gitignored — see `*.pdf` entries in `.gitignore`)

| File | Covers |
|---|---|
| `Manual de Orientação ao Contribuinte - MOC - versão 7.0 - NF-e e NFC-e.pdf` | Primary MOC — overall NF-e/NFC-e orientation |
| `ANEXO I - Leiaute e Regra de Validação - NF-e e NFC-e.pdf` | Field-by-field layout and validation rules |
| `ANEXO II -Manual EspecificaçõesTécnicas - Danfe-Código-Barras.pdf` | DANFE barcode spec |
| `Anexo III - Manual de Contingência - NF-e.pdf` | NF-e contingency modes |
| `Anexo IV - Manual de Contingência - NFC-e.pdf` | NFC-e contingency modes |
| `NT2014.002_v1.30 - WsNFeDistribuicaoDFe.pdf` | Distribution/query webservice — needed for submission/query tools |
| `NT_2025.002_v1.50_RTC_NF-e_IBS_CBS_IS.pdf` | Tax reform (IBS/CBS/IS) layout and validation-rule changes |
| `NFe_NT_2026.005_v1.00_RTC_SimplesNacional.pdf` | NT 2026.005 v1.00 — `tpRegimeIBSCBS` (C21a), `cAtivSN` (I17d), `gTribSN` item/total groups, Evento 412140 (future). Production 2026-11-16. |
| `NFe_NT_2026.006_v1.01_RTC_VinculacaoPagamento.pdf` | NT 2026.006 v1.01 — group YC `gPgtoVinc` (split payment, preparatory) and Evento 110300. Production 2026-11-16 (v1.01 date change). |
| `NFe_NT_2026.008_v1.01_RTC_ValorLiquido.pdf` | NT 2026.008 v1.01 — `vUnComLiq`/`vProdLiq`, `vProdLiqTot`, `ICMSPrevistoPagtoAntecip` (NB01, rule NB01-30 from 2027-03-01). Production 2026-11-16 except NB01-30. |
| `NFe_NT_2026.010_v1_00_DANFE_RTC.pdf` | NT 2026.010 v1.00 — DANFE layout for IBS/CBS/IS. Out of scope: this package renders no DANFE. |
| `NFe_NT_2025.002_v1.53_RTC_NF-e_IBS_CBS_IS.pdf` | NT 2025.002 v1.53 (supersedes v1.50 as the RTC reference; not yet diffed). |
| `NFe_NT2026.007_v1.11 - Emissão NF-e sem IE.pdf` | NT 2026.007 v1.11 (IE-optional issuance; supersedes v1.00). |
| `NT_2026.002_v1.11_DANFE_Simpl_Tp2_Emi_Offline_Autoriz_Alerta.pdf` | NT 2026.002 v1.11 — only moves validation-rule production dates (some to 2026-12-14). |
| `NFe_NT2023.002_v1.02.pdf` | NT 2023.002 v1.02 (Oct 2026) — NFC-e CPF issuer with IE, elimination of asynchronous authorization and of the inutilização services. `[NEED: not yet read in full; may affect the package's inutilização handling]` |
| `Tabela IT 2025.002 v.1.71 - cClassTrib.xlsx` | cClassTrib table v1.71 (also copied under `specs/cte/`). |
| `NT_2026.004_v1.01_AlteraSchemaNFCeNFeCNPJAlfa.pdf` | CNPJ alfanumérico schema changes (source for `xsd_pl010d_cnpj_alfa/`) |
| `DFe NTCJ 2025.001_CNPJ Alfa_v1.00.pdf` | NT Conjunta DFe 2025.001 v1.00 (25 April 2025) — primary source for alphanumeric CNPJ check-digit algorithm; includes JS + VB.NET reference implementations (Annex I/II) |
| `NT_2024.003- Produtos AGRO NF-e - v 1.10_Rev.pdf` | Agricultural products fields |
| `NT_2020.001 v1.60 - Manifestação do destinatário.pdf` | Recipient manifestation events |
| `NT2022.002v1.30a - Equiparação Exportação e outras alterações.pdf` | Export equivalence and other changes (source for `xsd/` PL_010c) |
| `NT_2026.002_v1.00.pdf` | "NFCe/NFe - Emissão Offline, Autorização com Alerta e DANFE Simplificado Tipo 2" — new `tpImp=6`, redefines `tpEmis=9` and `indPres=4`, new `cStat=120` "autorizado com alerta" status and alert-message group (0-5 occurrences), CFOP/item-group business-rule restrictions when `tpImp=6`. Cronograma: phase 1 (W16-40) test 01/06/2026 / prod 15/06/2026; phase 2 (DANFE Tipo 2 field-level changes) test 01/07/2026 / **prod 03/08/2026 — already in effect**; phase 3 (alert structure, `cStat=120`) test 01/09/2026 / prod 05/10/2026 — not yet in effect. |
| `NT_2026.002_v1.10_DANFE_Simpl_Tp2.pdf` | Same NT, version 1.10 (07/2026). Leiaute table (tpImp/tpEmis/indPres/cIndOp/ISUFEmit) is **identical** to v1.00 — only the validation-rule catalogue (§4) changed: rule `BA02-35` (and new companion `VC02-40`) moved from the 03/08/2026 wave to 05/10/2026; `VC02-50`/`W16-40`/`W16-50`/`W16-60` likewise deferred; 11 rules removed entirely (`BA05-10`, `BA06-10`, `BA12-10`-`BA15-10`, `BA20-10`, `BA20-20`, `I08-184`, `I08-186`, `VC02-50`). No impact on `mcp-nfe-br` since the business-rule catalogue is not enforced by the XSD-only validator. |
| `NT_2026.003_v1.00 - DANFE Simplificado Tipo 2.pdf` | Printed auxiliary-document (DANFE) layout, QR-code composition (incl. new offline URL parameters), and public-consultation spec for DANFE Simplificado Tipo 2. Instituted by Ajuste SINIEF nº 13, 6 April 2026. Same cronograma as NT 2026.002 phase 2 (prod 03/08/2026). Out of `mcp-nfe-br` code scope — this package does not render DANFE PDFs; relevant only if a DANFE-rendering tool is ever added. |
| `NT_2026.001_v1.02a - PAA NFe.pdf` | Padrão de Assinatura Avançada (PAA) — digital-certificate standard for advanced signature on behalf of the emitente. Read for BR-INV-3 (ICP-Brasil certificate retirement); does not mention "V10" or any certificate-chain retirement timeline. |
| `MCT10Vol.IIv.3.0.pdf` | ICP-Brasil "Manual de Condutas Técnicas 10 — Volume II" (Carimbo do Tempo/timestamp-authority conformance testing), v3.0, 2021-11-10. Not NF-e-specific. Read for BR-INV-3; the only "V.10" hits are a requirement-numbering label (`REQUISITO V.10`), unrelated to certificate-chain versioning. Does not cover certificate retirement. |

## Not yet retrieved

- Instrução Normativa RFB nº 2.229/2024 (CNPJ alfanumérico, primary text — not yet retrieved)
- Lei Complementar 214/2025 (Reforma Tributária do Consumo, primary text)
- A primary ITI/ICP-Brasil document describing the "V10 certificate chain" retirement claimed by secondary sources (tecnospeed.com.br, portalspedbrasil.com.br forum). Not found in any document supplied so far — see BR-INV-3 in `br.md` for current status.
