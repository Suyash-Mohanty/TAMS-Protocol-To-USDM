# Pipeline Result: UAT-IM-MR01

**Status:** SUCCESS
**PDF:** `UAT-IM-MR01.pdf`
**Model:** cortex/reforge-claude-opus-5
**Started:** 2026-10-08 12:17:02
**Finished:** 2026-10-08 12:24:40
**Duration:** 457.8s
**Entities:** 1003
**Waves:** 4

## Statistics

| Metric | Value |
|--------|-------|
| Total Agents | 21 |
| Succeeded | 21 |
| Failed | 0 |
| Total Entities | 1003 |
| Total Tokens | 287,300 |
| Total API Calls | 73 |
| Total Duration | 457.8s |

## Execution Flow

```
Wave 0  (115.6s)
  [OK] docstructure_agent (115.6s)  ->  05_extraction_document_structure.json
  [OK] metadata_agent (9.1s)  ->  01_extraction_metadata.json
  [OK] narrative_agent (49.0s)  ->  04_extraction_narrative.json
  [OK] pdf-parser (6.4s)
  [OK] provenance (0.0s)  ->  20_support_provenance.json
  [OK] soa_vision_agent (42.5s)  ->  02_extraction_soa_vision.json
  [OK] usdm-generator (0.0s)  ->  19_support_usdm_generator.json
  |
Wave 1  (164.8s)
  [OK] advanced_agent (16.1s)  ->  13_extraction_advanced_entities.json
  [OK] eligibility_agent (17.3s)  ->  06_extraction_eligibility.json
  [OK] objectives_agent (164.8s)  ->  07_extraction_objectives.json
  [OK] procedures_agent (65.5s)  ->  09_extraction_procedures_devices.json
  [OK] soa_text_agent (73.7s)  ->  03_extraction_soa_text.json
  [OK] studydesign_agent (14.5s)  ->  08_extraction_study_design.json
  |
Wave 2  (142.5s)
  [OK] biomedical_concept_agent (86.2s)  ->  14_extraction_biomedical_concepts.json
  [OK] execution_agent (142.5s)  ->  12_extraction_execution_model.json
  [OK] interventions_agent (20.5s)  ->  10_extraction_interventions.json
  [OK] scheduling_agent (70.7s)  ->  11_extraction_scheduling_logic.json
  |
Wave 3  (7.2s)
  [OK] enrichment_agent (7.2s)  ->  18_quality_enrichment.json
  [OK] postprocessing_agent (0.0s)  ->  15_quality_postprocessing.json
  [OK] reconciliation_agent (0.3s)  ->  16_quality_reconciliation.json
  [OK] validation_agent (0.0s)  ->  17_quality_validation.json
  |
Output
  [OK] UAT-IM-MR01_usdm.json
  [OK] UAT-IM-MR01_provenance.json
```

## Agent Results

| Step | Agent | Category | Status | Time (s) | Tokens | API Calls | Pages | Output File |
|------|-------|----------|--------|----------|--------|-----------|-------|-------------|
| 01 | metadata_agent | extraction | OK | 9.1 | 4,245 | 1 | 0-2 | `01_extraction_metadata.json` |
| 02 | soa_vision_agent | extraction | OK | 42.5 | 18,823 | 1 | 9-11,42-44,53-56 | `02_extraction_soa_vision.json` |
| 03 | soa_text_agent | extraction | OK | 73.7 | 24,196 | 1 | 9-11,42-44,53-56 | `03_extraction_soa_text.json` |
| 04 | narrative_agent | extraction | OK | 49.0 | 19,201 | 2 | 2,4-5,8-9,11,13,15,17,27 | `04_extraction_narrative.json` |
| 05 | docstructure_agent | extraction | OK | 115.6 | 23,677 | 1 | 0-5,8,16-19,21,23,27-29,31,46 | `05_extraction_document_structure.json` |
| 06 | eligibility_agent | extraction | OK | 17.3 | 5,268 | 1 | 2-4 | `06_extraction_eligibility.json` |
| 07 | objectives_agent | extraction | OK | 164.8 | 47,302 | 2 | 1-10,15-17 | `07_extraction_objectives.json` |
| 08 | studydesign_agent | extraction | OK | 14.5 | 18,113 | 1 | 4-7,11-13,16-29 | `08_extraction_study_design.json` |
| 09 | procedures_agent | extraction | OK | 65.5 | 19,554 | 1 | 3,6,8-10,13,17-21,25,27,34-35 | `09_extraction_procedures_devices.json` |
| 10 | interventions_agent | extraction | OK | 20.5 | 34,046 | 1 | 0-14,16-18,21-27,29-31,33-49 | `10_extraction_interventions.json` |
| 11 | scheduling_agent | extraction | OK | 70.7 | 15,829 | 1 | 6,11-12,44,57,59 | `11_extraction_scheduling_logic.json` |
| 12 | execution_agent | extraction | OK | 142.5 | 35,247 | 11 | 0-39,43-46,49,51,53,56,67,69-70,74-75,80,87,89,94,96-97,100,107,111,117-118,122,125,137-138,145-148,169-170,178-179,181 | `12_extraction_execution_model.json` |
| 13 | advanced_agent | extraction | OK | 16.1 | 8,020 | 1 | 0-3,5,8,178,181,183-184 | `13_extraction_advanced_entities.json` |
| 14 | biomedical_concept_agent | extraction | OK | 86.2 | 13,779 | 1 |  | `14_extraction_biomedical_concepts.json` |
| 15 | postprocessing_agent | quality | OK | 0.0 | 0 | 0 |  | `15_quality_postprocessing.json` |
| 16 | reconciliation_agent | quality | OK | 0.3 | 0 | 0 |  | `16_quality_reconciliation.json` |
| 17 | validation_agent | quality | OK | 0.0 | 0 | 0 |  | `17_quality_validation.json` |
| 18 | enrichment_agent | quality | OK | 7.2 | 0 | 47 |  | `18_quality_enrichment.json` |
| 19 | usdm-generator | support | OK | 0.0 | 0 | 0 |  | `19_support_usdm_generator.json` |
| 20 | provenance | support | OK | 0.0 | 0 | 0 |  | `20_support_provenance.json` |
| 00 | pdf-parser | support | OK | 6.4 | 0 | 0 | | |

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
