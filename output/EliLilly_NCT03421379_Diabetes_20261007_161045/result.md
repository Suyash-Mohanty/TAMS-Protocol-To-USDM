# Pipeline Result: EliLilly_NCT03421379_Diabetes

**Status:** SUCCESS
**PDF:** `EliLilly_NCT03421379_Diabetes.pdf`
**Model:** cortex/reforge-claude-opus-5
**Started:** 2026-10-07 16:10:45
**Finished:** 2026-10-07 16:15:07
**Duration:** 261.8s
**Entities:** 710
**Waves:** 4

## Statistics

| Metric | Value |
|--------|-------|
| Total Agents | 21 |
| Succeeded | 21 |
| Failed | 0 |
| Total Entities | 710 |
| Total Tokens | 221,092 |
| Total API Calls | 79 |
| Total Duration | 261.8s |

## Execution Flow

```
Wave 0  (51.4s)
  [OK] docstructure_agent (51.4s)  ->  05_extraction_document_structure.json
  [OK] metadata_agent (14.8s)  ->  01_extraction_metadata.json
  [OK] narrative_agent (26.2s)  ->  04_extraction_narrative.json
  [OK] pdf-parser (2.0s)
  [OK] provenance (0.0s)  ->  20_support_provenance.json
  [OK] soa_vision_agent (28.3s)  ->  02_extraction_soa_vision.json
  [OK] usdm-generator (0.6s)  ->  19_support_usdm_generator.json
  |
Wave 1  (66.6s)
  [OK] advanced_agent (5.4s)  ->  13_extraction_advanced_entities.json
  [OK] eligibility_agent (66.6s)  ->  06_extraction_eligibility.json
  [OK] objectives_agent (35.1s)  ->  07_extraction_objectives.json
  [OK] procedures_agent (56.0s)  ->  09_extraction_procedures_devices.json
  [OK] soa_text_agent (50.7s)  ->  03_extraction_soa_text.json
  [OK] studydesign_agent (12.2s)  ->  08_extraction_study_design.json
  |
Wave 2  (130.5s)
  [OK] biomedical_concept_agent (70.0s)  ->  14_extraction_biomedical_concepts.json
  [OK] execution_agent (130.5s)  ->  12_extraction_execution_model.json
  [OK] interventions_agent (28.3s)  ->  10_extraction_interventions.json
  [OK] scheduling_agent (87.6s)  ->  11_extraction_scheduling_logic.json
  |
Wave 3  (3.9s)
  [OK] enrichment_agent (3.9s)  ->  18_quality_enrichment.json
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
| 01 | metadata_agent | extraction | OK | 14.8 | 3,928 | 1 | 0-2 | `01_extraction_metadata.json` |
| 02 | soa_vision_agent | extraction | OK | 28.3 | 19,158 | 1 | 10-19 | `02_extraction_soa_vision.json` |
| 03 | soa_text_agent | extraction | OK | 50.7 | 17,248 | 1 | 10-19 | `03_extraction_soa_text.json` |
| 04 | narrative_agent | extraction | OK | 26.2 | 12,043 | 2 | 2,7-8,10,18,22-24 | `04_extraction_narrative.json` |
| 05 | docstructure_agent | extraction | OK | 51.4 | 12,220 | 1 | 0-4,7,15,35-36,39-40,43 | `05_extraction_document_structure.json` |
| 06 | eligibility_agent | extraction | OK | 66.6 | 12,981 | 1 | 24-28 | `06_extraction_eligibility.json` |
| 07 | objectives_agent | extraction | OK | 35.1 | 8,460 | 2 | 8-10 | `07_extraction_objectives.json` |
| 08 | studydesign_agent | extraction | OK | 12.2 | 12,705 | 1 | 1-12,19-25 | `08_extraction_study_design.json` |
| 09 | procedures_agent | extraction | OK | 56.0 | 16,735 | 1 | 3,8,12-16,18-25 | `09_extraction_procedures_devices.json` |
| 10 | interventions_agent | extraction | OK | 28.3 | 31,903 | 1 | 2-20,22-49 | `10_extraction_interventions.json` |
| 11 | scheduling_agent | extraction | OK | 87.6 | 20,284 | 1 | 3,9,11-18,23,34,57 | `11_extraction_scheduling_logic.json` |
| 12 | execution_agent | extraction | OK | 130.5 | 36,859 | 12 | 0-41,43-51,57,62-63,70,72 | `12_extraction_execution_model.json` |
| 13 | advanced_agent | extraction | OK | 5.4 | 4,868 | 1 | 0-3,7,9 | `13_extraction_advanced_entities.json` |
| 14 | biomedical_concept_agent | extraction | OK | 70.0 | 11,700 | 1 |  | `14_extraction_biomedical_concepts.json` |
| 15 | postprocessing_agent | quality | OK | 0.0 | 0 | 0 |  | `15_quality_postprocessing.json` |
| 16 | reconciliation_agent | quality | OK | 0.2 | 0 | 0 |  | `16_quality_reconciliation.json` |
| 17 | validation_agent | quality | OK | 0.0 | 0 | 0 |  | `17_quality_validation.json` |
| 18 | enrichment_agent | quality | OK | 3.9 | 0 | 52 |  | `18_quality_enrichment.json` |
| 19 | usdm-generator | support | OK | 0.6 | 0 | 0 |  | `19_support_usdm_generator.json` |
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
