# Pipeline Result: Alexion_NCT04573309_Wilsons

**Status:** SUCCESS
**PDF:** `Alexion_NCT04573309_Wilsons.pdf`
**Model:** cortex/reforge-claude-opus-5
**Started:** 2026-10-09 16:21:41
**Finished:** 2026-10-09 16:30:59
**Duration:** 557.9s
**Entities:** 1086
**Waves:** 4

## Statistics

| Metric | Value |
|--------|-------|
| Total Agents | 21 |
| Succeeded | 21 |
| Failed | 0 |
| Total Entities | 1086 |
| Total Tokens | 331,721 |
| Total API Calls | 56 |
| Total Duration | 557.9s |

## Execution Flow

```
Wave 0  (248.8s)
  [OK] docstructure_agent (248.8s)  ->  05_extraction_document_structure.json
  [OK] metadata_agent (162.3s)  ->  01_extraction_metadata.json
  [OK] narrative_agent (210.1s)  ->  04_extraction_narrative.json
  [OK] pdf-parser (0.9s)
  [OK] provenance (0.0s)  ->  20_support_provenance.json
  [OK] soa_vision_agent (227.9s)  ->  02_extraction_soa_vision.json
  [OK] usdm-generator (1.1s)  ->  19_support_usdm_generator.json
  |
Wave 1  (123.4s)
  [OK] advanced_agent (23.5s)  ->  13_extraction_advanced_entities.json
  [OK] eligibility_agent (98.3s)  ->  06_extraction_eligibility.json
  [OK] objectives_agent (123.4s)  ->  07_extraction_objectives.json
  [OK] procedures_agent (42.5s)  ->  09_extraction_procedures_devices.json
  [OK] soa_text_agent (92.8s)  ->  03_extraction_soa_text.json
  [OK] studydesign_agent (20.3s)  ->  08_extraction_study_design.json
  |
Wave 2  (137.1s)
  [OK] biomedical_concept_agent (76.7s)  ->  14_extraction_biomedical_concepts.json
  [OK] execution_agent (104.5s)  ->  12_extraction_execution_model.json
  [OK] interventions_agent (19.3s)  ->  10_extraction_interventions.json
  [OK] scheduling_agent (137.1s)  ->  11_extraction_scheduling_logic.json
  |
Wave 3  (14.4s)
  [OK] enrichment_agent (14.4s)  ->  18_quality_enrichment.json
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
| 01 | metadata_agent | extraction | OK | 162.3 | 4,340 | 1 | 0-2 | `01_extraction_metadata.json` |
| 02 | soa_vision_agent | extraction | OK | 227.9 | 24,975 | 1 | 9-15,23-25 | `02_extraction_soa_vision.json` |
| 03 | soa_text_agent | extraction | OK | 92.8 | 35,990 | 1 | 9-15,23-25 | `03_extraction_soa_text.json` |
| 04 | narrative_agent | extraction | OK | 210.1 | 27,964 | 2 | 2-6,8,12-13,15-16,20,29,67-68 | `04_extraction_narrative.json` |
| 05 | docstructure_agent | extraction | OK | 248.8 | 18,945 | 1 | 0-4,6-7,20,25-26,34,41,45,47-50,52,54 | `05_extraction_document_structure.json` |
| 06 | eligibility_agent | extraction | OK | 98.3 | 19,907 | 1 | 29-35 | `06_extraction_eligibility.json` |
| 07 | objectives_agent | extraction | OK | 123.4 | 34,601 | 2 | 7-10,21-23,26-29 | `07_extraction_objectives.json` |
| 08 | studydesign_agent | extraction | OK | 20.3 | 14,792 | 1 | 0-5,7-11,19-21,23-27 | `08_extraction_study_design.json` |
| 09 | procedures_agent | extraction | OK | 42.5 | 19,744 | 1 | 2,4,9,13-16,18,20,22,30,37,41,43-44 | `09_extraction_procedures_devices.json` |
| 10 | interventions_agent | extraction | OK | 19.3 | 35,199 | 1 | 2-7,9-17,19-22,24-27,29-38,40-48 | `10_extraction_interventions.json` |
| 11 | scheduling_agent | extraction | OK | 137.1 | 34,463 | 1 | 2,4,10,12,15,17,20,25,27,29,32,37,39-42,57 | `11_extraction_scheduling_logic.json` |
| 12 | execution_agent | extraction | OK | 104.5 | 28,120 | 9 | 0-41,50-53,68 | `12_extraction_execution_model.json` |
| 13 | advanced_agent | extraction | OK | 23.5 | 20,395 | 1 | 0-29,69-71 | `13_extraction_advanced_entities.json` |
| 14 | biomedical_concept_agent | extraction | OK | 76.7 | 12,286 | 1 |  | `14_extraction_biomedical_concepts.json` |
| 15 | postprocessing_agent | quality | OK | 0.0 | 0 | 0 |  | `15_quality_postprocessing.json` |
| 16 | reconciliation_agent | quality | OK | 0.3 | 0 | 0 |  | `16_quality_reconciliation.json` |
| 17 | validation_agent | quality | OK | 0.0 | 0 | 0 |  | `17_quality_validation.json` |
| 18 | enrichment_agent | quality | OK | 14.4 | 0 | 32 |  | `18_quality_enrichment.json` |
| 19 | usdm-generator | support | OK | 1.1 | 0 | 0 |  | `19_support_usdm_generator.json` |
| 20 | provenance | support | OK | 0.0 | 0 | 0 |  | `20_support_provenance.json` |
| 00 | pdf-parser | support | OK | 0.9 | 0 | 0 | | |

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
