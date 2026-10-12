# Pipeline Result: UAT-IM-MR01

**Status:** SUCCESS
**PDF:** `UAT-IM-MR01.pdf`
**Model:** cortex/reforge-claude-opus-5
**Started:** 2026-10-12 16:05:07
**Finished:** 2026-10-12 16:11:38
**Duration:** 390.7s
**Entities:** 1293
**Waves:** 4

## Statistics

| Metric | Value |
|--------|-------|
| Total Agents | 21 |
| Succeeded | 21 |
| Failed | 0 |
| Total Entities | 1293 |
| Total Tokens | 385,682 |
| Total API Calls | 71 |
| Total Duration | 390.7s |

## Execution Flow

```
Wave 0  (135.5s)
  [OK] docstructure_agent (67.1s)  ->  05_extraction_document_structure.json
  [OK] metadata_agent (14.3s)  ->  01_extraction_metadata.json
  [OK] narrative_agent (59.3s)  ->  04_extraction_narrative.json
  [OK] pdf-parser (7.3s)
  [OK] provenance (0.0s)  ->  20_support_provenance.json
  [OK] soa_vision_agent (135.5s)  ->  02_extraction_soa_vision.json
  [OK] usdm-generator (0.5s)  ->  19_support_usdm_generator.json
  |
Wave 1  (135.2s)
  [OK] advanced_agent (32.3s)  ->  13_extraction_advanced_entities.json
  [OK] eligibility_agent (121.9s)  ->  06_extraction_eligibility.json
  [OK] objectives_agent (135.2s)  ->  07_extraction_objectives.json
  [OK] procedures_agent (47.3s)  ->  09_extraction_procedures_devices.json
  [OK] soa_text_agent (68.4s)  ->  03_extraction_soa_text.json
  [OK] studydesign_agent (12.7s)  ->  08_extraction_study_design.json
  |
Wave 2  (96.5s)
  [OK] biomedical_concept_agent (70.7s)  ->  14_extraction_biomedical_concepts.json
  [OK] execution_agent (96.5s)  ->  12_extraction_execution_model.json
  [OK] interventions_agent (15.8s)  ->  10_extraction_interventions.json
  [OK] scheduling_agent (65.8s)  ->  11_extraction_scheduling_logic.json
  |
Wave 3  (3.4s)
  [OK] enrichment_agent (3.4s)  ->  18_quality_enrichment.json
  [OK] postprocessing_agent (0.0s)  ->  15_quality_postprocessing.json
  [OK] reconciliation_agent (0.5s)  ->  16_quality_reconciliation.json
  [OK] validation_agent (0.0s)  ->  17_quality_validation.json
  |
Output
  [OK] UAT-IM-MR01_usdm.json
  [OK] UAT-IM-MR01_provenance.json
```

## Agent Results

| Step | Agent | Category | Status | Time (s) | Tokens | API Calls | Pages | Output File |
|------|-------|----------|--------|----------|--------|-----------|-------|-------------|
| 01 | metadata_agent | extraction | OK | 14.3 | 4,242 | 1 | 0-2 | `01_extraction_metadata.json` |
| 02 | soa_vision_agent | extraction | OK | 135.5 | 60,646 | 2 | 9,18-35,170 | `02_extraction_soa_vision.json` |
| 03 | soa_text_agent | extraction | OK | 68.4 | 36,923 | 1 | 9,18-35,170 | `03_extraction_soa_text.json` |
| 04 | narrative_agent | extraction | OK | 59.3 | 28,694 | 2 | 2,4-9,11,13,15,17,27,171-177 | `04_extraction_narrative.json` |
| 05 | docstructure_agent | extraction | OK | 67.1 | 21,051 | 1 | 0-5,8,16-19,21,23,27-29,31,46 | `05_extraction_document_structure.json` |
| 06 | eligibility_agent | extraction | OK | 121.9 | 27,346 | 1 | 50-60 | `06_extraction_eligibility.json` |
| 07 | objectives_agent | extraction | OK | 135.2 | 53,925 | 2 | 1-3,8-10,15-17,41-47 | `07_extraction_objectives.json` |
| 08 | studydesign_agent | extraction | OK | 12.7 | 18,274 | 1 | 4-7,11-13,16-29 | `08_extraction_study_design.json` |
| 09 | procedures_agent | extraction | OK | 47.3 | 19,487 | 1 | 3,6,8-10,13,17-21,25,27,34-35 | `09_extraction_procedures_devices.json` |
| 10 | interventions_agent | extraction | OK | 15.8 | 35,110 | 1 | 0-14,16-18,21-27,29-31,33-49 | `10_extraction_interventions.json` |
| 11 | scheduling_agent | extraction | OK | 65.8 | 15,264 | 1 | 6,11-12,44,57,59 | `11_extraction_scheduling_logic.json` |
| 12 | execution_agent | extraction | OK | 96.5 | 35,381 | 11 | 0-39,43-46,49,51,53,56,67,69-70,74-75,80,87,89,94,96-97,100,107,111,117-118,122,125,137-138,145-148,169-170,178-179,181 | `12_extraction_execution_model.json` |
| 13 | advanced_agent | extraction | OK | 32.3 | 12,285 | 1 | 0-3,5,8,178,181,183-184 | `13_extraction_advanced_entities.json` |
| 14 | biomedical_concept_agent | extraction | OK | 70.7 | 17,054 | 1 |  | `14_extraction_biomedical_concepts.json` |
| 15 | postprocessing_agent | quality | OK | 0.0 | 0 | 0 |  | `15_quality_postprocessing.json` |
| 16 | reconciliation_agent | quality | OK | 0.5 | 0 | 0 |  | `16_quality_reconciliation.json` |
| 17 | validation_agent | quality | OK | 0.0 | 0 | 0 |  | `17_quality_validation.json` |
| 18 | enrichment_agent | quality | OK | 3.4 | 0 | 44 |  | `18_quality_enrichment.json` |
| 19 | usdm-generator | support | OK | 0.5 | 0 | 0 |  | `19_support_usdm_generator.json` |
| 20 | provenance | support | OK | 0.0 | 0 | 0 |  | `20_support_provenance.json` |
| 00 | pdf-parser | support | OK | 7.3 | 0 | 0 | | |

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
- `soa_page_019.png`
- `soa_page_020.png`
- `soa_page_021.png`
- `soa_page_022.png`
- `soa_page_023.png`
- `soa_page_024.png`
- `soa_page_025.png`
- `soa_page_026.png`
- `soa_page_027.png`
- `soa_page_028.png`
- `soa_page_029.png`
- `soa_page_030.png`
- `soa_page_031.png`
- `soa_page_032.png`
- `soa_page_033.png`
- `soa_page_034.png`
- `soa_page_035.png`
- `soa_page_036.png`
- `soa_page_171.png`
- `usdm_validation.json`
