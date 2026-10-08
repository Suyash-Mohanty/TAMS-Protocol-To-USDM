# Pipeline Result: UAT-IM-MR01

**Status:** SUCCESS
**PDF:** `UAT-IM-MR01.pdf`
**Model:** cortex/reforge-claude-opus-5
**Started:** 2026-10-08 16:47:54
**Finished:** 2026-10-08 16:55:39
**Duration:** 465.0s
**Entities:** 1106
**Waves:** 4

## Statistics

| Metric | Value |
|--------|-------|
| Total Agents | 21 |
| Succeeded | 21 |
| Failed | 0 |
| Total Entities | 1106 |
| Total Tokens | 306,805 |
| Total API Calls | 71 |
| Total Duration | 465.0s |

## Execution Flow

```
Wave 0  (121.4s)
  [OK] docstructure_agent (121.4s)  ->  05_extraction_document_structure.json
  [OK] metadata_agent (9.0s)  ->  01_extraction_metadata.json
  [OK] narrative_agent (89.9s)  ->  04_extraction_narrative.json
  [OK] pdf-parser (7.1s)
  [OK] provenance (0.0s)  ->  20_support_provenance.json
  [OK] soa_vision_agent (23.9s)  ->  02_extraction_soa_vision.json
  [OK] usdm-generator (5.4s)  ->  19_support_usdm_generator.json
  |
Wave 1  (180.0s)
  [OK] advanced_agent (44.0s)  ->  13_extraction_advanced_entities.json
  [OK] eligibility_agent (15.5s)  ->  06_extraction_eligibility.json
  [OK] objectives_agent (180.0s)  ->  07_extraction_objectives.json
  [OK] procedures_agent (61.2s)  ->  09_extraction_procedures_devices.json
  [OK] soa_text_agent (61.0s)  ->  03_extraction_soa_text.json
  [OK] studydesign_agent (20.4s)  ->  08_extraction_study_design.json
  |
Wave 2  (137.3s)
  [OK] biomedical_concept_agent (88.0s)  ->  14_extraction_biomedical_concepts.json
  [OK] execution_agent (137.3s)  ->  12_extraction_execution_model.json
  [OK] interventions_agent (21.3s)  ->  10_extraction_interventions.json
  [OK] scheduling_agent (70.4s)  ->  11_extraction_scheduling_logic.json
  |
Wave 3  (3.0s)
  [OK] enrichment_agent (3.0s)  ->  18_quality_enrichment.json
  [OK] postprocessing_agent (0.0s)  ->  15_quality_postprocessing.json
  [OK] reconciliation_agent (0.4s)  ->  16_quality_reconciliation.json
  [OK] validation_agent (0.2s)  ->  17_quality_validation.json
  |
Output
  [OK] UAT-IM-MR01_usdm.json
  [OK] UAT-IM-MR01_provenance.json
```

## Agent Results

| Step | Agent | Category | Status | Time (s) | Tokens | API Calls | Pages | Output File |
|------|-------|----------|--------|----------|--------|-----------|-------|-------------|
| 01 | metadata_agent | extraction | OK | 9.0 | 4,242 | 1 | 0-2 | `01_extraction_metadata.json` |
| 02 | soa_vision_agent | extraction | OK | 23.9 | 18,172 | 1 | 9-11,42-44,53-56 | `02_extraction_soa_vision.json` |
| 03 | soa_text_agent | extraction | OK | 61.0 | 20,366 | 1 | 9-11,42-44,53-56 | `03_extraction_soa_text.json` |
| 04 | narrative_agent | extraction | OK | 89.9 | 28,691 | 2 | 2,4-9,11,13,15,17,27,171-177 | `04_extraction_narrative.json` |
| 05 | docstructure_agent | extraction | OK | 121.4 | 25,220 | 1 | 0-5,8,16-19,21,23,27-29,31,46 | `05_extraction_document_structure.json` |
| 06 | eligibility_agent | extraction | OK | 15.5 | 5,058 | 1 | 2-4 | `06_extraction_eligibility.json` |
| 07 | objectives_agent | extraction | OK | 180.0 | 52,792 | 2 | 1-3,8-10,15-17,41-47 | `07_extraction_objectives.json` |
| 08 | studydesign_agent | extraction | OK | 20.4 | 18,323 | 1 | 4-7,11-13,16-29 | `08_extraction_study_design.json` |
| 09 | procedures_agent | extraction | OK | 61.2 | 19,109 | 1 | 3,6,8-10,13,17-21,25,27,34-35 | `09_extraction_procedures_devices.json` |
| 10 | interventions_agent | extraction | OK | 21.3 | 34,539 | 1 | 0-14,16-18,21-27,29-31,33-49 | `10_extraction_interventions.json` |
| 11 | scheduling_agent | extraction | OK | 70.4 | 15,734 | 1 | 6,11-12,44,57,59 | `11_extraction_scheduling_logic.json` |
| 12 | execution_agent | extraction | OK | 137.3 | 36,781 | 11 | 0-39,43-46,49,51,53,56,67,69-70,74-75,80,87,89,94,96-97,100,107,111,117-118,122,125,137-138,145-148,169-170,178-179,181 | `12_extraction_execution_model.json` |
| 13 | advanced_agent | extraction | OK | 44.0 | 12,718 | 1 | 0-3,5,8,178,181,183-184 | `13_extraction_advanced_entities.json` |
| 14 | biomedical_concept_agent | extraction | OK | 88.0 | 15,060 | 1 |  | `14_extraction_biomedical_concepts.json` |
| 15 | postprocessing_agent | quality | OK | 0.0 | 0 | 0 |  | `15_quality_postprocessing.json` |
| 16 | reconciliation_agent | quality | OK | 0.4 | 0 | 0 |  | `16_quality_reconciliation.json` |
| 17 | validation_agent | quality | OK | 0.2 | 0 | 0 |  | `17_quality_validation.json` |
| 18 | enrichment_agent | quality | OK | 3.0 | 0 | 45 |  | `18_quality_enrichment.json` |
| 19 | usdm-generator | support | OK | 5.4 | 0 | 0 |  | `19_support_usdm_generator.json` |
| 20 | provenance | support | OK | 0.0 | 0 | 0 |  | `20_support_provenance.json` |
| 00 | pdf-parser | support | OK | 7.1 | 0 | 0 | | |

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
- `UAT-IM-MR01.pdf`
- `UAT-IM-MR01_provenance.json`
- `UAT-IM-MR01_usdm.json`
- `conformance_report.json`
- `id_mapping.json`
- `soa_page_010.png`
- `soa_page_011.png`
- `soa_page_012.png`
- `soa_page_043.png`
- `soa_page_044.png`
- `soa_page_045.png`
- `soa_page_054.png`
- `soa_page_055.png`
- `soa_page_056.png`
- `soa_page_057.png`
- `usdm_validation.json`
