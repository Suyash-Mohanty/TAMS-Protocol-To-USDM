# Pipeline Result: J3R-MC-YDAF

**Status:** SUCCESS
**PDF:** `J3R-MC-YDAF.pdf`
**Model:** cortex/reforge-claude-opus-5
**Started:** 2026-10-12 15:49:01
**Finished:** 2026-10-12 15:56:09
**Duration:** 427.5s
**Entities:** 1352
**Waves:** 4

## Statistics

| Metric | Value |
|--------|-------|
| Total Agents | 21 |
| Succeeded | 21 |
| Failed | 0 |
| Total Entities | 1352 |
| Total Tokens | 345,754 |
| Total API Calls | 76 |
| Total Duration | 427.5s |

## Execution Flow

```
Wave 0  (89.8s)
  [OK] docstructure_agent (89.8s)  ->  05_extraction_document_structure.json
  [OK] metadata_agent (40.2s)  ->  01_extraction_metadata.json
  [OK] narrative_agent (70.9s)  ->  04_extraction_narrative.json
  [OK] pdf-parser (5.0s)
  [OK] provenance (0.0s)  ->  20_support_provenance.json
  [OK] soa_vision_agent (56.4s)  ->  02_extraction_soa_vision.json
  [OK] usdm-generator (3.6s)  ->  19_support_usdm_generator.json
  |
Wave 1  (196.3s)
  [OK] advanced_agent (7.0s)  ->  13_extraction_advanced_entities.json
  [OK] eligibility_agent (79.8s)  ->  06_extraction_eligibility.json
  [OK] objectives_agent (196.3s)  ->  07_extraction_objectives.json
  [OK] procedures_agent (49.3s)  ->  09_extraction_procedures_devices.json
  [OK] soa_text_agent (71.2s)  ->  03_extraction_soa_text.json
  [OK] studydesign_agent (13.7s)  ->  08_extraction_study_design.json
  |
Wave 2  (111.2s)
  [OK] biomedical_concept_agent (47.7s)  ->  14_extraction_biomedical_concepts.json
  [OK] execution_agent (111.2s)  ->  12_extraction_execution_model.json
  [OK] interventions_agent (16.5s)  ->  10_extraction_interventions.json
  [OK] scheduling_agent (67.0s)  ->  11_extraction_scheduling_logic.json
  |
Wave 3  (4.8s)
  [OK] enrichment_agent (4.8s)  ->  18_quality_enrichment.json
  [OK] postprocessing_agent (0.0s)  ->  15_quality_postprocessing.json
  [OK] reconciliation_agent (1.2s)  ->  16_quality_reconciliation.json
  [OK] validation_agent (0.0s)  ->  17_quality_validation.json
  |
Output
  [OK] J3R-MC-YDAF_usdm.json
  [OK] J3R-MC-YDAF_provenance.json
```

## Agent Results

| Step | Agent | Category | Status | Time (s) | Tokens | API Calls | Pages | Output File |
|------|-------|----------|--------|----------|--------|-----------|-------|-------------|
| 01 | metadata_agent | extraction | OK | 40.2 | 4,076 | 1 | 0-2 | `01_extraction_metadata.json` |
| 02 | soa_vision_agent | extraction | OK | 56.4 | 33,227 | 1 | 13-15,45-49,79-81,83-89,101-102 | `02_extraction_soa_vision.json` |
| 03 | soa_text_agent | extraction | OK | 71.2 | 36,525 | 1 | 13-15,45-49,79-81,83-89,101-102 | `03_extraction_soa_text.json` |
| 04 | narrative_agent | extraction | OK | 70.9 | 25,060 | 2 | 4-9,12,14,16,23-24,148-150 | `04_extraction_narrative.json` |
| 05 | docstructure_agent | extraction | OK | 89.8 | 23,340 | 1 | 0-4,6-7,17,19-21,23,25-26,28,30,34,40,46-47 | `05_extraction_document_structure.json` |
| 06 | eligibility_agent | extraction | OK | 79.8 | 18,318 | 1 | 46-52 | `06_extraction_eligibility.json` |
| 07 | objectives_agent | extraction | OK | 196.3 | 67,341 | 2 | 7-11,37-45 | `07_extraction_objectives.json` |
| 08 | studydesign_agent | extraction | OK | 13.7 | 20,371 | 1 | 0-1,3-29 | `08_extraction_study_design.json` |
| 09 | procedures_agent | extraction | OK | 49.3 | 17,149 | 1 | 5,7,14-20,23,25-27,34,47 | `09_extraction_procedures_devices.json` |
| 10 | interventions_agent | extraction | OK | 16.5 | 31,795 | 1 | 0-24,26-28,31-48 | `10_extraction_interventions.json` |
| 11 | scheduling_agent | extraction | OK | 67.0 | 16,264 | 1 | 2,5,15,43-44,48,50-51 | `11_extraction_scheduling_logic.json` |
| 12 | execution_agent | extraction | OK | 111.2 | 36,030 | 11 | 0-44,46,48-49,51-53,56-57,59-62,65,67,71-72,74,79-80,84,88,97,100,103,123,143,157-158,162 | `12_extraction_execution_model.json` |
| 13 | advanced_agent | extraction | OK | 7.0 | 4,986 | 1 | 0-4,15 | `13_extraction_advanced_entities.json` |
| 14 | biomedical_concept_agent | extraction | OK | 47.7 | 11,272 | 1 |  | `14_extraction_biomedical_concepts.json` |
| 15 | postprocessing_agent | quality | OK | 0.0 | 0 | 0 |  | `15_quality_postprocessing.json` |
| 16 | reconciliation_agent | quality | OK | 1.2 | 0 | 0 |  | `16_quality_reconciliation.json` |
| 17 | validation_agent | quality | OK | 0.0 | 0 | 0 |  | `17_quality_validation.json` |
| 18 | enrichment_agent | quality | OK | 4.8 | 0 | 50 |  | `18_quality_enrichment.json` |
| 19 | usdm-generator | support | OK | 3.6 | 0 | 0 |  | `19_support_usdm_generator.json` |
| 20 | provenance | support | OK | 0.0 | 0 | 0 |  | `20_support_provenance.json` |
| 00 | pdf-parser | support | OK | 5.0 | 0 | 0 | | |

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
- `J3R-MC-YDAF.pdf`
- `J3R-MC-YDAF_provenance.json`
- `J3R-MC-YDAF_usdm.json`
- `conformance_report.json`
- `id_mapping.json`
- `soa_page_014.png`
- `soa_page_015.png`
- `soa_page_016.png`
- `soa_page_046.png`
- `soa_page_047.png`
- `soa_page_048.png`
- `soa_page_049.png`
- `soa_page_050.png`
- `soa_page_080.png`
- `soa_page_081.png`
- `soa_page_082.png`
- `soa_page_084.png`
- `soa_page_085.png`
- `soa_page_086.png`
- `soa_page_087.png`
- `soa_page_088.png`
- `soa_page_089.png`
- `soa_page_090.png`
- `soa_page_102.png`
- `soa_page_103.png`
- `usdm_validation.json`
