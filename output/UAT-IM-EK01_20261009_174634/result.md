# Pipeline Result: UAT-IM-EK01

**Status:** SUCCESS
**PDF:** `UAT-IM-EK01.pdf`
**Model:** cortex/reforge-claude-opus-5
**Started:** 2026-10-09 17:46:34
**Finished:** 2026-10-09 17:54:07
**Duration:** 453.0s
**Entities:** 1149
**Waves:** 4

## Statistics

| Metric | Value |
|--------|-------|
| Total Agents | 21 |
| Succeeded | 21 |
| Failed | 0 |
| Total Entities | 1149 |
| Total Tokens | 317,991 |
| Total API Calls | 86 |
| Total Duration | 453.0s |

## Execution Flow

```
Wave 0  (132.1s)
  [OK] docstructure_agent (132.1s)  ->  05_extraction_document_structure.json
  [OK] metadata_agent (14.0s)  ->  01_extraction_metadata.json
  [OK] narrative_agent (73.3s)  ->  04_extraction_narrative.json
  [OK] pdf-parser (2.1s)
  [OK] provenance (0.0s)  ->  20_support_provenance.json
  [OK] soa_vision_agent (80.8s)  ->  02_extraction_soa_vision.json
  [OK] usdm-generator (4.2s)  ->  19_support_usdm_generator.json
  |
Wave 1  (146.8s)
  [OK] advanced_agent (3.2s)  ->  13_extraction_advanced_entities.json
  [OK] eligibility_agent (31.3s)  ->  06_extraction_eligibility.json
  [OK] objectives_agent (38.3s)  ->  07_extraction_objectives.json
  [OK] procedures_agent (78.5s)  ->  09_extraction_procedures_devices.json
  [OK] soa_text_agent (146.8s)  ->  03_extraction_soa_text.json
  [OK] studydesign_agent (23.6s)  ->  08_extraction_study_design.json
  |
Wave 2  (162.9s)
  [OK] biomedical_concept_agent (162.9s)  ->  14_extraction_biomedical_concepts.json
  [OK] execution_agent (98.9s)  ->  12_extraction_execution_model.json
  [OK] interventions_agent (10.1s)  ->  10_extraction_interventions.json
  [OK] scheduling_agent (55.9s)  ->  11_extraction_scheduling_logic.json
  |
Wave 3  (7.4s)
  [OK] enrichment_agent (7.4s)  ->  18_quality_enrichment.json
  [OK] postprocessing_agent (0.0s)  ->  15_quality_postprocessing.json
  [OK] reconciliation_agent (0.5s)  ->  16_quality_reconciliation.json
  [OK] validation_agent (0.0s)  ->  17_quality_validation.json
  |
Output
  [OK] UAT-IM-EK01_usdm.json
  [OK] UAT-IM-EK01_provenance.json
```

## Agent Results

| Step | Agent | Category | Status | Time (s) | Tokens | API Calls | Pages | Output File |
|------|-------|----------|--------|----------|--------|-----------|-------|-------------|
| 01 | metadata_agent | extraction | OK | 14.0 | 4,878 | 1 | 0-2 | `01_extraction_metadata.json` |
| 02 | soa_vision_agent | extraction | OK | 80.8 | 37,106 | 1 | 8-22,25-27,42-43 | `02_extraction_soa_vision.json` |
| 03 | soa_text_agent | extraction | OK | 146.8 | 45,394 | 1 | 8-22,25-27,42-43 | `03_extraction_soa_text.json` |
| 04 | narrative_agent | extraction | OK | 73.3 | 27,784 | 2 | 2-9,16,19,21,26,71-73 | `04_extraction_narrative.json` |
| 05 | docstructure_agent | extraction | OK | 132.1 | 25,690 | 1 | 0-5,9,11-12,16-17,19-20,31,42,44,49 | `05_extraction_document_structure.json` |
| 06 | eligibility_agent | extraction | OK | 31.3 | 10,558 | 1 | 8-10,29-32 | `06_extraction_eligibility.json` |
| 07 | objectives_agent | extraction | OK | 38.3 | 28,200 | 2 | 5-16,25-28,44-46 | `07_extraction_objectives.json` |
| 08 | studydesign_agent | extraction | OK | 23.6 | 16,572 | 1 | 0-18,27-29 | `08_extraction_study_design.json` |
| 09 | procedures_agent | extraction | OK | 78.5 | 21,530 | 1 | 3-5,9-10,12,14,16-17,19,21,24,31,34-35 | `09_extraction_procedures_devices.json` |
| 10 | interventions_agent | extraction | OK | 10.1 | 24,241 | 1 | 1-10,13-25,27-29,33-43 | `10_extraction_interventions.json` |
| 11 | scheduling_agent | extraction | OK | 55.9 | 13,419 | 1 | 3,14,31,36,38,41 | `11_extraction_scheduling_logic.json` |
| 12 | execution_agent | extraction | OK | 98.9 | 30,498 | 11 | 0-41,43-45,53-55,68-69,71,73 | `12_extraction_execution_model.json` |
| 13 | advanced_agent | extraction | OK | 3.2 | 4,623 | 1 | 0-3 | `13_extraction_advanced_entities.json` |
| 14 | biomedical_concept_agent | extraction | OK | 162.9 | 27,498 | 2 |  | `14_extraction_biomedical_concepts.json` |
| 15 | postprocessing_agent | quality | OK | 0.0 | 0 | 0 |  | `15_quality_postprocessing.json` |
| 16 | reconciliation_agent | quality | OK | 0.5 | 0 | 0 |  | `16_quality_reconciliation.json` |
| 17 | validation_agent | quality | OK | 0.0 | 0 | 0 |  | `17_quality_validation.json` |
| 18 | enrichment_agent | quality | OK | 7.4 | 0 | 59 |  | `18_quality_enrichment.json` |
| 19 | usdm-generator | support | OK | 4.2 | 0 | 0 |  | `19_support_usdm_generator.json` |
| 20 | provenance | support | OK | 0.0 | 0 | 0 |  | `20_support_provenance.json` |
| 00 | pdf-parser | support | OK | 2.1 | 0 | 0 | | |

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
- `UAT-IM-EK01.pdf`
- `UAT-IM-EK01_provenance.json`
- `UAT-IM-EK01_usdm.json`
- `conformance_report.json`
- `id_mapping.json`
- `soa_page_009.png`
- `soa_page_010.png`
- `soa_page_011.png`
- `soa_page_012.png`
- `soa_page_013.png`
- `soa_page_014.png`
- `soa_page_015.png`
- `soa_page_016.png`
- `soa_page_017.png`
- `soa_page_018.png`
- `soa_page_019.png`
- `soa_page_020.png`
- `soa_page_021.png`
- `soa_page_022.png`
- `soa_page_023.png`
- `soa_page_026.png`
- `soa_page_027.png`
- `soa_page_028.png`
- `soa_page_043.png`
- `soa_page_044.png`
- `usdm_validation.json`
