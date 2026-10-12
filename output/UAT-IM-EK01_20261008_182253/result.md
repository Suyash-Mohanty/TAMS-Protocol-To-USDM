# Pipeline Result: UAT-IM-EK01

**Status:** SUCCESS
**PDF:** `UAT-IM-EK01.pdf`
**Model:** cortex/reforge-claude-opus-5
**Started:** 2026-10-08 18:22:53
**Finished:** 2026-10-08 18:28:31
**Duration:** 338.0s
**Entities:** 982
**Waves:** 4

## Statistics

| Metric | Value |
|--------|-------|
| Total Agents | 21 |
| Succeeded | 21 |
| Failed | 0 |
| Total Entities | 982 |
| Total Tokens | 278,397 |
| Total API Calls | 85 |
| Total Duration | 338.0s |

## Execution Flow

```
Wave 0  (87.9s)
  [OK] docstructure_agent (87.9s)  ->  05_extraction_document_structure.json
  [OK] metadata_agent (16.9s)  ->  01_extraction_metadata.json
  [OK] narrative_agent (72.8s)  ->  04_extraction_narrative.json
  [OK] pdf-parser (1.2s)
  [OK] provenance (0.0s)  ->  20_support_provenance.json
  [OK] soa_vision_agent (57.9s)  ->  02_extraction_soa_vision.json
  [OK] usdm-generator (1.5s)  ->  19_support_usdm_generator.json
  |
Wave 1  (111.2s)
  [OK] advanced_agent (4.7s)  ->  13_extraction_advanced_entities.json
  [OK] eligibility_agent (26.2s)  ->  06_extraction_eligibility.json
  [OK] objectives_agent (39.0s)  ->  07_extraction_objectives.json
  [OK] procedures_agent (72.2s)  ->  09_extraction_procedures_devices.json
  [OK] soa_text_agent (111.2s)  ->  03_extraction_soa_text.json
  [OK] studydesign_agent (15.6s)  ->  08_extraction_study_design.json
  |
Wave 2  (134.6s)
  [OK] biomedical_concept_agent (134.6s)  ->  14_extraction_biomedical_concepts.json
  [OK] execution_agent (105.7s)  ->  12_extraction_execution_model.json
  [OK] interventions_agent (14.2s)  ->  10_extraction_interventions.json
  [OK] scheduling_agent (49.2s)  ->  11_extraction_scheduling_logic.json
  |
Wave 3  (3.7s)
  [OK] enrichment_agent (3.7s)  ->  18_quality_enrichment.json
  [OK] postprocessing_agent (0.0s)  ->  15_quality_postprocessing.json
  [OK] reconciliation_agent (0.3s)  ->  16_quality_reconciliation.json
  [OK] validation_agent (0.0s)  ->  17_quality_validation.json
  |
Output
  [OK] UAT-IM-EK01_usdm.json
  [OK] UAT-IM-EK01_provenance.json
```

## Agent Results

| Step | Agent | Category | Status | Time (s) | Tokens | API Calls | Pages | Output File |
|------|-------|----------|--------|----------|--------|-----------|-------|-------------|
| 01 | metadata_agent | extraction | OK | 16.9 | 4,878 | 1 | 0-2 | `01_extraction_metadata.json` |
| 02 | soa_vision_agent | extraction | OK | 57.9 | 22,809 | 1 | 8-17 | `02_extraction_soa_vision.json` |
| 03 | soa_text_agent | extraction | OK | 111.2 | 32,806 | 1 | 8-17 | `03_extraction_soa_text.json` |
| 04 | narrative_agent | extraction | OK | 72.8 | 27,829 | 2 | 2-9,16,19,21,26,71-73 | `04_extraction_narrative.json` |
| 05 | docstructure_agent | extraction | OK | 87.9 | 20,054 | 1 | 0-5,9,11-12,16-17,19-20,31,42,44,49 | `05_extraction_document_structure.json` |
| 06 | eligibility_agent | extraction | OK | 26.2 | 9,102 | 1 | 8-10,29-31 | `06_extraction_eligibility.json` |
| 07 | objectives_agent | extraction | OK | 39.0 | 28,106 | 2 | 5-16,25-28,44-46 | `07_extraction_objectives.json` |
| 08 | studydesign_agent | extraction | OK | 15.6 | 16,419 | 1 | 0-18,27-29 | `08_extraction_study_design.json` |
| 09 | procedures_agent | extraction | OK | 72.2 | 20,932 | 1 | 3-5,9-10,12,14,16-17,19,21,24,31,34-35 | `09_extraction_procedures_devices.json` |
| 10 | interventions_agent | extraction | OK | 14.2 | 24,554 | 1 | 1-10,13-25,27-29,33-43 | `10_extraction_interventions.json` |
| 11 | scheduling_agent | extraction | OK | 49.2 | 12,870 | 1 | 3,14,31,36,38,41 | `11_extraction_scheduling_logic.json` |
| 12 | execution_agent | extraction | OK | 105.7 | 30,420 | 11 | 0-41,43-45,53-55,68-69,71,73 | `12_extraction_execution_model.json` |
| 13 | advanced_agent | extraction | OK | 4.7 | 4,623 | 1 | 0-3 | `13_extraction_advanced_entities.json` |
| 14 | biomedical_concept_agent | extraction | OK | 134.6 | 22,995 | 2 |  | `14_extraction_biomedical_concepts.json` |
| 15 | postprocessing_agent | quality | OK | 0.0 | 0 | 0 |  | `15_quality_postprocessing.json` |
| 16 | reconciliation_agent | quality | OK | 0.3 | 0 | 0 |  | `16_quality_reconciliation.json` |
| 17 | validation_agent | quality | OK | 0.0 | 0 | 0 |  | `17_quality_validation.json` |
| 18 | enrichment_agent | quality | OK | 3.7 | 0 | 58 |  | `18_quality_enrichment.json` |
| 19 | usdm-generator | support | OK | 1.5 | 0 | 0 |  | `19_support_usdm_generator.json` |
| 20 | provenance | support | OK | 0.0 | 0 | 0 |  | `20_support_provenance.json` |
| 00 | pdf-parser | support | OK | 1.2 | 0 | 0 | | |

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
- `usdm_validation.json`
