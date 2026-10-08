# Pipeline Result: UAT-IM-MR01

**Status:** SUCCESS
**PDF:** `UAT-IM-MR01.pdf`
**Model:** cortex/reforge-claude-opus-5
**Started:** 2026-10-08 16:23:27
**Finished:** 2026-10-08 16:30:45
**Duration:** 437.3s
**Entities:** 1058
**Waves:** 4

## Statistics

| Metric | Value |
|--------|-------|
| Total Agents | 21 |
| Succeeded | 21 |
| Failed | 0 |
| Total Entities | 1058 |
| Total Tokens | 305,395 |
| Total API Calls | 70 |
| Total Duration | 437.3s |

## Execution Flow

```
Wave 0  (107.1s)
  [OK] docstructure_agent (107.1s)  ->  05_extraction_document_structure.json
  [OK] metadata_agent (17.4s)  ->  01_extraction_metadata.json
  [OK] narrative_agent (90.8s)  ->  04_extraction_narrative.json
  [OK] pdf-parser (5.1s)
  [OK] provenance (0.0s)  ->  20_support_provenance.json
  [OK] soa_vision_agent (29.0s)  ->  02_extraction_soa_vision.json
  [OK] usdm-generator (0.6s)  ->  19_support_usdm_generator.json
  |
Wave 1  (179.5s)
  [OK] advanced_agent (42.6s)  ->  13_extraction_advanced_entities.json
  [OK] eligibility_agent (13.6s)  ->  06_extraction_eligibility.json
  [OK] objectives_agent (179.5s)  ->  07_extraction_objectives.json
  [OK] procedures_agent (59.7s)  ->  09_extraction_procedures_devices.json
  [OK] soa_text_agent (58.8s)  ->  03_extraction_soa_text.json
  [OK] studydesign_agent (18.3s)  ->  08_extraction_study_design.json
  |
Wave 2  (133.1s)
  [OK] biomedical_concept_agent (97.4s)  ->  14_extraction_biomedical_concepts.json
  [OK] execution_agent (133.1s)  ->  12_extraction_execution_model.json
  [OK] interventions_agent (24.9s)  ->  10_extraction_interventions.json
  [OK] scheduling_agent (70.6s)  ->  11_extraction_scheduling_logic.json
  |
Wave 3  (3.3s)
  [OK] enrichment_agent (3.3s)  ->  18_quality_enrichment.json
  [OK] postprocessing_agent (0.1s)  ->  15_quality_postprocessing.json
  [OK] reconciliation_agent (0.9s)  ->  16_quality_reconciliation.json
  [OK] validation_agent (0.0s)  ->  17_quality_validation.json
  |
Output
  [OK] UAT-IM-MR01_usdm.json
  [OK] UAT-IM-MR01_provenance.json
```

## Agent Results

| Step | Agent | Category | Status | Time (s) | Tokens | API Calls | Pages | Output File |
|------|-------|----------|--------|----------|--------|-----------|-------|-------------|
| 01 | metadata_agent | extraction | OK | 17.4 | 4,242 | 1 | 0-2 | `01_extraction_metadata.json` |
| 02 | soa_vision_agent | extraction | OK | 29.0 | 19,430 | 1 | 9-11,42-44,53-56 | `02_extraction_soa_vision.json` |
| 03 | soa_text_agent | extraction | OK | 58.8 | 21,096 | 1 | 9-11,42-44,53-56 | `03_extraction_soa_text.json` |
| 04 | narrative_agent | extraction | OK | 90.8 | 28,691 | 2 | 2,4-9,11,13,15,17,27,171-177 | `04_extraction_narrative.json` |
| 05 | docstructure_agent | extraction | OK | 107.1 | 22,922 | 1 | 0-5,8,16-19,21,23,27-29,31,46 | `05_extraction_document_structure.json` |
| 06 | eligibility_agent | extraction | OK | 13.6 | 4,780 | 1 | 2-4 | `06_extraction_eligibility.json` |
| 07 | objectives_agent | extraction | OK | 179.5 | 51,597 | 2 | 1-3,8-10,15-17,41-47 | `07_extraction_objectives.json` |
| 08 | studydesign_agent | extraction | OK | 18.3 | 18,360 | 1 | 4-7,11-13,16-29 | `08_extraction_study_design.json` |
| 09 | procedures_agent | extraction | OK | 59.7 | 18,639 | 1 | 3,6,8-10,13,17-21,25,27,34-35 | `09_extraction_procedures_devices.json` |
| 10 | interventions_agent | extraction | OK | 24.9 | 35,189 | 1 | 0-14,16-18,21-27,29-31,33-49 | `10_extraction_interventions.json` |
| 11 | scheduling_agent | extraction | OK | 70.6 | 15,698 | 1 | 6,11-12,44,57,59 | `11_extraction_scheduling_logic.json` |
| 12 | execution_agent | extraction | OK | 133.1 | 35,417 | 11 | 0-39,43-46,49,51,53,56,67,69-70,74-75,80,87,89,94,96-97,100,107,111,117-118,122,125,137-138,145-148,169-170,178-179,181 | `12_extraction_execution_model.json` |
| 13 | advanced_agent | extraction | OK | 42.6 | 12,250 | 1 | 0-3,5,8,178,181,183-184 | `13_extraction_advanced_entities.json` |
| 14 | biomedical_concept_agent | extraction | OK | 97.4 | 17,084 | 1 |  | `14_extraction_biomedical_concepts.json` |
| 15 | postprocessing_agent | quality | OK | 0.1 | 0 | 0 |  | `15_quality_postprocessing.json` |
| 16 | reconciliation_agent | quality | OK | 0.9 | 0 | 0 |  | `16_quality_reconciliation.json` |
| 17 | validation_agent | quality | OK | 0.0 | 0 | 0 |  | `17_quality_validation.json` |
| 18 | enrichment_agent | quality | OK | 3.3 | 0 | 44 |  | `18_quality_enrichment.json` |
| 19 | usdm-generator | support | OK | 0.6 | 0 | 0 |  | `19_support_usdm_generator.json` |
| 20 | provenance | support | OK | 0.0 | 0 | 0 |  | `20_support_provenance.json` |
| 00 | pdf-parser | support | OK | 5.1 | 0 | 0 | | |

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
