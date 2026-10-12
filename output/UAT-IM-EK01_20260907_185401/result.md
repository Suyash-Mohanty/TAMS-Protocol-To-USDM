# Pipeline Result: UAT-IM-EK01

**Status:** SUCCESS
**PDF:** `UAT-IM-EK01.pdf`
**Model:** cortex/reforge-claude-opus-5
**Started:** 2026-09-07 18:54:01
**Finished:** 2026-09-07 19:01:18
**Duration:** 437.2s
**Entities:** 999
**Waves:** 4

## Statistics

| Metric | Value |
|--------|-------|
| Total Agents | 21 |
| Succeeded | 21 |
| Failed | 0 |
| Total Entities | 999 |
| Total Tokens | 287,508 |
| Total API Calls | 94 |
| Total Duration | 437.2s |

## Execution Flow

```
Wave 0  (89.9s)
  [OK] docstructure_agent (89.9s)  ->  05_extraction_document_structure.json
  [OK] metadata_agent (17.1s)  ->  01_extraction_metadata.json
  [OK] narrative_agent (43.2s)  ->  04_extraction_narrative.json
  [OK] pdf-parser (2.7s)
  [OK] provenance (0.0s)  ->  20_support_provenance.json
  [OK] soa_vision_agent (75.9s)  ->  02_extraction_soa_vision.json
  [OK] usdm-generator (1.7s)  ->  19_support_usdm_generator.json
  |
Wave 1  (134.2s)
  [OK] advanced_agent (2.8s)  ->  13_extraction_advanced_entities.json
  [OK] eligibility_agent (27.0s)  ->  06_extraction_eligibility.json
  [OK] objectives_agent (87.2s)  ->  07_extraction_objectives.json
  [OK] procedures_agent (80.9s)  ->  09_extraction_procedures_devices.json
  [OK] soa_text_agent (134.2s)  ->  03_extraction_soa_text.json
  [OK] studydesign_agent (11.4s)  ->  08_extraction_study_design.json
  |
Wave 2  (165.5s)
  [OK] biomedical_concept_agent (165.5s)  ->  14_extraction_biomedical_concepts.json
  [OK] execution_agent (104.0s)  ->  12_extraction_execution_model.json
  [OK] interventions_agent (15.3s)  ->  10_extraction_interventions.json
  [OK] scheduling_agent (62.0s)  ->  11_extraction_scheduling_logic.json
  |
Wave 3  (11.2s)
  [OK] enrichment_agent (11.2s)  ->  18_quality_enrichment.json
  [OK] postprocessing_agent (0.3s)  ->  15_quality_postprocessing.json
  [OK] reconciliation_agent (0.4s)  ->  16_quality_reconciliation.json
  [OK] validation_agent (0.0s)  ->  17_quality_validation.json
  |
Output
  [OK] UAT-IM-EK01_usdm.json
  [OK] UAT-IM-EK01_provenance.json
```

## Agent Results

| Step | Agent | Category | Status | Time (s) | Tokens | API Calls | Pages | Output File |
|------|-------|----------|--------|----------|--------|-----------|-------|-------------|
| 01 | metadata_agent | extraction | OK | 17.1 | 4,874 | 1 | 0-2 | `01_extraction_metadata.json` |
| 02 | soa_vision_agent | extraction | OK | 75.9 | 24,353 | 1 | 8-17 | `02_extraction_soa_vision.json` |
| 03 | soa_text_agent | extraction | OK | 134.2 | 37,630 | 1 | 8-17 | `03_extraction_soa_text.json` |
| 04 | narrative_agent | extraction | OK | 43.2 | 17,888 | 2 | 2,5-9,16,19,21,26 | `04_extraction_narrative.json` |
| 05 | docstructure_agent | extraction | OK | 89.9 | 19,953 | 1 | 0-5,9,11-12,16-17,19-20,31,42,44,49 | `05_extraction_document_structure.json` |
| 06 | eligibility_agent | extraction | OK | 27.0 | 8,901 | 1 | 8-10,29-31 | `06_extraction_eligibility.json` |
| 07 | objectives_agent | extraction | OK | 87.2 | 36,534 | 2 | 1-16,25-28 | `07_extraction_objectives.json` |
| 08 | studydesign_agent | extraction | OK | 11.4 | 16,291 | 1 | 0-18,27-29 | `08_extraction_study_design.json` |
| 09 | procedures_agent | extraction | OK | 80.9 | 21,248 | 1 | 3-5,9-10,12,14,16-17,19,21,24,31,34-35 | `09_extraction_procedures_devices.json` |
| 10 | interventions_agent | extraction | OK | 15.3 | 23,975 | 1 | 1-10,13-25,27-29,33-43 | `10_extraction_interventions.json` |
| 11 | scheduling_agent | extraction | OK | 62.0 | 13,601 | 1 | 3,14,31,36,38,41 | `11_extraction_scheduling_logic.json` |
| 12 | execution_agent | extraction | OK | 104.0 | 30,448 | 11 | 0-41,43-45,53-55,68-69,71,73 | `12_extraction_execution_model.json` |
| 13 | advanced_agent | extraction | OK | 2.8 | 3,600 | 1 | 0-3 | `13_extraction_advanced_entities.json` |
| 14 | biomedical_concept_agent | extraction | OK | 165.5 | 28,212 | 2 |  | `14_extraction_biomedical_concepts.json` |
| 15 | postprocessing_agent | quality | OK | 0.3 | 0 | 0 |  | `15_quality_postprocessing.json` |
| 16 | reconciliation_agent | quality | OK | 0.4 | 0 | 0 |  | `16_quality_reconciliation.json` |
| 17 | validation_agent | quality | OK | 0.0 | 0 | 0 |  | `17_quality_validation.json` |
| 18 | enrichment_agent | quality | OK | 11.2 | 0 | 67 |  | `18_quality_enrichment.json` |
| 19 | usdm-generator | support | OK | 1.7 | 0 | 0 |  | `19_support_usdm_generator.json` |
| 20 | provenance | support | OK | 0.0 | 0 | 0 |  | `20_support_provenance.json` |
| 00 | pdf-parser | support | OK | 2.7 | 0 | 0 | | |

## Output Files

- `01_extraction_metadata.json`
- `02_extraction_soa_vision.json`
- `03_extraction_soa_text.json`
- `04_extraction_narrative.json`
- `05_extraction_document_structure.json`
- `06_extraction_eligibility.json`
- `07_extraction_objectives.json`
- `08_extraction_study_design.json`
- `09_extraction_procedures_devices.json`
- `10_extraction_interventions.json`
- `11_extraction_scheduling_logic.json`
- `12_extraction_execution_model.json`
- `13_extraction_advanced_entities.json`
- `14_extraction_biomedical_concepts.json`
- `15_quality_postprocessing.json`
- `16_quality_reconciliation.json`
- `17_quality_validation.json`
- `18_quality_enrichment.json`
- `19_support_usdm_generator.json`
- `20_support_provenance.json`
- `9_final_soa_provenance.json`
- `UAT-IM-EK01.pdf`
- `UAT-IM-EK01_provenance.json`
- `UAT-IM-EK01_usdm.json`
- `conformance_report.json`
- `id_mapping.json`
- `soa_page_009.png`
- `soa_page_010.png`
- `soa_page_011.png`
- `soa_page_012.png`
- `soa_page_013.png`
- `soa_page_014.png`
- `soa_page_015.png`
- `soa_page_016.png`
- `soa_page_017.png`
- `soa_page_018.png`
