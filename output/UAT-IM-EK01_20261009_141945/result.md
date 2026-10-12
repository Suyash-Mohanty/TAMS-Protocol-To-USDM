# Pipeline Result: UAT-IM-EK01

**Status:** SUCCESS
**PDF:** `UAT-IM-EK01.pdf`
**Model:** cortex/reforge-claude-opus-5
**Started:** 2026-10-09 14:19:45
**Finished:** 2026-10-09 14:28:42
**Duration:** 536.9s
**Entities:** 986
**Waves:** 4

## Statistics

| Metric | Value |
|--------|-------|
| Total Agents | 21 |
| Succeeded | 21 |
| Failed | 0 |
| Total Entities | 986 |
| Total Tokens | 278,438 |
| Total API Calls | 84 |
| Total Duration | 536.9s |

## Execution Flow

```
Wave 0  (266.2s)
  [OK] docstructure_agent (90.2s)  ->  05_extraction_document_structure.json
  [OK] metadata_agent (11.1s)  ->  01_extraction_metadata.json
  [OK] narrative_agent (266.2s)  ->  04_extraction_narrative.json
  [OK] pdf-parser (2.3s)
  [OK] provenance (0.0s)  ->  20_support_provenance.json
  [OK] soa_vision_agent (54.7s)  ->  02_extraction_soa_vision.json
  [OK] usdm-generator (2.6s)  ->  19_support_usdm_generator.json
  |
Wave 1  (110.7s)
  [OK] advanced_agent (3.3s)  ->  13_extraction_advanced_entities.json
  [OK] eligibility_agent (24.8s)  ->  06_extraction_eligibility.json
  [OK] objectives_agent (37.9s)  ->  07_extraction_objectives.json
  [OK] procedures_agent (77.3s)  ->  09_extraction_procedures_devices.json
  [OK] soa_text_agent (110.7s)  ->  03_extraction_soa_text.json
  [OK] studydesign_agent (11.8s)  ->  08_extraction_study_design.json
  |
Wave 2  (133.2s)
  [OK] biomedical_concept_agent (133.2s)  ->  14_extraction_biomedical_concepts.json
  [OK] execution_agent (95.4s)  ->  12_extraction_execution_model.json
  [OK] interventions_agent (11.9s)  ->  10_extraction_interventions.json
  [OK] scheduling_agent (55.2s)  ->  11_extraction_scheduling_logic.json
  |
Wave 3  (14.4s)
  [OK] enrichment_agent (14.4s)  ->  18_quality_enrichment.json
  [OK] postprocessing_agent (0.2s)  ->  15_quality_postprocessing.json
  [OK] reconciliation_agent (0.3s)  ->  16_quality_reconciliation.json
  [OK] validation_agent (0.0s)  ->  17_quality_validation.json
  |
Output
  [OK] UAT-IM-EK01_usdm.json
  [OK] UAT-IM-EK01_provenance.json
```

## Agent Results

| Step | Agent | Category | Status | Time (s) | Tokens | API Calls | Pages | Output File |
|------|-------|----------|--------|----------|--------|-----------|-------|-------------|
| 01 | metadata_agent | extraction | OK | 11.1 | 4,594 | 1 | 0-2 | `01_extraction_metadata.json` |
| 02 | soa_vision_agent | extraction | OK | 54.7 | 22,856 | 1 | 8-17 | `02_extraction_soa_vision.json` |
| 03 | soa_text_agent | extraction | OK | 110.7 | 32,719 | 1 | 8-17 | `03_extraction_soa_text.json` |
| 04 | narrative_agent | extraction | OK | 266.2 | 27,860 | 2 | 2-9,16,19,21,26,71-73 | `04_extraction_narrative.json` |
| 05 | docstructure_agent | extraction | OK | 90.2 | 20,315 | 1 | 0-5,9,11-12,16-17,19-20,31,42,44,49 | `05_extraction_document_structure.json` |
| 06 | eligibility_agent | extraction | OK | 24.8 | 9,138 | 1 | 8-10,29-31 | `06_extraction_eligibility.json` |
| 07 | objectives_agent | extraction | OK | 37.9 | 28,064 | 2 | 5-16,25-28,44-46 | `07_extraction_objectives.json` |
| 08 | studydesign_agent | extraction | OK | 11.8 | 16,448 | 1 | 0-18,27-29 | `08_extraction_study_design.json` |
| 09 | procedures_agent | extraction | OK | 77.3 | 21,067 | 1 | 3-5,9-10,12,14,16-17,19,21,24,31,34-35 | `09_extraction_procedures_devices.json` |
| 10 | interventions_agent | extraction | OK | 11.9 | 24,328 | 1 | 1-10,13-25,27-29,33-43 | `10_extraction_interventions.json` |
| 11 | scheduling_agent | extraction | OK | 55.2 | 13,285 | 1 | 3,14,31,36,38,41 | `11_extraction_scheduling_logic.json` |
| 12 | execution_agent | extraction | OK | 95.4 | 30,074 | 11 | 0-41,43-45,53-55,68-69,71,73 | `12_extraction_execution_model.json` |
| 13 | advanced_agent | extraction | OK | 3.3 | 4,623 | 1 | 0-3 | `13_extraction_advanced_entities.json` |
| 14 | biomedical_concept_agent | extraction | OK | 133.2 | 23,067 | 2 |  | `14_extraction_biomedical_concepts.json` |
| 15 | postprocessing_agent | quality | OK | 0.2 | 0 | 0 |  | `15_quality_postprocessing.json` |
| 16 | reconciliation_agent | quality | OK | 0.3 | 0 | 0 |  | `16_quality_reconciliation.json` |
| 17 | validation_agent | quality | OK | 0.0 | 0 | 0 |  | `17_quality_validation.json` |
| 18 | enrichment_agent | quality | OK | 14.4 | 0 | 57 |  | `18_quality_enrichment.json` |
| 19 | usdm-generator | support | OK | 2.6 | 0 | 0 |  | `19_support_usdm_generator.json` |
| 20 | provenance | support | OK | 0.0 | 0 | 0 |  | `20_support_provenance.json` |
| 00 | pdf-parser | support | OK | 2.3 | 0 | 0 | | |

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
- `usdm_validation.json`
