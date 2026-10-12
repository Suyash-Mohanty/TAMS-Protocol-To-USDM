# Pipeline Result: UAT-IM-EK01

**Status:** FAILED
**PDF:** `UAT-IM-EK01.pdf`
**Model:** cortex/reforge-claude-opus-5
**Started:** 2026-10-09 14:05:59
**Finished:** 2026-10-09 14:19:30
**Duration:** 811.2s
**Entities:** 1010
**Waves:** 4

## Statistics

| Metric | Value |
|--------|-------|
| Total Agents | 21 |
| Succeeded | 20 |
| Failed | 1 |
| Total Entities | 1010 |
| Total Tokens | 259,640 |
| Total API Calls | 86 |
| Total Duration | 811.2s |

## Execution Flow

```
Wave 0  (502.3s)
  [FAIL] docstructure_agent (0.0s)  ->  05_extraction_document_structure.json
  [OK] metadata_agent (456.9s)  ->  01_extraction_metadata.json
  [OK] narrative_agent (500.7s)  ->  04_extraction_narrative.json
  [OK] pdf-parser (10.7s)
  [OK] provenance (0.0s)  ->  20_support_provenance.json
  [OK] soa_vision_agent (502.3s)  ->  02_extraction_soa_vision.json
  [OK] usdm-generator (11.8s)  ->  19_support_usdm_generator.json
  |
Wave 1  (112.9s)
  [OK] advanced_agent (4.4s)  ->  13_extraction_advanced_entities.json
  [OK] eligibility_agent (26.8s)  ->  06_extraction_eligibility.json
  [OK] objectives_agent (38.5s)  ->  07_extraction_objectives.json
  [OK] procedures_agent (80.7s)  ->  09_extraction_procedures_devices.json
  [OK] soa_text_agent (112.9s)  ->  03_extraction_soa_text.json
  [OK] studydesign_agent (12.1s)  ->  08_extraction_study_design.json
  |
Wave 2  (135.3s)
  [OK] biomedical_concept_agent (135.3s)  ->  14_extraction_biomedical_concepts.json
  [OK] execution_agent (104.5s)  ->  12_extraction_execution_model.json
  [OK] interventions_agent (18.3s)  ->  10_extraction_interventions.json
  [OK] scheduling_agent (52.2s)  ->  11_extraction_scheduling_logic.json
  |
Wave 3  (10.3s)
  [OK] enrichment_agent (10.3s)  ->  18_quality_enrichment.json
  [OK] postprocessing_agent (0.2s)  ->  15_quality_postprocessing.json
  [OK] reconciliation_agent (1.5s)  ->  16_quality_reconciliation.json
  [OK] validation_agent (0.0s)  ->  17_quality_validation.json
  |
Output
  [OK] UAT-IM-EK01_usdm.json
  [OK] UAT-IM-EK01_provenance.json
```

## Agent Results

| Step | Agent | Category | Status | Time (s) | Tokens | API Calls | Pages | Output File |
|------|-------|----------|--------|----------|--------|-----------|-------|-------------|
| 01 | metadata_agent | extraction | OK | 456.9 | 4,878 | 1 | 0-2 | `01_extraction_metadata.json` |
| 02 | soa_vision_agent | extraction | OK | 502.3 | 23,212 | 1 | 8-17 | `02_extraction_soa_vision.json` |
| 03 | soa_text_agent | extraction | OK | 112.9 | 32,741 | 1 | 8-17 | `03_extraction_soa_text.json` |
| 04 | narrative_agent | extraction | OK | 500.7 | 27,826 | 2 | 2-9,16,19,21,26,71-73 | `04_extraction_narrative.json` |
| 05 | docstructure_agent | extraction | FAIL | 0.0 | 0 | 0 | 0-5,9,11-12,16-17,19-20,31,42,44,49 | `05_extraction_document_structure.json` |
| 06 | eligibility_agent | extraction | OK | 26.8 | 9,087 | 1 | 8-10,29-31 | `06_extraction_eligibility.json` |
| 07 | objectives_agent | extraction | OK | 38.5 | 28,204 | 2 | 5-16,25-28,44-46 | `07_extraction_objectives.json` |
| 08 | studydesign_agent | extraction | OK | 12.1 | 16,364 | 1 | 0-18,27-29 | `08_extraction_study_design.json` |
| 09 | procedures_agent | extraction | OK | 80.7 | 21,259 | 1 | 3-5,9-10,12,14,16-17,19,21,24,31,34-35 | `09_extraction_procedures_devices.json` |
| 10 | interventions_agent | extraction | OK | 18.3 | 24,604 | 1 | 1-10,13-25,27-29,33-43 | `10_extraction_interventions.json` |
| 11 | scheduling_agent | extraction | OK | 52.2 | 13,151 | 1 | 3,14,31,36,38,41 | `11_extraction_scheduling_logic.json` |
| 12 | execution_agent | extraction | OK | 104.5 | 30,429 | 11 | 0-41,43-45,53-55,68-69,71,73 | `12_extraction_execution_model.json` |
| 13 | advanced_agent | extraction | OK | 4.4 | 4,623 | 1 | 0-3 | `13_extraction_advanced_entities.json` |
| 14 | biomedical_concept_agent | extraction | OK | 135.3 | 23,262 | 2 |  | `14_extraction_biomedical_concepts.json` |
| 15 | postprocessing_agent | quality | OK | 0.2 | 0 | 0 |  | `15_quality_postprocessing.json` |
| 16 | reconciliation_agent | quality | OK | 1.5 | 0 | 0 |  | `16_quality_reconciliation.json` |
| 17 | validation_agent | quality | OK | 0.0 | 0 | 0 |  | `17_quality_validation.json` |
| 18 | enrichment_agent | quality | OK | 10.3 | 0 | 60 |  | `18_quality_enrichment.json` |
| 19 | usdm-generator | support | OK | 11.8 | 0 | 0 |  | `19_support_usdm_generator.json` |
| 20 | provenance | support | OK | 0.0 | 0 | 0 |  | `20_support_provenance.json` |
| 00 | pdf-parser | support | OK | 10.7 | 0 | 0 | | |

## Failed Agents

- **docstructure_agent**: Timed out after 420s

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
