# Pipeline Result: EliLilly_NCT03421379_Diabetes

**Status:** SUCCESS
**PDF:** `EliLilly_NCT03421379_Diabetes.pdf`
**Model:** cortex/reforge-claude-opus-5
**Started:** 2026-10-07 18:01:36
**Finished:** 2026-10-07 18:06:12
**Duration:** 275.2s
**Entities:** 795
**Waves:** 4

## Statistics

| Metric | Value |
|--------|-------|
| Total Agents | 21 |
| Succeeded | 21 |
| Failed | 0 |
| Total Entities | 795 |
| Total Tokens | 245,981 |
| Total API Calls | 69 |
| Total Duration | 275.2s |

## Execution Flow

```
Wave 0  (57.4s)
  [OK] docstructure_agent (47.5s)  ->  05_extraction_document_structure.json
  [OK] metadata_agent (10.2s)  ->  01_extraction_metadata.json
  [OK] narrative_agent (57.4s)  ->  04_extraction_narrative.json
  [OK] pdf-parser (2.0s)
  [OK] provenance (0.0s)  ->  20_support_provenance.json
  [OK] soa_vision_agent (24.7s)  ->  02_extraction_soa_vision.json
  [OK] usdm-generator (2.3s)  ->  19_support_usdm_generator.json
  |
Wave 1  (77.1s)
  [OK] advanced_agent (7.5s)  ->  13_extraction_advanced_entities.json
  [OK] eligibility_agent (77.1s)  ->  06_extraction_eligibility.json
  [OK] objectives_agent (54.9s)  ->  07_extraction_objectives.json
  [OK] procedures_agent (54.3s)  ->  09_extraction_procedures_devices.json
  [OK] soa_text_agent (52.9s)  ->  03_extraction_soa_text.json
  [OK] studydesign_agent (13.6s)  ->  08_extraction_study_design.json
  |
Wave 2  (129.5s)
  [OK] biomedical_concept_agent (73.9s)  ->  14_extraction_biomedical_concepts.json
  [OK] execution_agent (129.5s)  ->  12_extraction_execution_model.json
  [OK] interventions_agent (30.7s)  ->  10_extraction_interventions.json
  [OK] scheduling_agent (110.3s)  ->  11_extraction_scheduling_logic.json
  |
Wave 3  (2.8s)
  [OK] enrichment_agent (2.8s)  ->  18_quality_enrichment.json
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
| 01 | metadata_agent | extraction | OK | 10.2 | 3,928 | 1 | 0-2 | `01_extraction_metadata.json` |
| 02 | soa_vision_agent | extraction | OK | 24.7 | 19,130 | 1 | 10-19 | `02_extraction_soa_vision.json` |
| 03 | soa_text_agent | extraction | OK | 52.9 | 17,385 | 1 | 10-19 | `03_extraction_soa_text.json` |
| 04 | narrative_agent | extraction | OK | 57.4 | 20,586 | 2 | 2-4,7-8,10,18,22-24,53-57 | `04_extraction_narrative.json` |
| 05 | docstructure_agent | extraction | OK | 47.5 | 11,971 | 1 | 0-4,7,15,35-36,39-40,43 | `05_extraction_document_structure.json` |
| 06 | eligibility_agent | extraction | OK | 77.1 | 14,601 | 1 | 24-29 | `06_extraction_eligibility.json` |
| 07 | objectives_agent | extraction | OK | 54.9 | 18,292 | 2 | 8-10,21-23,46-48 | `07_extraction_objectives.json` |
| 08 | studydesign_agent | extraction | OK | 13.6 | 12,983 | 1 | 1-12,19-25 | `08_extraction_study_design.json` |
| 09 | procedures_agent | extraction | OK | 54.3 | 16,582 | 1 | 3,8,12-16,18-25 | `09_extraction_procedures_devices.json` |
| 10 | interventions_agent | extraction | OK | 30.7 | 32,583 | 1 | 2-20,22-49 | `10_extraction_interventions.json` |
| 11 | scheduling_agent | extraction | OK | 110.3 | 23,565 | 1 | 3,9,11-18,23,34,57 | `11_extraction_scheduling_logic.json` |
| 12 | execution_agent | extraction | OK | 129.5 | 36,448 | 12 | 0-41,43-51,57,62-63,70,72 | `12_extraction_execution_model.json` |
| 13 | advanced_agent | extraction | OK | 7.5 | 5,992 | 1 | 0-3,7,9,71-72 | `13_extraction_advanced_entities.json` |
| 14 | biomedical_concept_agent | extraction | OK | 73.9 | 11,935 | 1 |  | `14_extraction_biomedical_concepts.json` |
| 15 | postprocessing_agent | quality | OK | 0.0 | 0 | 0 |  | `15_quality_postprocessing.json` |
| 16 | reconciliation_agent | quality | OK | 0.2 | 0 | 0 |  | `16_quality_reconciliation.json` |
| 17 | validation_agent | quality | OK | 0.0 | 0 | 0 |  | `17_quality_validation.json` |
| 18 | enrichment_agent | quality | OK | 2.8 | 0 | 42 |  | `18_quality_enrichment.json` |
| 19 | usdm-generator | support | OK | 2.3 | 0 | 0 |  | `19_support_usdm_generator.json` |
| 20 | provenance | support | OK | 0.0 | 0 | 0 |  | `20_support_provenance.json` |
| 00 | pdf-parser | support | OK | 2.0 | 0 | 0 | | |

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
