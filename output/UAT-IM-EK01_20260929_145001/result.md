# Pipeline Result: UAT-IM-EK01

**Status:** SUCCESS
**PDF:** `UAT-IM-EK01.pdf`
**Model:** cortex/reforge-claude-opus-5
**Started:** 2026-09-29 14:50:01
**Finished:** 2026-09-29 14:58:07
**Duration:** 486.2s
**Entities:** 1034
**Waves:** 4

## Statistics

| Metric | Value |
|--------|-------|
| Total Agents | 21 |
| Succeeded | 21 |
| Failed | 0 |
| Total Entities | 1034 |
| Total Tokens | 291,259 |
| Total API Calls | 87 |
| Total Duration | 486.2s |

## Execution Flow

```
Wave 0  (123.9s)
  [OK] docstructure_agent (123.9s)  ->  05_extraction_document_structure.json
  [OK] metadata_agent (15.3s)  ->  01_extraction_metadata.json
  [OK] narrative_agent (41.0s)  ->  04_extraction_narrative.json
  [OK] pdf-parser (2.1s)
  [OK] provenance (0.0s)  ->  20_support_provenance.json
  [OK] soa_vision_agent (73.1s)  ->  02_extraction_soa_vision.json
  [OK] usdm-generator (0.4s)  ->  19_support_usdm_generator.json
  |
Wave 1  (134.3s)
  [OK] advanced_agent (3.0s)  ->  13_extraction_advanced_entities.json
  [OK] eligibility_agent (25.9s)  ->  06_extraction_eligibility.json
  [OK] objectives_agent (106.8s)  ->  07_extraction_objectives.json
  [OK] procedures_agent (71.1s)  ->  09_extraction_procedures_devices.json
  [OK] soa_text_agent (134.3s)  ->  03_extraction_soa_text.json
  [OK] studydesign_agent (13.2s)  ->  08_extraction_study_design.json
  |
Wave 2  (188.9s)
  [OK] biomedical_concept_agent (188.9s)  ->  14_extraction_biomedical_concepts.json
  [OK] execution_agent (110.7s)  ->  12_extraction_execution_model.json
  [OK] interventions_agent (17.6s)  ->  10_extraction_interventions.json
  [OK] scheduling_agent (66.3s)  ->  11_extraction_scheduling_logic.json
  |
Wave 3  (9.6s)
  [OK] enrichment_agent (9.6s)  ->  18_quality_enrichment.json
  [OK] postprocessing_agent (0.0s)  ->  15_quality_postprocessing.json
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
| 01 | metadata_agent | extraction | OK | 15.3 | 4,878 | 1 | 0-2 | `01_extraction_metadata.json` |
| 02 | soa_vision_agent | extraction | OK | 73.1 | 24,279 | 1 | 8-17 | `02_extraction_soa_vision.json` |
| 03 | soa_text_agent | extraction | OK | 134.3 | 35,869 | 1 | 8-17 | `03_extraction_soa_text.json` |
| 04 | narrative_agent | extraction | OK | 41.0 | 18,486 | 2 | 2,5-9,16,19,21,26 | `04_extraction_narrative.json` |
| 05 | docstructure_agent | extraction | OK | 123.9 | 24,123 | 1 | 0-5,9,11-12,16-17,19-20,31,42,44,49 | `05_extraction_document_structure.json` |
| 06 | eligibility_agent | extraction | OK | 25.9 | 8,913 | 1 | 8-10,29-31 | `06_extraction_eligibility.json` |
| 07 | objectives_agent | extraction | OK | 106.8 | 38,999 | 2 | 1-16,25-28 | `07_extraction_objectives.json` |
| 08 | studydesign_agent | extraction | OK | 13.2 | 16,277 | 1 | 0-18,27-29 | `08_extraction_study_design.json` |
| 09 | procedures_agent | extraction | OK | 71.1 | 20,304 | 1 | 3-5,9-10,12,14,16-17,19,21,24,31,34-35 | `09_extraction_procedures_devices.json` |
| 10 | interventions_agent | extraction | OK | 17.6 | 23,908 | 1 | 1-10,13-25,27-29,33-43 | `10_extraction_interventions.json` |
| 11 | scheduling_agent | extraction | OK | 66.3 | 14,442 | 1 | 3,14,31,36,38,41 | `11_extraction_scheduling_logic.json` |
| 12 | execution_agent | extraction | OK | 110.7 | 30,776 | 11 | 0-41,43-45,53-55,68-69,71,73 | `12_extraction_execution_model.json` |
| 13 | advanced_agent | extraction | OK | 3.0 | 3,600 | 1 | 0-3 | `13_extraction_advanced_entities.json` |
| 14 | biomedical_concept_agent | extraction | OK | 188.9 | 26,405 | 2 |  | `14_extraction_biomedical_concepts.json` |
| 15 | postprocessing_agent | quality | OK | 0.0 | 0 | 0 |  | `15_quality_postprocessing.json` |
| 16 | reconciliation_agent | quality | OK | 0.4 | 0 | 0 |  | `16_quality_reconciliation.json` |
| 17 | validation_agent | quality | OK | 0.0 | 0 | 0 |  | `17_quality_validation.json` |
| 18 | enrichment_agent | quality | OK | 9.6 | 0 | 60 |  | `18_quality_enrichment.json` |
| 19 | usdm-generator | support | OK | 0.4 | 0 | 0 |  | `19_support_usdm_generator.json` |
| 20 | provenance | support | OK | 0.0 | 0 | 0 |  | `20_support_provenance.json` |
| 00 | pdf-parser | support | OK | 2.1 | 0 | 0 | | |

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
