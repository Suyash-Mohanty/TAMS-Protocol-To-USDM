# Pipeline Result: Alexion_NCT04573309_Wilsons

**Status:** SUCCESS
**PDF:** `Alexion_NCT04573309_Wilsons.pdf`
**Model:** cortex/reforge-claude-opus-5
**Started:** 2026-09-07 17:03:08
**Finished:** 2026-09-07 17:11:43
**Duration:** 515.1s
**Entities:** 1000
**Waves:** 4

## Statistics

| Metric | Value |
|--------|-------|
| Total Agents | 21 |
| Succeeded | 21 |
| Failed | 0 |
| Total Entities | 1000 |
| Total Tokens | 333,800 |
| Total API Calls | 71 |
| Total Duration | 515.1s |

## Execution Flow

```
Wave 0  (240.6s)
  [OK] docstructure_agent (79.5s)  ->  05_extraction_document_structure.json
  [OK] metadata_agent (13.5s)  ->  01_extraction_metadata.json
  [OK] narrative_agent (29.1s)  ->  04_extraction_narrative.json
  [OK] pdf-parser (1.0s)
  [OK] provenance (0.0s)  ->  20_support_provenance.json
  [OK] soa_vision_agent (240.6s)  ->  02_extraction_soa_vision.json
  [OK] usdm-generator (0.0s)  ->  19_support_usdm_generator.json
  |
Wave 1  (89.0s)
  [OK] advanced_agent (7.8s)  ->  13_extraction_advanced_entities.json
  [OK] eligibility_agent (65.0s)  ->  06_extraction_eligibility.json
  [OK] objectives_agent (89.0s)  ->  07_extraction_objectives.json
  [OK] procedures_agent (47.6s)  ->  09_extraction_procedures_devices.json
  [OK] soa_text_agent (87.1s)  ->  03_extraction_soa_text.json
  [OK] studydesign_agent (15.9s)  ->  08_extraction_study_design.json
  |
Wave 2  (121.4s)
  [OK] biomedical_concept_agent (75.8s)  ->  14_extraction_biomedical_concepts.json
  [OK] execution_agent (97.9s)  ->  12_extraction_execution_model.json
  [OK] interventions_agent (24.2s)  ->  10_extraction_interventions.json
  [OK] scheduling_agent (121.4s)  ->  11_extraction_scheduling_logic.json
  |
Wave 3  (7.3s)
  [OK] enrichment_agent (7.3s)  ->  18_quality_enrichment.json
  [OK] postprocessing_agent (0.0s)  ->  15_quality_postprocessing.json
  [OK] reconciliation_agent (0.3s)  ->  16_quality_reconciliation.json
  [OK] validation_agent (0.0s)  ->  17_quality_validation.json
  |
Output
  [OK] Alexion_NCT04573309_Wilsons_usdm.json
  [OK] Alexion_NCT04573309_Wilsons_provenance.json
```

## Agent Results

| Step | Agent | Category | Status | Time (s) | Tokens | API Calls | Pages | Output File |
|------|-------|----------|--------|----------|--------|-----------|-------|-------------|
| 01 | metadata_agent | extraction | OK | 13.5 | 4,340 | 1 | 0-2 | `01_extraction_metadata.json` |
| 02 | soa_vision_agent | extraction | OK | 240.6 | 60,395 | 3 | 9-15,23-25 | `02_extraction_soa_vision.json` |
| 03 | soa_text_agent | extraction | OK | 87.1 | 33,987 | 1 | 9-15,23-25 | `03_extraction_soa_text.json` |
| 04 | narrative_agent | extraction | OK | 29.1 | 19,902 | 2 | 2-3,6,8,12-13,15-16,20,29 | `04_extraction_narrative.json` |
| 05 | docstructure_agent | extraction | OK | 79.5 | 17,849 | 1 | 0-4,6-7,20,25-26,34,41,45,47-50,52,54 | `05_extraction_document_structure.json` |
| 06 | eligibility_agent | extraction | OK | 65.0 | 13,952 | 1 | 29-35 | `06_extraction_eligibility.json` |
| 07 | objectives_agent | extraction | OK | 89.0 | 24,501 | 2 | 7-9,26-29 | `07_extraction_objectives.json` |
| 08 | studydesign_agent | extraction | OK | 15.9 | 14,281 | 1 | 0-5,7-11,19-21,23-27 | `08_extraction_study_design.json` |
| 09 | procedures_agent | extraction | OK | 47.6 | 20,069 | 1 | 2,4,9,13-16,18,20,22,30,37,41,43-44 | `09_extraction_procedures_devices.json` |
| 10 | interventions_agent | extraction | OK | 24.2 | 34,946 | 1 | 2-7,9-17,19-22,24-27,29-38,40-48 | `10_extraction_interventions.json` |
| 11 | scheduling_agent | extraction | OK | 121.4 | 31,923 | 1 | 2,4,10,12,15,17,20,25,27,29,32,37,39-42,57 | `11_extraction_scheduling_logic.json` |
| 12 | execution_agent | extraction | OK | 97.9 | 28,110 | 9 | 0-41,50-53,68 | `12_extraction_execution_model.json` |
| 13 | advanced_agent | extraction | OK | 7.8 | 17,262 | 1 | 0-29,69-71 | `13_extraction_advanced_entities.json` |
| 14 | biomedical_concept_agent | extraction | OK | 75.8 | 12,283 | 1 |  | `14_extraction_biomedical_concepts.json` |
| 15 | postprocessing_agent | quality | OK | 0.0 | 0 | 0 |  | `15_quality_postprocessing.json` |
| 16 | reconciliation_agent | quality | OK | 0.3 | 0 | 0 |  | `16_quality_reconciliation.json` |
| 17 | validation_agent | quality | OK | 0.0 | 0 | 0 |  | `17_quality_validation.json` |
| 18 | enrichment_agent | quality | OK | 7.3 | 0 | 45 |  | `18_quality_enrichment.json` |
| 19 | usdm-generator | support | OK | 0.0 | 0 | 0 |  | `19_support_usdm_generator.json` |
| 20 | provenance | support | OK | 0.0 | 0 | 0 |  | `20_support_provenance.json` |
| 00 | pdf-parser | support | OK | 1.0 | 0 | 0 | | |

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
