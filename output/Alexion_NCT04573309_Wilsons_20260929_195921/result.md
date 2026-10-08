# Pipeline Result: Alexion_NCT04573309_Wilsons

**Status:** SUCCESS
**PDF:** `Alexion_NCT04573309_Wilsons.pdf`
**Model:** cortex/reforge-claude-opus-5
**Started:** 2026-09-29 19:59:21
**Finished:** 2026-09-29 20:09:44
**Duration:** 623.2s
**Entities:** 1016
**Waves:** 4

## Statistics

| Metric | Value |
|--------|-------|
| Total Agents | 21 |
| Succeeded | 21 |
| Failed | 0 |
| Total Entities | 1016 |
| Total Tokens | 391,818 |
| Total API Calls | 78 |
| Total Duration | 623.2s |

## Execution Flow

```
Wave 0  (113.1s)
  [OK] docstructure_agent (113.1s)  ->  05_extraction_document_structure.json
  [OK] metadata_agent (14.9s)  ->  01_extraction_metadata.json
  [OK] narrative_agent (28.6s)  ->  04_extraction_narrative.json
  [OK] pdf-parser (0.7s)
  [OK] provenance (0.0s)  ->  20_support_provenance.json
  [OK] soa_vision_agent (71.8s)  ->  02_extraction_soa_vision.json
  [OK] usdm-generator (0.0s)  ->  19_support_usdm_generator.json
  |
Wave 1  (208.9s)
  [OK] advanced_agent (8.5s)  ->  13_extraction_advanced_entities.json
  [OK] eligibility_agent (79.4s)  ->  06_extraction_eligibility.json
  [OK] objectives_agent (133.3s)  ->  07_extraction_objectives.json
  [OK] procedures_agent (81.6s)  ->  09_extraction_procedures_devices.json
  [OK] soa_text_agent (208.9s)  ->  03_extraction_soa_text.json
  [OK] studydesign_agent (16.6s)  ->  08_extraction_study_design.json
  |
Wave 2  (255.4s)
  [OK] biomedical_concept_agent (199.6s)  ->  14_extraction_biomedical_concepts.json
  [OK] execution_agent (255.4s)  ->  12_extraction_execution_model.json
  [OK] interventions_agent (32.9s)  ->  10_extraction_interventions.json
  [OK] scheduling_agent (135.1s)  ->  11_extraction_scheduling_logic.json
  |
Wave 3  (14.8s)
  [OK] enrichment_agent (14.8s)  ->  18_quality_enrichment.json
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
| 01 | metadata_agent | extraction | OK | 14.9 | 5,494 | 1 | 0-2 | `01_extraction_metadata.json` |
| 02 | soa_vision_agent | extraction | OK | 71.8 | 24,600 | 1 | 9-15,23-25 | `02_extraction_soa_vision.json` |
| 03 | soa_text_agent | extraction | OK | 208.9 | 49,580 | 1 | 9-15,23-25 | `03_extraction_soa_text.json` |
| 04 | narrative_agent | extraction | OK | 28.6 | 24,966 | 2 | 2-3,6,8,12-13,15-16,20,29 | `04_extraction_narrative.json` |
| 05 | docstructure_agent | extraction | OK | 113.1 | 26,971 | 1 | 0-4,6-7,20,25-26,34,41,45,47-50,52,54 | `05_extraction_document_structure.json` |
| 06 | eligibility_agent | extraction | OK | 79.4 | 18,268 | 1 | 29-35 | `06_extraction_eligibility.json` |
| 07 | objectives_agent | extraction | OK | 133.3 | 31,373 | 2 | 7-9,26-29 | `07_extraction_objectives.json` |
| 08 | studydesign_agent | extraction | OK | 16.6 | 19,134 | 1 | 0-5,7-11,19-21,23-27 | `08_extraction_study_design.json` |
| 09 | procedures_agent | extraction | OK | 81.6 | 28,624 | 1 | 2,4,9,13-16,18,20,22,30,37,41,43-44 | `09_extraction_procedures_devices.json` |
| 10 | interventions_agent | extraction | OK | 32.9 | 46,904 | 1 | 2-7,9-17,19-22,24-27,29-38,40-48 | `10_extraction_interventions.json` |
| 11 | scheduling_agent | extraction | OK | 135.1 | 33,258 | 1 | 2,4,10,12,15,17,20,25,27,29,32,37,39-42,57 | `11_extraction_scheduling_logic.json` |
| 12 | execution_agent | extraction | OK | 255.4 | 42,753 | 9 | 0-41,50-53,68 | `12_extraction_execution_model.json` |
| 13 | advanced_agent | extraction | OK | 8.5 | 23,556 | 1 | 0-29,69-71 | `13_extraction_advanced_entities.json` |
| 14 | biomedical_concept_agent | extraction | OK | 199.6 | 16,337 | 1 |  | `14_extraction_biomedical_concepts.json` |
| 15 | postprocessing_agent | quality | OK | 0.0 | 0 | 0 |  | `15_quality_postprocessing.json` |
| 16 | reconciliation_agent | quality | OK | 0.3 | 0 | 0 |  | `16_quality_reconciliation.json` |
| 17 | validation_agent | quality | OK | 0.0 | 0 | 0 |  | `17_quality_validation.json` |
| 18 | enrichment_agent | quality | OK | 14.8 | 0 | 54 |  | `18_quality_enrichment.json` |
| 19 | usdm-generator | support | OK | 0.0 | 0 | 0 |  | `19_support_usdm_generator.json` |
| 20 | provenance | support | OK | 0.0 | 0 | 0 |  | `20_support_provenance.json` |
| 00 | pdf-parser | support | OK | 0.7 | 0 | 0 | | |

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
