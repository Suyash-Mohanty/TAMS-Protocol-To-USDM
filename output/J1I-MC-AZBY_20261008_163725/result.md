# Pipeline Result: J1I-MC-AZBY

**Status:** SUCCESS
**PDF:** `J1I-MC-AZBY.pdf`
**Model:** cortex/reforge-claude-opus-5
**Started:** 2026-10-08 16:37:25
**Finished:** 2026-10-08 16:44:09
**Duration:** 404.3s
**Entities:** 907
**Waves:** 4

## Statistics

| Metric | Value |
|--------|-------|
| Total Agents | 21 |
| Succeeded | 21 |
| Failed | 0 |
| Total Entities | 907 |
| Total Tokens | 298,627 |
| Total API Calls | 64 |
| Total Duration | 404.3s |

## Execution Flow

```
Wave 0  (89.7s)
  [OK] docstructure_agent (89.7s)  ->  05_extraction_document_structure.json
  [OK] metadata_agent (14.0s)  ->  01_extraction_metadata.json
  [OK] narrative_agent (71.3s)  ->  04_extraction_narrative.json
  [OK] pdf-parser (4.1s)
  [OK] provenance (0.0s)  ->  20_support_provenance.json
  [OK] soa_vision_agent (76.2s)  ->  02_extraction_soa_vision.json
  [OK] usdm-generator (0.5s)  ->  19_support_usdm_generator.json
  |
Wave 1  (171.0s)
  [OK] advanced_agent (9.3s)  ->  13_extraction_advanced_entities.json
  [OK] eligibility_agent (85.5s)  ->  06_extraction_eligibility.json
  [OK] objectives_agent (171.0s)  ->  07_extraction_objectives.json
  [OK] procedures_agent (48.2s)  ->  09_extraction_procedures_devices.json
  [OK] soa_text_agent (26.1s)  ->  03_extraction_soa_text.json
  [OK] studydesign_agent (18.9s)  ->  08_extraction_study_design.json
  |
Wave 2  (140.2s)
  [OK] biomedical_concept_agent (21.1s)  ->  14_extraction_biomedical_concepts.json
  [OK] execution_agent (140.2s)  ->  12_extraction_execution_model.json
  [OK] interventions_agent (22.3s)  ->  10_extraction_interventions.json
  [OK] scheduling_agent (115.8s)  ->  11_extraction_scheduling_logic.json
  |
Wave 3  (2.6s)
  [OK] enrichment_agent (2.6s)  ->  18_quality_enrichment.json
  [OK] postprocessing_agent (0.1s)  ->  15_quality_postprocessing.json
  [OK] reconciliation_agent (0.3s)  ->  16_quality_reconciliation.json
  [OK] validation_agent (0.0s)  ->  17_quality_validation.json
  |
Output
  [OK] J1I-MC-AZBY_usdm.json
  [OK] J1I-MC-AZBY_provenance.json
```

## Agent Results

| Step | Agent | Category | Status | Time (s) | Tokens | API Calls | Pages | Output File |
|------|-------|----------|--------|----------|--------|-----------|-------|-------------|
| 01 | metadata_agent | extraction | OK | 14.0 | 3,727 | 1 | 0-2 | `01_extraction_metadata.json` |
| 02 | soa_vision_agent | extraction | OK | 76.2 | 24,090 | 1 | 12-20,24 | `02_extraction_soa_vision.json` |
| 03 | soa_text_agent | extraction | OK | 26.1 | 15,702 | 1 | 12-20,24 | `03_extraction_soa_text.json` |
| 04 | narrative_agent | extraction | OK | 71.3 | 22,712 | 2 | 3,8-12,14,18-19,138-142 | `04_extraction_narrative.json` |
| 05 | docstructure_agent | extraction | OK | 89.7 | 17,550 | 1 | 0-4,8,10-11,19,22-24,27,33 | `05_extraction_document_structure.json` |
| 06 | eligibility_agent | extraction | OK | 85.5 | 17,364 | 1 | 3-5,45-50 | `06_extraction_eligibility.json` |
| 07 | objectives_agent | extraction | OK | 171.0 | 51,948 | 2 | 2-4,11-16,39-45 | `07_extraction_objectives.json` |
| 08 | studydesign_agent | extraction | OK | 18.9 | 16,817 | 1 | 0-1,7-9,11-13,15-17,19-29 | `08_extraction_study_design.json` |
| 09 | procedures_agent | extraction | OK | 48.2 | 14,817 | 1 | 9,11,17,19,21,24,29-30,33,36,39,46,55-56 | `09_extraction_procedures_devices.json` |
| 10 | interventions_agent | extraction | OK | 22.3 | 31,691 | 1 | 0-1,3-22,25-27,29-32,34-47 | `10_extraction_interventions.json` |
| 11 | scheduling_agent | extraction | OK | 115.8 | 33,392 | 1 | 4-5,9,15-16,19,21-34 | `11_extraction_scheduling_logic.json` |
| 12 | execution_agent | extraction | OK | 140.2 | 39,263 | 10 | 0-44,46-47,51,57-58,60,63,65,70,74-75,85,88,92,95,97,101,112-113,122,136-137,140,142,145 | `12_extraction_execution_model.json` |
| 13 | advanced_agent | extraction | OK | 9.3 | 5,359 | 1 | 0-3,8 | `13_extraction_advanced_entities.json` |
| 14 | biomedical_concept_agent | extraction | OK | 21.1 | 4,195 | 1 |  | `14_extraction_biomedical_concepts.json` |
| 15 | postprocessing_agent | quality | OK | 0.1 | 0 | 0 |  | `15_quality_postprocessing.json` |
| 16 | reconciliation_agent | quality | OK | 0.3 | 0 | 0 |  | `16_quality_reconciliation.json` |
| 17 | validation_agent | quality | OK | 0.0 | 0 | 0 |  | `17_quality_validation.json` |
| 18 | enrichment_agent | quality | OK | 2.6 | 0 | 39 |  | `18_quality_enrichment.json` |
| 19 | usdm-generator | support | OK | 0.5 | 0 | 0 |  | `19_support_usdm_generator.json` |
| 20 | provenance | support | OK | 0.0 | 0 | 0 |  | `20_support_provenance.json` |
| 00 | pdf-parser | support | OK | 4.1 | 0 | 0 | | |

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
- `J1I-MC-AZBY.pdf`
- `J1I-MC-AZBY_provenance.json`
- `J1I-MC-AZBY_usdm.json`
- `conformance_report.json`
- `id_mapping.json`
- `soa_page_013.png`
- `soa_page_014.png`
- `soa_page_015.png`
- `soa_page_016.png`
- `soa_page_017.png`
- `soa_page_018.png`
- `soa_page_019.png`
- `soa_page_020.png`
- `soa_page_021.png`
- `soa_page_025.png`
- `usdm_validation.json`
