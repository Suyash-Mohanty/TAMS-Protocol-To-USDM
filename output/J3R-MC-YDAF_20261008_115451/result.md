# Pipeline Result: J3R-MC-YDAF

**Status:** SUCCESS
**PDF:** `J3R-MC-YDAF.pdf`
**Model:** cortex/reforge-claude-opus-5
**Started:** 2026-10-08 11:54:51
**Finished:** 2026-10-08 12:02:13
**Duration:** 441.3s
**Entities:** 1018
**Waves:** 4

## Statistics

| Metric | Value |
|--------|-------|
| Total Agents | 21 |
| Succeeded | 21 |
| Failed | 0 |
| Total Entities | 1018 |
| Total Tokens | 261,149 |
| Total API Calls | 78 |
| Total Duration | 441.3s |

## Execution Flow

```
Wave 0  (147.4s)
  [OK] docstructure_agent (147.4s)  ->  05_extraction_document_structure.json
  [OK] metadata_agent (67.5s)  ->  01_extraction_metadata.json
  [OK] narrative_agent (88.8s)  ->  04_extraction_narrative.json
  [OK] pdf-parser (5.4s)
  [OK] provenance (0.0s)  ->  20_support_provenance.json
  [OK] soa_vision_agent (89.0s)  ->  02_extraction_soa_vision.json
  [OK] usdm-generator (0.0s)  ->  19_support_usdm_generator.json
  |
Wave 1  (108.8s)
  [OK] advanced_agent (5.1s)  ->  13_extraction_advanced_entities.json
  [OK] eligibility_agent (34.7s)  ->  06_extraction_eligibility.json
  [OK] objectives_agent (108.8s)  ->  07_extraction_objectives.json
  [OK] procedures_agent (49.4s)  ->  09_extraction_procedures_devices.json
  [OK] soa_text_agent (84.0s)  ->  03_extraction_soa_text.json
  [OK] studydesign_agent (15.4s)  ->  08_extraction_study_design.json
  |
Wave 2  (145.4s)
  [OK] biomedical_concept_agent (59.2s)  ->  14_extraction_biomedical_concepts.json
  [OK] execution_agent (145.4s)  ->  12_extraction_execution_model.json
  [OK] interventions_agent (27.6s)  ->  10_extraction_interventions.json
  [OK] scheduling_agent (71.6s)  ->  11_extraction_scheduling_logic.json
  |
Wave 3  (8.5s)
  [OK] enrichment_agent (8.5s)  ->  18_quality_enrichment.json
  [OK] postprocessing_agent (0.2s)  ->  15_quality_postprocessing.json
  [OK] reconciliation_agent (0.2s)  ->  16_quality_reconciliation.json
  [OK] validation_agent (0.0s)  ->  17_quality_validation.json
  |
Output
  [OK] J3R-MC-YDAF_usdm.json
  [OK] J3R-MC-YDAF_provenance.json
```

## Agent Results

| Step | Agent | Category | Status | Time (s) | Tokens | API Calls | Pages | Output File |
|------|-------|----------|--------|----------|--------|-----------|-------|-------------|
| 01 | metadata_agent | extraction | OK | 67.5 | 3,998 | 1 | 0-2 | `01_extraction_metadata.json` |
| 02 | soa_vision_agent | extraction | OK | 89.0 | 20,060 | 1 | 13-15,45-49,79-80 | `02_extraction_soa_vision.json` |
| 03 | soa_text_agent | extraction | OK | 84.0 | 26,161 | 1 | 13-15,45-49,79-80 | `03_extraction_soa_text.json` |
| 04 | narrative_agent | extraction | OK | 88.8 | 16,247 | 2 | 4,7-9,12,14,16,23-24 | `04_extraction_narrative.json` |
| 05 | docstructure_agent | extraction | OK | 147.4 | 22,579 | 1 | 0-4,6-7,17,19-21,23,25-26,28,30,34,40,46-47 | `05_extraction_document_structure.json` |
| 06 | eligibility_agent | extraction | OK | 34.7 | 10,540 | 1 | 15-17,45-48 | `06_extraction_eligibility.json` |
| 07 | objectives_agent | extraction | OK | 108.8 | 29,454 | 2 | 3-11 | `07_extraction_objectives.json` |
| 08 | studydesign_agent | extraction | OK | 15.4 | 20,166 | 1 | 0-1,3-29 | `08_extraction_study_design.json` |
| 09 | procedures_agent | extraction | OK | 49.4 | 15,449 | 1 | 5,7,14-20,23,25-27,34,47 | `09_extraction_procedures_devices.json` |
| 10 | interventions_agent | extraction | OK | 27.6 | 31,244 | 1 | 0-24,26-28,31-48 | `10_extraction_interventions.json` |
| 11 | scheduling_agent | extraction | OK | 71.6 | 16,508 | 1 | 2,5,15,43-44,48,50-51 | `11_extraction_scheduling_logic.json` |
| 12 | execution_agent | extraction | OK | 145.4 | 35,176 | 11 | 0-44,46,48-49,51-53,56-57,59-62,65,67,71-72,74,79-80,84,88,97,100,103,123,143,157-158,162 | `12_extraction_execution_model.json` |
| 13 | advanced_agent | extraction | OK | 5.1 | 3,408 | 1 | 0-4,15 | `13_extraction_advanced_entities.json` |
| 14 | biomedical_concept_agent | extraction | OK | 59.2 | 10,159 | 1 |  | `14_extraction_biomedical_concepts.json` |
| 15 | postprocessing_agent | quality | OK | 0.2 | 0 | 0 |  | `15_quality_postprocessing.json` |
| 16 | reconciliation_agent | quality | OK | 0.2 | 0 | 0 |  | `16_quality_reconciliation.json` |
| 17 | validation_agent | quality | OK | 0.0 | 0 | 0 |  | `17_quality_validation.json` |
| 18 | enrichment_agent | quality | OK | 8.5 | 0 | 52 |  | `18_quality_enrichment.json` |
| 19 | usdm-generator | support | OK | 0.0 | 0 | 0 |  | `19_support_usdm_generator.json` |
| 20 | provenance | support | OK | 0.0 | 0 | 0 |  | `20_support_provenance.json` |
| 00 | pdf-parser | support | OK | 5.4 | 0 | 0 | | |

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
