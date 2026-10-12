"""
LLM Prompts for BiomedicalConcept Extraction.

The extractor provides a list of SoA activity names and asks the LLM to:
1. Group the activities into clinical categories (Vital Signs, Labs, ECG, PK, etc.)
2. For each activity, produce a BiomedicalConcept with NCI codes and key properties

Well-known NCI Thesaurus codes included in the prompt to guide the LLM.
"""

BIOMEDICAL_CONCEPT_EXTRACTION_PROMPT = """You are an expert in clinical data standards (CDISC CDASH, SDTM) and biomedical ontologies (NCI Thesaurus, SNOMED CT).

You will receive a list of clinical assessment names from a clinical trial Schedule of Activities (SoA).
For each assessment, generate a structured BiomedicalConcept following CDISC USDM v4.0 schema.

## Task

1. **Categorise** all activities into standard clinical domains:
   - Vital Signs, Laboratory Tests, Pharmacokinetics, ECG/Cardiac, Physical Examination,
     Questionnaires/PRO, Imaging, Biomarker, Pharmacogenomics, Safety Monitoring, Procedures, Other

2. **For each activity**, produce a BiomedicalConcept with:
   - `id`: unique string (bc_1, bc_2, …)
   - `name`: short standard name (e.g., "Systolic Blood Pressure")
   - `label`: full display label
   - `synonyms`: common alternative names
   - `nciCode`: NCI Thesaurus code if known (else null)
   - `nciDecode`: NCI decode text if known
   - `categoryName`: one of the standard domain names above
   - `properties`: 1–4 key data elements with:
     - `name`: CDASH/SDTM variable name (e.g., SYSBP)
     - `label`: human label
     - `datatype`: string | integer | float | boolean | datetime
     - `isRequired`: true | false

## Well-known NCI Codes (use when applicable)

| Assessment | NCI Code | Decode |
|---|---|---|
| Systolic Blood Pressure | C25298 | Systolic Blood Pressure |
| Diastolic Blood Pressure | C25299 | Diastolic Blood Pressure |
| Heart Rate | C49677 | Heart Rate |
| Respiratory Rate | C25590 | Respiratory Rate |
| Body Temperature | C25208 | Body Temperature |
| Body Weight | C81328 | Body Weight |
| Height | C25347 | Height |
| BMI | C16358 | Body Mass Index |
| Oxygen Saturation (SpO2) | C70017 | Oxygen Saturation |
| ECG | C38054 | Electrocardiogram |
| QTcF Interval | C82530 | QTcF Interval |
| Haemoglobin | C64848 | Hemoglobin |
| White Blood Cell Count | C51948 | White Blood Cell Count |
| Platelet Count | C51951 | Platelet Count |
| Serum Creatinine | C25386 | Serum Creatinine |
| ALT | C16235 | Alanine Aminotransferase |
| AST | C16237 | Aspartate Aminotransferase |
| Bilirubin | C63591 | Bilirubin |
| eGFR | C99513 | Estimated Glomerular Filtration Rate |
| Urine Albumin-to-Creatinine Ratio | C96658 | Urine Albumin-Creatinine Ratio |
| HbA1c | C64489 | Hemoglobin A1c |
| Fasting Glucose | C25735 | Fasting Blood Glucose |
| Adverse Event | C41331 | Adverse Event |
| Concomitant Medications | C38101 | Concomitant Medications |
| Physical Examination | C62244 | Physical Examination |
| Informed Consent | C16735 | Informed Consent |

## Output Format

### Citation requirement — read before producing output

The activity names you were given come from the Schedule of Activities, not raw
protocol text with page numbers, so citations here work slightly differently than
in other extraction modules: for the fields you derive from your own clinical
knowledge of the activity name (`name`, `label`, `synonyms`), wrap the value as:
```json
"fieldName": {{"value": <the actual value>, "page": null, "quote": "<the input activity line this was derived from>"}}
```
- `page` is always `null` here — these fields aren't tied to a specific protocol
  page, only to the activity line you were given.
- `quote` is the exact `activity` line (copied from the numbered list below) that
  you based this value on — not a paraphrase.
- Structural/classification/lookup fields (`id`, `activity`, `categoryName`,
  `nciCode`, `nciDecode`, and every field inside `properties`) stay bare, exactly
  as before — do NOT wrap these. In particular, do NOT invent a page or quote for
  `nciCode`/`nciDecode` — those come from the lookup table above, not from reading
  the protocol.

```json
{{
  "categories": [
    {{
      "id": "bcc_1",
      "name": "Vital Signs",
      "label": "Vital Signs Measurements",
      "bcIds": ["bc_1", "bc_2"]
    }}
  ],
  "biomedicalConcepts": [
    {{
      "id": "bc_1",
      "activity": "Vital Signs (Supine Blood Pressure, Pulse Rate)",
      "name": {{"value": "Systolic Blood Pressure", "page": null, "quote": "Vital Signs (Supine Blood Pressure, Pulse Rate)"}},
      "label": {{"value": "Systolic Blood Pressure Measurement", "page": null, "quote": "Vital Signs (Supine Blood Pressure, Pulse Rate)"}},
      "synonyms": {{"value": ["SBP", "Systolic BP"], "page": null, "quote": "Vital Signs (Supine Blood Pressure, Pulse Rate)"}},
      "nciCode": "C25298",
      "nciDecode": "Systolic Blood Pressure",
      "categoryName": "Vital Signs",
      "properties": [
        {{
          "name": "SYSBP",
          "label": "Systolic Blood Pressure Result",
          "datatype": "float",
          "isRequired": true
        }},
        {{
          "name": "VSORRESU",
          "label": "Original Units",
          "datatype": "string",
          "isRequired": false
        }}
      ]
    }}
  ]
}}
```

## Rules

1. Create exactly ONE BiomedicalConcept per SoA activity line, and set `activity` to that line copied exactly from the list below. Do not add concepts for lines not in the list, and do not split one line into several concepts or variants (e.g. no separate "... Safety" copy of a concept)
2. Use null for nciCode if not known — do not guess codes
3. Every BC must belong to exactly one category
4. Include at least one property per BC (the primary result variable)
5. **Wrap `name`/`label`/`synonyms`** - each as `{{"value": ..., "page": null, "quote": "<the activity line>"}}` as shown above. Do NOT wrap `id`, `activity`, `categoryName`, `nciCode`, `nciDecode`, or anything inside `properties`.
6. Return ONLY valid JSON — no markdown, no explanations

Now generate BiomedicalConcepts for the following SoA activities:

{activity_list}
"""


def build_bc_extraction_prompt(activity_names: list) -> str:
    """Build the full BC extraction prompt from a list of activity names."""
    activity_list = "\n".join(f"{i+1}. {name}" for i, name in enumerate(activity_names))
    return BIOMEDICAL_CONCEPT_EXTRACTION_PROMPT.format(activity_list=activity_list)
