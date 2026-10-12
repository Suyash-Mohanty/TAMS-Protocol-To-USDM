# Pipeline Result: J3R-MC-YDAF

**Status:** SUCCESS
**PDF:** `J3R-MC-YDAF.pdf`
**Model:** cortex/reforge-claude-opus-5
**Started:** 2026-10-07 14:02:14
**Finished:** 2026-10-07 14:08:27
**Duration:** 372.7s
**Entities:** 996
**Waves:** 4

## Statistics

| Metric | Value |
|--------|-------|
| Total Agents | 21 |
| Succeeded | 21 |
| Failed | 0 |
| Total Entities | 996 |
| Total Tokens | 258,017 |
| Total API Calls | 87 |
| Total Duration | 372.7s |

## Execution Flow

```
Wave 0  (131.9s)
  [OK] docstructure_agent (131.9s)  ->  05_extraction_document_structure.json
  [OK] metadata_agent (49.5s)  ->  01_extraction_metadata.json
  [OK] narrative_agent (75.4s)  ->  04_extraction_narrative.json
  [OK] pdf-parser (5.4s)
  [OK] provenance (0.0s)  ->  20_support_provenance.json
  [OK] soa_vision_agent (69.8s)  ->  02_extraction_soa_vision.json
  [OK] usdm-generator (0.9s)  ->  19_support_usdm_generator.json
  |
Wave 1  (92.6s)
  [OK] advanced_agent (3.6s)  ->  13_extraction_advanced_entities.json
  [OK] eligibility_agent (33.5s)  ->  06_extraction_eligibility.json
  [OK] objectives_agent (92.6s)  ->  07_extraction_objectives.json
  [OK] procedures_agent (58.8s)  ->  09_extraction_procedures_devices.json
  [OK] soa_text_agent (73.0s)  ->  03_extraction_soa_text.json
  [OK] studydesign_agent (13.8s)  ->  08_extraction_study_design.json
  |
Wave 2  (136.2s)
  [OK] biomedical_concept_agent (51.1s)  ->  14_extraction_biomedical_concepts.json
  [OK] execution_agent (136.2s)  ->  12_extraction_execution_model.json
  [OK] interventions_agent (23.1s)  ->  10_extraction_interventions.json
  [OK] scheduling_agent (69.4s)  ->  11_extraction_scheduling_logic.json
  |
Wave 3  (4.0s)
  [OK] enrichment_agent (4.0s)  ->  18_quality_enrichment.json
  [OK] postprocessing_agent (0.0s)  ->  15_quality_postprocessing.json
  [OK] reconciliation_agent (0.2s)  ->  16_quality_reconciliation.json
  [OK] validation_agent (0.2s)  ->  17_quality_validation.json
  |
Output
  [OK] J3R-MC-YDAF_usdm.json
  [OK] J3R-MC-YDAF_provenance.json
```

## Agent Results

| Step | Agent | Category | Status | Time (s) | Tokens | API Calls | Pages | Output File |
|------|-------|----------|--------|----------|--------|-----------|-------|-------------|
| 01 | metadata_agent | extraction | OK | 49.5 | 3,995 | 1 | 0-2 | `01_extraction_metadata.json` |
| 02 | soa_vision_agent | extraction | OK | 69.8 | 19,998 | 1 | 13-15,45-49,79-80 | `02_extraction_soa_vision.json` |
| 03 | soa_text_agent | extraction | OK | 73.0 | 24,726 | 1 | 13-15,45-49,79-80 | `03_extraction_soa_text.json` |
| 04 | narrative_agent | extraction | OK | 75.4 | 16,242 | 2 | 4,7-9,12,14,16,23-24 | `04_extraction_narrative.json` |
| 05 | docstructure_agent | extraction | OK | 131.9 | 22,953 | 1 | 0-4,6-7,17,19-21,23,25-26,28,30,34,40,46-47 | `05_extraction_document_structure.json` |
| 06 | eligibility_agent | extraction | OK | 33.5 | 10,323 | 1 | 15-17,45-48 | `06_extraction_eligibility.json` |
| 07 | objectives_agent | extraction | OK | 92.6 | 28,632 | 2 | 3-11 | `07_extraction_objectives.json` |
| 08 | studydesign_agent | extraction | OK | 13.8 | 20,044 | 1 | 0-1,3-29 | `08_extraction_study_design.json` |
| 09 | procedures_agent | extraction | OK | 58.8 | 16,885 | 1 | 5,7,14-20,23,25-27,34,47 | `09_extraction_procedures_devices.json` |
| 10 | interventions_agent | extraction | OK | 23.1 | 30,719 | 1 | 0-24,26-28,31-48 | `10_extraction_interventions.json` |
| 11 | scheduling_agent | extraction | OK | 69.4 | 16,106 | 1 | 2,5,15,43-44,48,50-51 | `11_extraction_scheduling_logic.json` |
| 12 | execution_agent | extraction | OK | 136.2 | 35,225 | 11 | 0-44,46,48-49,51-53,56-57,59-62,65,67,71-72,74,79-80,84,88,97,100,103,123,143,157-158,162 | `12_extraction_execution_model.json` |
| 13 | advanced_agent | extraction | OK | 3.6 | 3,408 | 1 | 0-4,15 | `13_extraction_advanced_entities.json` |
| 14 | biomedical_concept_agent | extraction | OK | 51.1 | 8,761 | 1 |  | `14_extraction_biomedical_concepts.json` |
| 15 | postprocessing_agent | quality | OK | 0.0 | 0 | 0 |  | `15_quality_postprocessing.json` |
| 16 | reconciliation_agent | quality | OK | 0.2 | 0 | 0 |  | `16_quality_reconciliation.json` |
| 17 | validation_agent | quality | OK | 0.2 | 0 | 0 |  | `17_quality_validation.json` |
| 18 | enrichment_agent | quality | OK | 4.0 | 0 | 61 |  | `18_quality_enrichment.json` |
| 19 | usdm-generator | support | OK | 0.9 | 0 | 0 |  | `19_support_usdm_generator.json` |
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
- `usdm_validation.json`
