# Pipeline Result: Alexion_NCT04573309_Wilsons

**Status:** FAILED
**PDF:** `Alexion_NCT04573309_Wilsons.pdf`
**Model:** cortex/reforge-claude-opus-5
**Started:** 2026-09-07 16:33:34
**Finished:** 2026-09-07 16:45:19
**Duration:** 705.2s
**Entities:** 921
**Waves:** 4

## Statistics

| Metric | Value |
|--------|-------|
| Total Agents | 21 |
| Succeeded | 20 |
| Failed | 1 |
| Total Entities | 921 |
| Total Tokens | 268,230 |
| Total API Calls | 69 |
| Total Duration | 705.2s |

## Execution Flow

```
Wave 0  (87.2s)
  [OK] docstructure_agent (87.2s)  ->  05_extraction_document_structure.json
  [OK] metadata_agent (16.0s)  ->  01_extraction_metadata.json
  [OK] narrative_agent (32.3s)  ->  04_extraction_narrative.json
  [OK] pdf-parser (1.9s)
  [OK] provenance (0.0s)  ->  20_support_provenance.json
  [OK] soa_vision_agent (54.5s)  ->  02_extraction_soa_vision.json
  [OK] usdm-generator (0.0s)  ->  19_support_usdm_generator.json
  |
Wave 1  (97.4s)
  [OK] advanced_agent (7.7s)  ->  13_extraction_advanced_entities.json
  [OK] eligibility_agent (63.7s)  ->  06_extraction_eligibility.json
  [OK] objectives_agent (97.4s)  ->  07_extraction_objectives.json
  [OK] procedures_agent (47.0s)  ->  09_extraction_procedures_devices.json
  [OK] soa_text_agent (93.5s)  ->  03_extraction_soa_text.json
  [OK] studydesign_agent (17.2s)  ->  08_extraction_study_design.json
  |
Wave 2  (106.1s)
  [OK] biomedical_concept_agent (76.3s)  ->  14_extraction_biomedical_concepts.json
  [OK] execution_agent (106.1s)  ->  12_extraction_execution_model.json
  [OK] interventions_agent (23.1s)  ->  10_extraction_interventions.json
  [FAIL] scheduling_agent (0.0s)  ->  11_extraction_scheduling_logic.json
  |
Wave 3  (7.3s)
  [OK] enrichment_agent (7.3s)  ->  18_quality_enrichment.json
  [OK] postprocessing_agent (0.0s)  ->  15_quality_postprocessing.json
  [OK] reconciliation_agent (0.2s)  ->  16_quality_reconciliation.json
  [OK] validation_agent (0.0s)  ->  17_quality_validation.json
  |
Output
  [OK] Alexion_NCT04573309_Wilsons_usdm.json
  [OK] Alexion_NCT04573309_Wilsons_provenance.json
```

## Agent Results

| Step | Agent | Category | Status | Time (s) | Tokens | API Calls | Pages | Output File |
|------|-------|----------|--------|----------|--------|-----------|-------|-------------|
| 01 | metadata_agent | extraction | OK | 16.0 | 4,338 | 1 | 0-2 | `01_extraction_metadata.json` |
| 02 | soa_vision_agent | extraction | OK | 54.5 | 22,397 | 1 | 9-15,23-25 | `02_extraction_soa_vision.json` |
| 03 | soa_text_agent | extraction | OK | 93.5 | 36,343 | 1 | 9-15,23-25 | `03_extraction_soa_text.json` |
| 04 | narrative_agent | extraction | OK | 32.3 | 19,806 | 2 | 2-3,6,8,12-13,15-16,20,29 | `04_extraction_narrative.json` |
| 05 | docstructure_agent | extraction | OK | 87.2 | 18,205 | 1 | 0-4,6-7,20,25-26,34,41,45,47-50,52,54 | `05_extraction_document_structure.json` |
| 06 | eligibility_agent | extraction | OK | 63.7 | 13,976 | 1 | 29-35 | `06_extraction_eligibility.json` |
| 07 | objectives_agent | extraction | OK | 97.4 | 25,439 | 2 | 7-9,26-29 | `07_extraction_objectives.json` |
| 08 | studydesign_agent | extraction | OK | 17.2 | 14,340 | 1 | 0-5,7-11,19-21,23-27 | `08_extraction_study_design.json` |
| 09 | procedures_agent | extraction | OK | 47.0 | 20,110 | 1 | 2,4,9,13-16,18,20,22,30,37,41,43-44 | `09_extraction_procedures_devices.json` |
| 10 | interventions_agent | extraction | OK | 23.1 | 34,896 | 1 | 2-7,9-17,19-22,24-27,29-38,40-48 | `10_extraction_interventions.json` |
| 11 | scheduling_agent | extraction | FAIL | 0.0 | 0 | 0 |  | `11_extraction_scheduling_logic.json` |
| 12 | execution_agent | extraction | OK | 106.1 | 28,587 | 9 | 0-41,50-53,68 | `12_extraction_execution_model.json` |
| 13 | advanced_agent | extraction | OK | 7.7 | 17,247 | 1 | 0-29,69-71 | `13_extraction_advanced_entities.json` |
| 14 | biomedical_concept_agent | extraction | OK | 76.3 | 12,546 | 1 |  | `14_extraction_biomedical_concepts.json` |
| 15 | postprocessing_agent | quality | OK | 0.0 | 0 | 0 |  | `15_quality_postprocessing.json` |
| 16 | reconciliation_agent | quality | OK | 0.2 | 0 | 0 |  | `16_quality_reconciliation.json` |
| 17 | validation_agent | quality | OK | 0.0 | 0 | 0 |  | `17_quality_validation.json` |
| 18 | enrichment_agent | quality | OK | 7.3 | 0 | 46 |  | `18_quality_enrichment.json` |
| 19 | usdm-generator | support | OK | 0.0 | 0 | 0 |  | `19_support_usdm_generator.json` |
| 20 | provenance | support | OK | 0.0 | 0 | 0 |  | `20_support_provenance.json` |
| 00 | pdf-parser | support | OK | 1.9 | 0 | 0 | | |

## Failed Agents

- **scheduling_agent**: Failed after 4 attempts: Extraction returned no data

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
