# Pipeline Result: Alexion_NCT04573309_Wilsons

**Status:** FAILED
**PDF:** `Alexion_NCT04573309_Wilsons.pdf`
**Model:** gemini-2.5-pro
**Started:** 2026-10-05 18:06:52
**Finished:** 2026-10-05 18:08:31
**Duration:** 98.3s
**Entities:** 172
**Waves:** 4

## Statistics

| Metric | Value |
|--------|-------|
| Total Agents | 21 |
| Succeeded | 9 |
| Failed | 12 |
| Total Entities | 172 |
| Total Tokens | 0 |
| Total API Calls | 0 |
| Total Duration | 98.3s |

## Execution Flow

```
Wave 0  (1.8s)
  [FAIL] docstructure_agent (0.0s)  ->  05_extraction_document_structure.json
  [FAIL] metadata_agent (0.0s)  ->  01_extraction_metadata.json
  [OK] narrative_agent (0.1s)  ->  04_extraction_narrative.json
  [OK] pdf-parser (1.8s)
  [OK] provenance (0.0s)  ->  20_support_provenance.json
  [FAIL] soa_vision_agent (0.0s)  ->  02_extraction_soa_vision.json
  [OK] usdm-generator (0.3s)  ->  19_support_usdm_generator.json
  |
Wave 1  (0.0s)
  [FAIL] advanced_agent (0.0s)  ->  13_extraction_advanced_entities.json
  [FAIL] eligibility_agent (0.0s)  ->  06_extraction_eligibility.json
  [FAIL] objectives_agent (0.0s)  ->  07_extraction_objectives.json
  [FAIL] procedures_agent (0.0s)  ->  09_extraction_procedures_devices.json
  [FAIL] soa_text_agent (0.0s)  ->  03_extraction_soa_text.json
  [FAIL] studydesign_agent (0.0s)  ->  08_extraction_study_design.json
  |
Wave 2  (7.7s)
  [FAIL] biomedical_concept_agent (0.0s)  ->  14_extraction_biomedical_concepts.json
  [OK] execution_agent (7.7s)  ->  12_extraction_execution_model.json
  [FAIL] interventions_agent (0.0s)  ->  10_extraction_interventions.json
  [FAIL] scheduling_agent (0.0s)  ->  11_extraction_scheduling_logic.json
  |
Wave 3  (0.0s)
  [OK] enrichment_agent (0.0s)  ->  18_quality_enrichment.json
  [OK] postprocessing_agent (0.0s)  ->  15_quality_postprocessing.json
  [OK] reconciliation_agent (0.0s)  ->  16_quality_reconciliation.json
  [OK] validation_agent (0.0s)  ->  17_quality_validation.json
  |
Output
  [OK] Alexion_NCT04573309_Wilsons_usdm.json
  [OK] Alexion_NCT04573309_Wilsons_provenance.json
```

## Agent Results

| Step | Agent | Category | Status | Time (s) | Tokens | API Calls | Pages | Output File |
|------|-------|----------|--------|----------|--------|-----------|-------|-------------|
| 01 | metadata_agent | extraction | FAIL | 0.0 | 0 | 0 |  | `01_extraction_metadata.json` |
| 02 | soa_vision_agent | extraction | FAIL | 0.0 | 0 | 0 |  | `02_extraction_soa_vision.json` |
| 03 | soa_text_agent | extraction | FAIL | 0.0 | 0 | 0 |  | `03_extraction_soa_text.json` |
| 04 | narrative_agent | extraction | OK | 0.1 | 0 | 0 |  | `04_extraction_narrative.json` |
| 05 | docstructure_agent | extraction | FAIL | 0.0 | 0 | 0 |  | `05_extraction_document_structure.json` |
| 06 | eligibility_agent | extraction | FAIL | 0.0 | 0 | 0 |  | `06_extraction_eligibility.json` |
| 07 | objectives_agent | extraction | FAIL | 0.0 | 0 | 0 |  | `07_extraction_objectives.json` |
| 08 | studydesign_agent | extraction | FAIL | 0.0 | 0 | 0 |  | `08_extraction_study_design.json` |
| 09 | procedures_agent | extraction | FAIL | 0.0 | 0 | 0 |  | `09_extraction_procedures_devices.json` |
| 10 | interventions_agent | extraction | FAIL | 0.0 | 0 | 0 |  | `10_extraction_interventions.json` |
| 11 | scheduling_agent | extraction | FAIL | 0.0 | 0 | 0 |  | `11_extraction_scheduling_logic.json` |
| 12 | execution_agent | extraction | OK | 7.7 | 0 | 0 | 0-41,50-53,68 | `12_extraction_execution_model.json` |
| 13 | advanced_agent | extraction | FAIL | 0.0 | 0 | 0 |  | `13_extraction_advanced_entities.json` |
| 14 | biomedical_concept_agent | extraction | FAIL | 0.0 | 0 | 0 |  | `14_extraction_biomedical_concepts.json` |
| 15 | postprocessing_agent | quality | OK | 0.0 | 0 | 0 |  | `15_quality_postprocessing.json` |
| 16 | reconciliation_agent | quality | OK | 0.0 | 0 | 0 |  | `16_quality_reconciliation.json` |
| 17 | validation_agent | quality | OK | 0.0 | 0 | 0 |  | `17_quality_validation.json` |
| 18 | enrichment_agent | quality | OK | 0.0 | 0 | 0 |  | `18_quality_enrichment.json` |
| 19 | usdm-generator | support | OK | 0.3 | 0 | 0 |  | `19_support_usdm_generator.json` |
| 20 | provenance | support | OK | 0.0 | 0 | 0 |  | `20_support_provenance.json` |
| 00 | pdf-parser | support | OK | 1.8 | 0 | 0 | | |

## Failed Agents

- **metadata_agent**: Failed after 4 attempts: Extraction returned no data
- **docstructure_agent**: Failed after 4 attempts: Extraction returned no data
- **soa_vision_agent**: Failed after 4 attempts: Extraction returned no data
- **studydesign_agent**: Failed after 4 attempts: Extraction returned no data
- **objectives_agent**: Failed after 4 attempts: Extraction returned no data
- **eligibility_agent**: Failed after 4 attempts: Extraction returned no data
- **soa_text_agent**: Failed after 4 attempts: Extraction returned no data
- **advanced_agent**: Failed after 4 attempts: Extraction returned no data
- **procedures_agent**: Failed after 4 attempts: Extraction returned no data
- **biomedical_concept_agent**: Failed after 4 attempts: Extraction returned no data
- **interventions_agent**: Failed after 4 attempts: Extraction returned no data
- **scheduling_agent**: Failed after 4 attempts: Extraction returned no data

## Output Files

- `04_extraction_narrative.json`
- `12_extraction_execution_model.json`
- `15_quality_postprocessing.json`
- `16_quality_reconciliation.json`
- `17_quality_validation.json`
- `18_quality_enrichment.json`
- `19_support_usdm_generator.json`
- `20_support_provenance.json`
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
