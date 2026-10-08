# Pipeline Result: Alexion_NCT04573309_Wilsons

**Status:** SUCCESS
**PDF:** `Alexion_NCT04573309_Wilsons.pdf`
**Model:** cortex/reforge-claude-opus-5
**Started:** 2026-10-08 13:30:00
**Finished:** 2026-10-08 13:36:17
**Duration:** 376.9s
**Entities:** 1077
**Waves:** 4

## Statistics

| Metric | Value |
|--------|-------|
| Total Agents | 21 |
| Succeeded | 21 |
| Failed | 0 |
| Total Entities | 1077 |
| Total Tokens | 323,133 |
| Total API Calls | 55 |
| Total Duration | 376.9s |

## Execution Flow

```
Wave 0  (98.4s)
  [OK] docstructure_agent (98.4s)  ->  05_extraction_document_structure.json
  [OK] metadata_agent (16.1s)  ->  01_extraction_metadata.json
  [OK] narrative_agent (62.8s)  ->  04_extraction_narrative.json
  [OK] pdf-parser (1.8s)
  [OK] provenance (0.0s)  ->  20_support_provenance.json
  [OK] soa_vision_agent (70.7s)  ->  02_extraction_soa_vision.json
  [OK] usdm-generator (0.0s)  ->  19_support_usdm_generator.json
  |
Wave 1  (126.8s)
  [OK] advanced_agent (24.1s)  ->  13_extraction_advanced_entities.json
  [OK] eligibility_agent (65.1s)  ->  06_extraction_eligibility.json
  [OK] objectives_agent (126.8s)  ->  07_extraction_objectives.json
  [OK] procedures_agent (43.4s)  ->  09_extraction_procedures_devices.json
  [OK] soa_text_agent (95.4s)  ->  03_extraction_soa_text.json
  [OK] studydesign_agent (18.0s)  ->  08_extraction_study_design.json
  |
Wave 2  (119.7s)
  [OK] biomedical_concept_agent (73.1s)  ->  14_extraction_biomedical_concepts.json
  [OK] execution_agent (106.6s)  ->  12_extraction_execution_model.json
  [OK] interventions_agent (19.0s)  ->  10_extraction_interventions.json
  [OK] scheduling_agent (119.7s)  ->  11_extraction_scheduling_logic.json
  |
Wave 3  (4.8s)
  [OK] enrichment_agent (4.8s)  ->  18_quality_enrichment.json
  [OK] postprocessing_agent (0.0s)  ->  15_quality_postprocessing.json
  [OK] reconciliation_agent (0.2s)  ->  16_quality_reconciliation.json
  [OK] validation_agent (0.3s)  ->  17_quality_validation.json
  |
Output
  [OK] Alexion_NCT04573309_Wilsons_usdm.json
  [OK] Alexion_NCT04573309_Wilsons_provenance.json
```

## Agent Results

| Step | Agent | Category | Status | Time (s) | Tokens | API Calls | Pages | Output File |
|------|-------|----------|--------|----------|--------|-----------|-------|-------------|
| 01 | metadata_agent | extraction | OK | 16.1 | 4,340 | 1 | 0-2 | `01_extraction_metadata.json` |
| 02 | soa_vision_agent | extraction | OK | 70.7 | 24,354 | 1 | 9-15,23-25 | `02_extraction_soa_vision.json` |
| 03 | soa_text_agent | extraction | OK | 95.4 | 36,302 | 1 | 9-15,23-25 | `03_extraction_soa_text.json` |
| 04 | narrative_agent | extraction | OK | 62.8 | 27,962 | 2 | 2-6,8,12-13,15-16,20,29,67-68 | `04_extraction_narrative.json` |
| 05 | docstructure_agent | extraction | OK | 98.4 | 18,342 | 1 | 0-4,6-7,20,25-26,34,41,45,47-50,52,54 | `05_extraction_document_structure.json` |
| 06 | eligibility_agent | extraction | OK | 65.1 | 14,252 | 1 | 29-35 | `06_extraction_eligibility.json` |
| 07 | objectives_agent | extraction | OK | 126.8 | 34,428 | 2 | 7-10,21-23,26-29 | `07_extraction_objectives.json` |
| 08 | studydesign_agent | extraction | OK | 18.0 | 14,605 | 1 | 0-5,7-11,19-21,23-27 | `08_extraction_study_design.json` |
| 09 | procedures_agent | extraction | OK | 43.4 | 19,748 | 1 | 2,4,9,13-16,18,20,22,30,37,41,43-44 | `09_extraction_procedures_devices.json` |
| 10 | interventions_agent | extraction | OK | 19.0 | 35,161 | 1 | 2-7,9-17,19-22,24-27,29-38,40-48 | `10_extraction_interventions.json` |
| 11 | scheduling_agent | extraction | OK | 119.7 | 32,616 | 1 | 2,4,10,12,15,17,20,25,27,29,32,37,39-42,57 | `11_extraction_scheduling_logic.json` |
| 12 | execution_agent | extraction | OK | 106.6 | 28,605 | 9 | 0-41,50-53,68 | `12_extraction_execution_model.json` |
| 13 | advanced_agent | extraction | OK | 24.1 | 20,256 | 1 | 0-29,69-71 | `13_extraction_advanced_entities.json` |
| 14 | biomedical_concept_agent | extraction | OK | 73.1 | 12,162 | 1 |  | `14_extraction_biomedical_concepts.json` |
| 15 | postprocessing_agent | quality | OK | 0.0 | 0 | 0 |  | `15_quality_postprocessing.json` |
| 16 | reconciliation_agent | quality | OK | 0.2 | 0 | 0 |  | `16_quality_reconciliation.json` |
| 17 | validation_agent | quality | OK | 0.3 | 0 | 0 |  | `17_quality_validation.json` |
| 18 | enrichment_agent | quality | OK | 4.8 | 0 | 31 |  | `18_quality_enrichment.json` |
| 19 | usdm-generator | support | OK | 0.0 | 0 | 0 |  | `19_support_usdm_generator.json` |
| 20 | provenance | support | OK | 0.0 | 0 | 0 |  | `20_support_provenance.json` |
| 00 | pdf-parser | support | OK | 1.8 | 0 | 0 | | |

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
