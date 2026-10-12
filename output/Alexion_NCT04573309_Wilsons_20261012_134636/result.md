# Pipeline Result: Alexion_NCT04573309_Wilsons

**Status:** SUCCESS
**PDF:** `Alexion_NCT04573309_Wilsons.pdf`
**Model:** cortex/reforge-claude-opus-5
**Started:** 2026-10-12 13:46:36
**Finished:** 2026-10-12 13:54:45
**Duration:** 489.3s
**Entities:** 903
**Waves:** 4

## Statistics

| Metric | Value |
|--------|-------|
| Total Agents | 21 |
| Succeeded | 21 |
| Failed | 0 |
| Total Entities | 903 |
| Total Tokens | 377,731 |
| Total API Calls | 48 |
| Total Duration | 489.3s |

## Execution Flow

```
Wave 0  (154.5s)
  [OK] docstructure_agent (66.3s)  ->  05_extraction_document_structure.json
  [OK] metadata_agent (11.8s)  ->  01_extraction_metadata.json
  [OK] narrative_agent (77.4s)  ->  04_extraction_narrative.json
  [OK] pdf-parser (2.3s)
  [OK] provenance (0.0s)  ->  20_support_provenance.json
  [OK] soa_vision_agent (154.5s)  ->  02_extraction_soa_vision.json
  [OK] usdm-generator (1.4s)  ->  19_support_usdm_generator.json
  |
Wave 1  (110.5s)
  [OK] advanced_agent (28.0s)  ->  13_extraction_advanced_entities.json
  [OK] eligibility_agent (70.4s)  ->  06_extraction_eligibility.json
  [OK] objectives_agent (110.5s)  ->  07_extraction_objectives.json
  [OK] procedures_agent (40.3s)  ->  09_extraction_procedures_devices.json
  [OK] soa_text_agent (45.3s)  ->  03_extraction_soa_text.json
  [OK] studydesign_agent (18.0s)  ->  08_extraction_study_design.json
  |
Wave 2  (189.5s)
  [OK] biomedical_concept_agent (29.9s)  ->  14_extraction_biomedical_concepts.json
  [OK] execution_agent (71.2s)  ->  12_extraction_execution_model.json
  [OK] interventions_agent (23.7s)  ->  10_extraction_interventions.json
  [OK] scheduling_agent (189.5s)  ->  11_extraction_scheduling_logic.json
  |
Wave 3  (4.6s)
  [OK] enrichment_agent (4.6s)  ->  18_quality_enrichment.json
  [OK] postprocessing_agent (0.0s)  ->  15_quality_postprocessing.json
  [OK] reconciliation_agent (0.1s)  ->  16_quality_reconciliation.json
  [OK] validation_agent (0.0s)  ->  17_quality_validation.json
  |
Output
  [OK] Alexion_NCT04573309_Wilsons_usdm.json
  [OK] Alexion_NCT04573309_Wilsons_provenance.json
```

## Agent Results

| Step | Agent | Category | Status | Time (s) | Tokens | API Calls | Pages | Output File |
|------|-------|----------|--------|----------|--------|-----------|-------|-------------|
| 01 | metadata_agent | extraction | OK | 11.8 | 5,469 | 1 | 0-2 | `01_extraction_metadata.json` |
| 02 | soa_vision_agent | extraction | OK | 154.5 | 43,235 | 2 | 9-15,23-25 | `02_extraction_soa_vision.json` |
| 03 | soa_text_agent | extraction | OK | 45.3 | 30,453 | 1 | 9-15,23-25 | `03_extraction_soa_text.json` |
| 04 | narrative_agent | extraction | OK | 77.4 | 37,305 | 2 | 2-6,8,12-13,15-16,20,29,67-68 | `04_extraction_narrative.json` |
| 05 | docstructure_agent | extraction | OK | 66.3 | 21,499 | 1 | 0-4,6-7,20,25-26,34,41,45,47-50,52,54 | `05_extraction_document_structure.json` |
| 06 | eligibility_agent | extraction | OK | 70.4 | 19,920 | 1 | 29-35 | `06_extraction_eligibility.json` |
| 07 | objectives_agent | extraction | OK | 110.5 | 41,501 | 2 | 7-10,21-23,26-29 | `07_extraction_objectives.json` |
| 08 | studydesign_agent | extraction | OK | 18.0 | 16,753 | 1 | 0-5,7-11,19-21,23-27 | `08_extraction_study_design.json` |
| 09 | procedures_agent | extraction | OK | 40.3 | 22,432 | 1 | 2,4,9,13-16,18,20,22,30,37,41,43-44 | `09_extraction_procedures_devices.json` |
| 10 | interventions_agent | extraction | OK | 23.7 | 37,408 | 1 | 2-7,9-17,19-22,24-27,29-38,40-48 | `10_extraction_interventions.json` |
| 11 | scheduling_agent | extraction | OK | 189.5 | 42,603 | 1 | 2,4,10,12,15,17,20,25,27,29,32,37,39-42,57 | `11_extraction_scheduling_logic.json` |
| 12 | execution_agent | extraction | OK | 71.2 | 27,498 | 9 | 0-41,50-53,68 | `12_extraction_execution_model.json` |
| 13 | advanced_agent | extraction | OK | 28.0 | 23,875 | 1 | 0-29,69-71 | `13_extraction_advanced_entities.json` |
| 14 | biomedical_concept_agent | extraction | OK | 29.9 | 7,780 | 1 |  | `14_extraction_biomedical_concepts.json` |
| 15 | postprocessing_agent | quality | OK | 0.0 | 0 | 0 |  | `15_quality_postprocessing.json` |
| 16 | reconciliation_agent | quality | OK | 0.1 | 0 | 0 |  | `16_quality_reconciliation.json` |
| 17 | validation_agent | quality | OK | 0.0 | 0 | 0 |  | `17_quality_validation.json` |
| 18 | enrichment_agent | quality | OK | 4.6 | 0 | 23 |  | `18_quality_enrichment.json` |
| 19 | usdm-generator | support | OK | 1.4 | 0 | 0 |  | `19_support_usdm_generator.json` |
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
