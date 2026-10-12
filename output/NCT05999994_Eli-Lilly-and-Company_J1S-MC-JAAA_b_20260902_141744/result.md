# Pipeline Result: NCT05999994_Eli-Lilly-and-Company_J1S-MC-JAAA_b

**Status:** SUCCESS
**PDF:** `NCT05999994_Eli-Lilly-and-Company_J1S-MC-JAAA_b.pdf`
**Model:** cortex
**Started:** 2026-09-02 14:17:44
**Finished:** 2026-09-02 14:21:05
**Duration:** 200.4s
**Entities:** 417
**Waves:** 4

## Statistics

| Metric | Value |
|--------|-------|
| Total Agents | 21 |
| Succeeded | 21 |
| Failed | 0 |
| Total Entities | 417 |
| Total Tokens | 173,278 |
| Total API Calls | 69 |
| Total Duration | 200.4s |

## Execution Flow

```
Wave 0  (61.6s)
  [OK] docstructure_agent (61.6s)  ->  05_extraction_document_structure.json
  [OK] metadata_agent (11.8s)  ->  01_extraction_metadata.json
  [OK] narrative_agent (28.9s)  ->  04_extraction_narrative.json
  [OK] pdf-parser (1.2s)
  [OK] provenance (0.0s)  ->  20_support_provenance.json
  [OK] soa_vision_agent (20.6s)  ->  02_extraction_soa_vision.json
  [OK] usdm-generator (0.6s)  ->  19_support_usdm_generator.json
  |
Wave 1  (33.1s)
  [OK] advanced_agent (6.0s)  ->  13_extraction_advanced_entities.json
  [OK] eligibility_agent (13.4s)  ->  06_extraction_eligibility.json
  [OK] objectives_agent (17.4s)  ->  07_extraction_objectives.json
  [OK] procedures_agent (33.1s)  ->  09_extraction_procedures_devices.json
  [OK] soa_text_agent (16.8s)  ->  03_extraction_soa_text.json
  [OK] studydesign_agent (11.8s)  ->  08_extraction_study_design.json
  |
Wave 2  (87.9s)
  [OK] biomedical_concept_agent (43.7s)  ->  14_extraction_biomedical_concepts.json
  [OK] execution_agent (87.9s)  ->  12_extraction_execution_model.json
  [OK] interventions_agent (21.9s)  ->  10_extraction_interventions.json
  [OK] scheduling_agent (56.8s)  ->  11_extraction_scheduling_logic.json
  |
Wave 3  (17.3s)
  [OK] enrichment_agent (17.3s)  ->  18_quality_enrichment.json
  [OK] postprocessing_agent (0.1s)  ->  15_quality_postprocessing.json
  [OK] reconciliation_agent (0.1s)  ->  16_quality_reconciliation.json
  [OK] validation_agent (0.0s)  ->  17_quality_validation.json
  |
Output
  [OK] NCT05999994_Eli-Lilly-and-Company_J1S-MC-JAAA_b_usdm.json
  [OK] NCT05999994_Eli-Lilly-and-Company_J1S-MC-JAAA_b_provenance.json
```

## Agent Results

| Step | Agent | Category | Status | Time (s) | Tokens | API Calls | Pages | Output File |
|------|-------|----------|--------|----------|--------|-----------|-------|-------------|
| 01 | metadata_agent | extraction | OK | 11.8 | 3,575 | 1 | 0-2 | `01_extraction_metadata.json` |
| 02 | soa_vision_agent | extraction | OK | 20.6 | 16,474 | 1 | 8-10,13-15,22-25 | `02_extraction_soa_vision.json` |
| 03 | soa_text_agent | extraction | OK | 16.8 | 9,529 | 1 | 8-10,13-15,22-25 | `03_extraction_soa_text.json` |
| 04 | narrative_agent | extraction | OK | 28.9 | 15,137 | 2 | 2,7-9,14,17,21,23-28 | `04_extraction_narrative.json` |
| 05 | docstructure_agent | extraction | OK | 61.6 | 12,872 | 1 | 0-4,7,13-15,17,22,31-32,39,45,50 | `05_extraction_document_structure.json` |
| 06 | eligibility_agent | extraction | OK | 13.4 | 4,653 | 1 | 14-16 | `06_extraction_eligibility.json` |
| 07 | objectives_agent | extraction | OK | 17.4 | 12,878 | 2 | 0-14 | `07_extraction_objectives.json` |
| 08 | studydesign_agent | extraction | OK | 11.8 | 12,717 | 1 | 1-3,7-15,18-23,27-29 | `08_extraction_study_design.json` |
| 09 | procedures_agent | extraction | OK | 33.1 | 11,144 | 1 | 3,16,19,23,26-28,30-31,33,41,45 | `09_extraction_procedures_devices.json` |
| 10 | interventions_agent | extraction | OK | 21.9 | 22,994 | 1 | 2-4,8-39,41-46 | `10_extraction_interventions.json` |
| 11 | scheduling_agent | extraction | OK | 56.8 | 13,272 | 1 | 2-3,9,18,20,22,24-27,30,37,48 | `11_extraction_scheduling_logic.json` |
| 12 | execution_agent | extraction | OK | 87.9 | 24,405 | 11 | 0-39,42,49 | `12_extraction_execution_model.json` |
| 13 | advanced_agent | extraction | OK | 6.0 | 6,073 | 1 | 0-3,7,17,21-22,27,29 | `13_extraction_advanced_entities.json` |
| 14 | biomedical_concept_agent | extraction | OK | 43.7 | 7,555 | 1 |  | `14_extraction_biomedical_concepts.json` |
| 15 | postprocessing_agent | quality | OK | 0.1 | 0 | 0 |  | `15_quality_postprocessing.json` |
| 16 | reconciliation_agent | quality | OK | 0.1 | 0 | 0 |  | `16_quality_reconciliation.json` |
| 17 | validation_agent | quality | OK | 0.0 | 0 | 0 |  | `17_quality_validation.json` |
| 18 | enrichment_agent | quality | OK | 17.3 | 0 | 43 |  | `18_quality_enrichment.json` |
| 19 | usdm-generator | support | OK | 0.6 | 0 | 0 |  | `19_support_usdm_generator.json` |
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
- `NCT05999994_Eli-Lilly-and-Company_J1S-MC-JAAA_b.pdf`
- `NCT05999994_Eli-Lilly-and-Company_J1S-MC-JAAA_b_provenance.json`
- `NCT05999994_Eli-Lilly-and-Company_J1S-MC-JAAA_b_usdm.json`
- `conformance_report.json`
- `id_mapping.json`
- `soa_page_009.png`
- `soa_page_010.png`
- `soa_page_011.png`
- `soa_page_014.png`
- `soa_page_015.png`
- `soa_page_016.png`
- `soa_page_023.png`
- `soa_page_024.png`
- `soa_page_025.png`
- `soa_page_026.png`
