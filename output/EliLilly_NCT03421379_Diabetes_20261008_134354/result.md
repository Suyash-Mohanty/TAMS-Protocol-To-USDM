# Pipeline Result: EliLilly_NCT03421379_Diabetes

**Status:** SUCCESS
**PDF:** `EliLilly_NCT03421379_Diabetes.pdf`
**Model:** cortex/reforge-claude-opus-5
**Started:** 2026-10-08 13:43:54
**Finished:** 2026-10-08 13:52:30
**Duration:** 515.9s
**Entities:** 804
**Waves:** 4

## Statistics

| Metric | Value |
|--------|-------|
| Total Agents | 21 |
| Succeeded | 21 |
| Failed | 0 |
| Total Entities | 804 |
| Total Tokens | 258,887 |
| Total API Calls | 74 |
| Total Duration | 515.9s |

## Execution Flow

```
Wave 0  (54.0s)
  [OK] docstructure_agent (49.7s)  ->  05_extraction_document_structure.json
  [OK] metadata_agent (6.8s)  ->  01_extraction_metadata.json
  [OK] narrative_agent (52.0s)  ->  04_extraction_narrative.json
  [OK] pdf-parser (1.8s)
  [OK] provenance (0.0s)  ->  20_support_provenance.json
  [OK] soa_vision_agent (54.0s)  ->  02_extraction_soa_vision.json
  [OK] usdm-generator (0.4s)  ->  19_support_usdm_generator.json
  |
Wave 1  (79.9s)
  [OK] advanced_agent (27.1s)  ->  13_extraction_advanced_entities.json
  [OK] eligibility_agent (79.9s)  ->  06_extraction_eligibility.json
  [OK] objectives_agent (62.3s)  ->  07_extraction_objectives.json
  [OK] procedures_agent (61.4s)  ->  09_extraction_procedures_devices.json
  [OK] soa_text_agent (46.9s)  ->  03_extraction_soa_text.json
  [OK] studydesign_agent (14.7s)  ->  08_extraction_study_design.json
  |
Wave 2  (351.2s)
  [OK] biomedical_concept_agent (72.0s)  ->  14_extraction_biomedical_concepts.json
  [OK] execution_agent (351.2s)  ->  12_extraction_execution_model.json
  [OK] interventions_agent (36.2s)  ->  10_extraction_interventions.json
  [OK] scheduling_agent (107.0s)  ->  11_extraction_scheduling_logic.json
  |
Wave 3  (2.9s)
  [OK] enrichment_agent (2.9s)  ->  18_quality_enrichment.json
  [OK] postprocessing_agent (0.0s)  ->  15_quality_postprocessing.json
  [OK] reconciliation_agent (0.2s)  ->  16_quality_reconciliation.json
  [OK] validation_agent (0.0s)  ->  17_quality_validation.json
  |
Output
  [OK] EliLilly_NCT03421379_Diabetes_usdm.json
  [OK] EliLilly_NCT03421379_Diabetes_provenance.json
```

## Agent Results

| Step | Agent | Category | Status | Time (s) | Tokens | API Calls | Pages | Output File |
|------|-------|----------|--------|----------|--------|-----------|-------|-------------|
| 01 | metadata_agent | extraction | OK | 6.8 | 3,928 | 1 | 0-2 | `01_extraction_metadata.json` |
| 02 | soa_vision_agent | extraction | OK | 54.0 | 32,547 | 2 | 10-19 | `02_extraction_soa_vision.json` |
| 03 | soa_text_agent | extraction | OK | 46.9 | 16,599 | 1 | 10-19 | `03_extraction_soa_text.json` |
| 04 | narrative_agent | extraction | OK | 52.0 | 20,611 | 2 | 2-4,7-8,10,18,22-24,53-57 | `04_extraction_narrative.json` |
| 05 | docstructure_agent | extraction | OK | 49.7 | 12,265 | 1 | 0-4,7,15,35-36,39-40,43 | `05_extraction_document_structure.json` |
| 06 | eligibility_agent | extraction | OK | 79.9 | 14,580 | 1 | 24-29 | `06_extraction_eligibility.json` |
| 07 | objectives_agent | extraction | OK | 62.3 | 17,799 | 2 | 8-10,21-23,46-48 | `07_extraction_objectives.json` |
| 08 | studydesign_agent | extraction | OK | 14.7 | 12,934 | 1 | 1-12,19-25 | `08_extraction_study_design.json` |
| 09 | procedures_agent | extraction | OK | 61.4 | 17,017 | 1 | 3,8,12-16,18-25 | `09_extraction_procedures_devices.json` |
| 10 | interventions_agent | extraction | OK | 36.2 | 32,782 | 1 | 2-20,22-49 | `10_extraction_interventions.json` |
| 11 | scheduling_agent | extraction | OK | 107.0 | 23,323 | 1 | 3,9,11-18,23,34,57 | `11_extraction_scheduling_logic.json` |
| 12 | execution_agent | extraction | OK | 351.2 | 36,398 | 12 | 0-41,43-51,57,62-63,70,72 | `12_extraction_execution_model.json` |
| 13 | advanced_agent | extraction | OK | 27.1 | 5,992 | 1 | 0-3,7,9,71-72 | `13_extraction_advanced_entities.json` |
| 14 | biomedical_concept_agent | extraction | OK | 72.0 | 12,112 | 1 |  | `14_extraction_biomedical_concepts.json` |
| 15 | postprocessing_agent | quality | OK | 0.0 | 0 | 0 |  | `15_quality_postprocessing.json` |
| 16 | reconciliation_agent | quality | OK | 0.2 | 0 | 0 |  | `16_quality_reconciliation.json` |
| 17 | validation_agent | quality | OK | 0.0 | 0 | 0 |  | `17_quality_validation.json` |
| 18 | enrichment_agent | quality | OK | 2.9 | 0 | 46 |  | `18_quality_enrichment.json` |
| 19 | usdm-generator | support | OK | 0.4 | 0 | 0 |  | `19_support_usdm_generator.json` |
| 20 | provenance | support | OK | 0.0 | 0 | 0 |  | `20_support_provenance.json` |
| 00 | pdf-parser | support | OK | 1.8 | 0 | 0 | | |

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
- `EliLilly_NCT03421379_Diabetes.pdf`
- `EliLilly_NCT03421379_Diabetes_provenance.json`
- `EliLilly_NCT03421379_Diabetes_usdm.json`
- `conformance_report.json`
- `id_mapping.json`
- `soa_page_011.png`
- `soa_page_012.png`
- `soa_page_013.png`
- `soa_page_014.png`
- `soa_page_015.png`
- `soa_page_016.png`
- `soa_page_017.png`
- `soa_page_018.png`
- `soa_page_019.png`
- `soa_page_020.png`
- `usdm_validation.json`
