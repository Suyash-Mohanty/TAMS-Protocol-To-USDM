# Pipeline Result: Alexion_NCT04573309_Wilsons

**Status:** SUCCESS
**PDF:** `Alexion_NCT04573309_Wilsons.pdf`
**Model:** cortex/reforge-claude-opus-5
**Started:** 2026-10-09 16:48:52
**Finished:** 2026-10-09 16:56:38
**Duration:** 466.2s
**Entities:** 1061
**Waves:** 4

## Statistics

| Metric | Value |
|--------|-------|
| Total Agents | 21 |
| Succeeded | 21 |
| Failed | 0 |
| Total Entities | 1061 |
| Total Tokens | 344,843 |
| Total API Calls | 57 |
| Total Duration | 466.2s |

## Execution Flow

```
Wave 0  (173.8s)
  [OK] docstructure_agent (76.8s)  ->  05_extraction_document_structure.json
  [OK] metadata_agent (13.1s)  ->  01_extraction_metadata.json
  [OK] narrative_agent (54.3s)  ->  04_extraction_narrative.json
  [OK] pdf-parser (1.7s)
  [OK] provenance (0.0s)  ->  20_support_provenance.json
  [OK] soa_vision_agent (173.8s)  ->  02_extraction_soa_vision.json
  [OK] usdm-generator (0.9s)  ->  19_support_usdm_generator.json
  |
Wave 1  (116.7s)
  [OK] advanced_agent (23.8s)  ->  13_extraction_advanced_entities.json
  [OK] eligibility_agent (95.8s)  ->  06_extraction_eligibility.json
  [OK] objectives_agent (116.7s)  ->  07_extraction_objectives.json
  [OK] procedures_agent (42.9s)  ->  09_extraction_procedures_devices.json
  [OK] soa_text_agent (94.7s)  ->  03_extraction_soa_text.json
  [OK] studydesign_agent (17.4s)  ->  08_extraction_study_design.json
  |
Wave 2  (131.4s)
  [OK] biomedical_concept_agent (73.1s)  ->  14_extraction_biomedical_concepts.json
  [OK] execution_agent (97.7s)  ->  12_extraction_execution_model.json
  [OK] interventions_agent (18.5s)  ->  10_extraction_interventions.json
  [OK] scheduling_agent (131.4s)  ->  11_extraction_scheduling_logic.json
  |
Wave 3  (9.4s)
  [OK] enrichment_agent (9.4s)  ->  18_quality_enrichment.json
  [OK] postprocessing_agent (0.0s)  ->  15_quality_postprocessing.json
  [OK] reconciliation_agent (0.3s)  ->  16_quality_reconciliation.json
  [OK] validation_agent (0.1s)  ->  17_quality_validation.json
  |
Output
  [OK] Alexion_NCT04573309_Wilsons_usdm.json
  [OK] Alexion_NCT04573309_Wilsons_provenance.json
```

## Agent Results

| Step | Agent | Category | Status | Time (s) | Tokens | API Calls | Pages | Output File |
|------|-------|----------|--------|----------|--------|-----------|-------|-------------|
| 01 | metadata_agent | extraction | OK | 13.1 | 4,340 | 1 | 0-2 | `01_extraction_metadata.json` |
| 02 | soa_vision_agent | extraction | OK | 173.8 | 44,117 | 2 | 9-15,23-25 | `02_extraction_soa_vision.json` |
| 03 | soa_text_agent | extraction | OK | 94.7 | 35,397 | 1 | 9-15,23-25 | `03_extraction_soa_text.json` |
| 04 | narrative_agent | extraction | OK | 54.3 | 26,986 | 2 | 2-6,8,12-13,15-16,20,29,67-68 | `04_extraction_narrative.json` |
| 05 | docstructure_agent | extraction | OK | 76.8 | 17,426 | 1 | 0-4,6-7,20,25-26,34,41,45,47-50,52,54 | `05_extraction_document_structure.json` |
| 06 | eligibility_agent | extraction | OK | 95.8 | 19,919 | 1 | 29-35 | `06_extraction_eligibility.json` |
| 07 | objectives_agent | extraction | OK | 116.7 | 32,865 | 2 | 7-10,21-23,26-29 | `07_extraction_objectives.json` |
| 08 | studydesign_agent | extraction | OK | 17.4 | 14,515 | 1 | 0-5,7-11,19-21,23-27 | `08_extraction_study_design.json` |
| 09 | procedures_agent | extraction | OK | 42.9 | 19,729 | 1 | 2,4,9,13-16,18,20,22,30,37,41,43-44 | `09_extraction_procedures_devices.json` |
| 10 | interventions_agent | extraction | OK | 18.5 | 35,101 | 1 | 2-7,9-17,19-22,24-27,29-38,40-48 | `10_extraction_interventions.json` |
| 11 | scheduling_agent | extraction | OK | 131.4 | 33,659 | 1 | 2,4,10,12,15,17,20,25,27,29,32,37,39-42,57 | `11_extraction_scheduling_logic.json` |
| 12 | execution_agent | extraction | OK | 97.7 | 28,018 | 9 | 0-41,50-53,68 | `12_extraction_execution_model.json` |
| 13 | advanced_agent | extraction | OK | 23.8 | 20,395 | 1 | 0-29,69-71 | `13_extraction_advanced_entities.json` |
| 14 | biomedical_concept_agent | extraction | OK | 73.1 | 12,376 | 1 |  | `14_extraction_biomedical_concepts.json` |
| 15 | postprocessing_agent | quality | OK | 0.0 | 0 | 0 |  | `15_quality_postprocessing.json` |
| 16 | reconciliation_agent | quality | OK | 0.3 | 0 | 0 |  | `16_quality_reconciliation.json` |
| 17 | validation_agent | quality | OK | 0.1 | 0 | 0 |  | `17_quality_validation.json` |
| 18 | enrichment_agent | quality | OK | 9.4 | 0 | 32 |  | `18_quality_enrichment.json` |
| 19 | usdm-generator | support | OK | 0.9 | 0 | 0 |  | `19_support_usdm_generator.json` |
| 20 | provenance | support | OK | 0.0 | 0 | 0 |  | `20_support_provenance.json` |
| 00 | pdf-parser | support | OK | 1.7 | 0 | 0 | | |

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
- `Alexion_NCT04573309_Wilsons_citations.json`
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
