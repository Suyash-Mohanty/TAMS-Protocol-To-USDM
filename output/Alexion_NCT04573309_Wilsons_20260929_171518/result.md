# Pipeline Result: Alexion_NCT04573309_Wilsons

**Status:** SUCCESS
**PDF:** `Alexion_NCT04573309_Wilsons.pdf`
**Model:** cortex/reforge-claude-opus-5
**Started:** 2026-09-29 17:15:18
**Finished:** 2026-09-29 17:21:17
**Duration:** 358.9s
**Entities:** 991
**Waves:** 4

## Statistics

| Metric | Value |
|--------|-------|
| Total Agents | 21 |
| Succeeded | 21 |
| Failed | 0 |
| Total Entities | 991 |
| Total Tokens | 301,835 |
| Total API Calls | 68 |
| Total Duration | 358.9s |

## Execution Flow

```
Wave 0  (89.1s)
  [OK] docstructure_agent (89.1s)  ->  05_extraction_document_structure.json
  [OK] metadata_agent (13.7s)  ->  01_extraction_metadata.json
  [OK] narrative_agent (30.2s)  ->  04_extraction_narrative.json
  [OK] pdf-parser (1.9s)
  [OK] provenance (0.0s)  ->  20_support_provenance.json
  [OK] soa_vision_agent (71.3s)  ->  02_extraction_soa_vision.json
  [OK] usdm-generator (0.9s)  ->  19_support_usdm_generator.json
  |
Wave 1  (99.0s)
  [OK] advanced_agent (9.0s)  ->  13_extraction_advanced_entities.json
  [OK] eligibility_agent (64.4s)  ->  06_extraction_eligibility.json
  [OK] objectives_agent (99.0s)  ->  07_extraction_objectives.json
  [OK] procedures_agent (47.1s)  ->  09_extraction_procedures_devices.json
  [OK] soa_text_agent (97.7s)  ->  03_extraction_soa_text.json
  [OK] studydesign_agent (13.3s)  ->  08_extraction_study_design.json
  |
Wave 2  (128.8s)
  [OK] biomedical_concept_agent (74.4s)  ->  14_extraction_biomedical_concepts.json
  [OK] execution_agent (102.8s)  ->  12_extraction_execution_model.json
  [OK] interventions_agent (22.9s)  ->  10_extraction_interventions.json
  [OK] scheduling_agent (128.8s)  ->  11_extraction_scheduling_logic.json
  |
Wave 3  (6.4s)
  [OK] enrichment_agent (6.4s)  ->  18_quality_enrichment.json
  [OK] postprocessing_agent (0.0s)  ->  15_quality_postprocessing.json
  [OK] reconciliation_agent (0.3s)  ->  16_quality_reconciliation.json
  [OK] validation_agent (0.2s)  ->  17_quality_validation.json
  |
Output
  [OK] Alexion_NCT04573309_Wilsons_usdm.json
  [OK] Alexion_NCT04573309_Wilsons_provenance.json
```

## Agent Results

| Step | Agent | Category | Status | Time (s) | Tokens | API Calls | Pages | Output File |
|------|-------|----------|--------|----------|--------|-----------|-------|-------------|
| 01 | metadata_agent | extraction | OK | 13.7 | 4,340 | 1 | 0-2 | `01_extraction_metadata.json` |
| 02 | soa_vision_agent | extraction | OK | 71.3 | 24,344 | 1 | 9-15,23-25 | `02_extraction_soa_vision.json` |
| 03 | soa_text_agent | extraction | OK | 97.7 | 36,062 | 1 | 9-15,23-25 | `03_extraction_soa_text.json` |
| 04 | narrative_agent | extraction | OK | 30.2 | 19,923 | 2 | 2-3,6,8,12-13,15-16,20,29 | `04_extraction_narrative.json` |
| 05 | docstructure_agent | extraction | OK | 89.1 | 18,004 | 1 | 0-4,6-7,20,25-26,34,41,45,47-50,52,54 | `05_extraction_document_structure.json` |
| 06 | eligibility_agent | extraction | OK | 64.4 | 14,033 | 1 | 29-35 | `06_extraction_eligibility.json` |
| 07 | objectives_agent | extraction | OK | 99.0 | 25,688 | 2 | 7-9,26-29 | `07_extraction_objectives.json` |
| 08 | studydesign_agent | extraction | OK | 13.3 | 14,139 | 1 | 0-5,7-11,19-21,23-27 | `08_extraction_study_design.json` |
| 09 | procedures_agent | extraction | OK | 47.1 | 19,998 | 1 | 2,4,9,13-16,18,20,22,30,37,41,43-44 | `09_extraction_procedures_devices.json` |
| 10 | interventions_agent | extraction | OK | 22.9 | 34,791 | 1 | 2-7,9-17,19-22,24-27,29-38,40-48 | `10_extraction_interventions.json` |
| 11 | scheduling_agent | extraction | OK | 128.8 | 33,081 | 1 | 2,4,10,12,15,17,20,25,27,29,32,37,39-42,57 | `11_extraction_scheduling_logic.json` |
| 12 | execution_agent | extraction | OK | 102.8 | 28,324 | 9 | 0-41,50-53,68 | `12_extraction_execution_model.json` |
| 13 | advanced_agent | extraction | OK | 9.0 | 17,262 | 1 | 0-29,69-71 | `13_extraction_advanced_entities.json` |
| 14 | biomedical_concept_agent | extraction | OK | 74.4 | 11,846 | 1 |  | `14_extraction_biomedical_concepts.json` |
| 15 | postprocessing_agent | quality | OK | 0.0 | 0 | 0 |  | `15_quality_postprocessing.json` |
| 16 | reconciliation_agent | quality | OK | 0.3 | 0 | 0 |  | `16_quality_reconciliation.json` |
| 17 | validation_agent | quality | OK | 0.2 | 0 | 0 |  | `17_quality_validation.json` |
| 18 | enrichment_agent | quality | OK | 6.4 | 0 | 44 |  | `18_quality_enrichment.json` |
| 19 | usdm-generator | support | OK | 0.9 | 0 | 0 |  | `19_support_usdm_generator.json` |
| 20 | provenance | support | OK | 0.0 | 0 | 0 |  | `20_support_provenance.json` |
| 00 | pdf-parser | support | OK | 1.9 | 0 | 0 | | |

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
- `Alexion_NCT04573309_Wilsons.pdf`
- `Alexion_NCT04573309_Wilsons_provenance.json`
- `Alexion_NCT04573309_Wilsons_usdm.json`
- `conformance_report.json`
- `id_mapping.json`
- `soa_page_010.png`
- `soa_page_011.png`
- `soa_page_012.png`
- `soa_page_013.png`
- `soa_page_014.png`
- `soa_page_015.png`
- `soa_page_016.png`
- `soa_page_024.png`
- `soa_page_025.png`
- `soa_page_026.png`
