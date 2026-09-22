# Pipeline Result: Alexion_NCT04573309_Wilsons

**Status:** FAILED
**PDF:** `Alexion_NCT04573309_Wilsons.pdf`
**Model:** cortex-claude
**Started:** 2026-09-01 12:54:11
**Finished:** 2026-09-01 13:00:52
**Duration:** 400.5s
**Entities:** 685
**Waves:** 3

## Statistics

| Metric | Value |
|--------|-------|
| Total Agents | 19 |
| Succeeded | 18 |
| Failed | 1 |
| Total Entities | 685 |
| Total Tokens | 223,434 |
| Total API Calls | 22 |
| Total Duration | 400.5s |

## Execution Flow

```
Wave 0  (100.9s)
  [OK] docstructure_agent (74.0s)  ->  05_extraction_document_structure.json
  [OK] execution_agent (100.9s)  ->  12_extraction_execution_model.json
  [OK] metadata_agent (10.0s)  ->  01_extraction_metadata.json
  [OK] narrative_agent (26.1s)  ->  04_extraction_narrative.json
  [OK] pdf-parser (0.8s)
  [OK] provenance (0.0s)  ->  20_support_provenance.json
  [OK] usdm-generator (0.1s)  ->  19_support_usdm_generator.json
  |
Wave 1  (114.4s)
  [OK] advanced_agent (8.0s)  ->  13_extraction_advanced_entities.json
  [OK] eligibility_agent (64.5s)  ->  06_extraction_eligibility.json
  [OK] enrichment_agent (0.8s)  ->  18_quality_enrichment.json
  [OK] objectives_agent (114.4s)  ->  07_extraction_objectives.json
  [OK] postprocessing_agent (0.0s)  ->  15_quality_postprocessing.json
  [OK] procedures_agent (47.3s)  ->  09_extraction_procedures_devices.json
  [OK] reconciliation_agent (0.1s)  ->  16_quality_reconciliation.json
  [OK] studydesign_agent (17.9s)  ->  08_extraction_study_design.json
  [OK] validation_agent (0.0s)  ->  17_quality_validation.json
  |
Wave 2  (126.9s)
  [FAIL] biomedical_concept_agent (0.0s)  ->  14_extraction_biomedical_concepts.json
  [OK] interventions_agent (26.0s)  ->  10_extraction_interventions.json
  [OK] scheduling_agent (126.9s)  ->  11_extraction_scheduling_logic.json
  |
Output
  [OK] Alexion_NCT04573309_Wilsons_usdm.json
  [OK] Alexion_NCT04573309_Wilsons_provenance.json
```

## Agent Results

| Step | Agent | Category | Status | Time (s) | Tokens | API Calls | Pages | Output File |
|------|-------|----------|--------|----------|--------|-----------|-------|-------------|
| 01 | metadata_agent | extraction | OK | 10.0 | 4,340 | 1 | 0-2 | `01_extraction_metadata.json` |
| 04 | narrative_agent | extraction | OK | 26.1 | 19,859 | 2 | 2-3,6,8,12-13,15-16,20,29 | `04_extraction_narrative.json` |
| 05 | docstructure_agent | extraction | OK | 74.0 | 17,495 | 1 | 0-4,6-7,20,25-26,34,41,45,47-50,52,54 | `05_extraction_document_structure.json` |
| 06 | eligibility_agent | extraction | OK | 64.5 | 13,965 | 1 | 29-35 | `06_extraction_eligibility.json` |
| 07 | objectives_agent | extraction | OK | 114.4 | 26,179 | 2 | 7-9,26-29 | `07_extraction_objectives.json` |
| 08 | studydesign_agent | extraction | OK | 17.9 | 14,177 | 1 | 0-5,7-11,19-21,23-27 | `08_extraction_study_design.json` |
| 09 | procedures_agent | extraction | OK | 47.3 | 19,954 | 1 | 2,4,9,13-16,18,20,22,30,37,41,43-44 | `09_extraction_procedures_devices.json` |
| 10 | interventions_agent | extraction | OK | 26.0 | 35,058 | 1 | 2-7,9-17,19-22,24-27,29-38,40-48 | `10_extraction_interventions.json` |
| 11 | scheduling_agent | extraction | OK | 126.9 | 27,299 | 1 | 2,4,10,12,15,17,20,25,27,29,32,37,39-42,57 | `11_extraction_scheduling_logic.json` |
| 12 | execution_agent | extraction | OK | 100.9 | 27,846 | 9 | 0-41,50-53,68 | `12_extraction_execution_model.json` |
| 13 | advanced_agent | extraction | OK | 8.0 | 17,262 | 1 | 0-29,69-71 | `13_extraction_advanced_entities.json` |
| 14 | biomedical_concept_agent | extraction | FAIL | 0.0 | 0 | 0 |  | `14_extraction_biomedical_concepts.json` |
| 15 | postprocessing_agent | quality | OK | 0.0 | 0 | 0 |  | `15_quality_postprocessing.json` |
| 16 | reconciliation_agent | quality | OK | 0.1 | 0 | 0 |  | `16_quality_reconciliation.json` |
| 17 | validation_agent | quality | OK | 0.0 | 0 | 0 |  | `17_quality_validation.json` |
| 18 | enrichment_agent | quality | OK | 0.8 | 0 | 1 |  | `18_quality_enrichment.json` |
| 19 | usdm-generator | support | OK | 0.1 | 0 | 0 |  | `19_support_usdm_generator.json` |
| 20 | provenance | support | OK | 0.0 | 0 | 0 |  | `20_support_provenance.json` |
| 00 | pdf-parser | support | OK | 0.8 | 0 | 0 | | |

## Failed Agents

- **biomedical_concept_agent**: Failed after 4 attempts: Extraction returned no data

## Output Files

- `01_extraction_metadata.json`
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
- `15_quality_postprocessing.json`
- `16_quality_reconciliation.json`
- `17_quality_validation.json`
- `18_quality_enrichment.json`
- `19_support_usdm_generator.json`
- `20_support_provenance.json`
- `Alexion_NCT04573309_Wilsons.pdf`
- `Alexion_NCT04573309_Wilsons_provenance.json`
- `Alexion_NCT04573309_Wilsons_usdm.json`
- `conformance_report.json`
- `id_mapping.json`
