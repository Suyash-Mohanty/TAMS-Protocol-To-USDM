"""
LLM Prompts for Procedure and Medical Device extraction.
"""

PROCEDURES_SYSTEM_PROMPT = """You are an expert clinical protocol analyst specializing in extracting 
procedure and medical device information from clinical trial protocols.

Your task is to identify:
1. Clinical procedures performed during the study
2. Medical devices used (drug delivery, diagnostic, monitoring devices)
3. Drug ingredients and their strengths

Return valid JSON only."""

PROCEDURES_USER_PROMPT = """Extract all Procedures, Medical Devices, and Drug Ingredients from the following protocol text.

**Procedures to extract:**
- Sampling procedures (blood draws, biopsies, urine collection)
- Diagnostic procedures (imaging, ECG, endoscopy)
- Therapeutic procedures (infusions, injections)
- Monitoring procedures (vital signs, telemetry)
- Assessment procedures (physical exams, neurological assessments)

**Medical Devices to extract:**
- Drug delivery devices (infusion pumps, autoinjectors, inhalers, syringes)
- Monitoring devices (glucose monitors, ECG devices, wearables)
- Diagnostic devices (spirometers, imaging equipment)
- Venous access devices (cannulas, catheters, IV lines)
- Any specific device mentioned by name or model

**DO NOT classify as medical devices:**
- Drug formulations (tablets, capsules, pills, solutions, suspensions)
- The study drug itself (this is an intervention, not a device)
- Chemical compounds or active ingredients

**Ingredients/Strengths to extract:**
- Active pharmaceutical ingredients
- Excipients if mentioned
- Drug strengths and concentrations

**Biospecimen Retention to extract:**
- Statements about whether collected biospecimens (blood, tissue, urine, etc.) are
  retained after their initial use, or destroyed
- Retention duration (e.g. "up to 15 years")
- Whether retained specimens may be used for future research
- Genetic/DNA testing consent language, and whether retained specimens include DNA
- If the protocol is silent on specimen retention, do not include this key at all —
  do not invent a statement

### Citation requirement — read before producing output

Every scalar field whose value comes from the protocol text (not a structural field
like `id`, `substanceId`, `scopeId`, `procedureType`, `deviceType`, or `role`) MUST be
written as an object with three keys instead of a bare value:
```json
"fieldName": {{"value": <the actual value>, "page": <0-indexed page number>, "quote": "<exact sentence or phrase from the protocol that states this value>"}}
```
- `page` is the 0-indexed page number where you found this specific value.
- `quote` must be copied verbatim from the protocol — not a paraphrase. If you cannot
  find a specific supporting quote, set `quote` to `null` and `page` to `null` rather
  than guessing.
- `id`, `substanceId`, `scopeId`, `procedureType`, `deviceType`, and `role` are
  structural/linking fields and stay bare — do NOT wrap those. The nested `code`
  object on a Procedure (CPT/SNOMED code, codeSystem, decode) is also structural
  and stays bare.

Return JSON in this exact format:
```json
{{
  "procedures": [
    {{
      "id": "proc_1",
      "name": {{"value": "Venipuncture", "page": 20, "quote": "Blood will be collected by venipuncture"}},
      "label": {{"value": "Blood Draw", "page": 20, "quote": "Blood Draw"}},
      "description": {{"value": "Collection of blood samples for laboratory analysis", "page": 20, "quote": "Blood will be collected by venipuncture for laboratory analysis"}},
      "procedureType": "Sampling",
      "code": {{
        "code": "36415",
        "codeSystem": "CPT",
        "decode": "Collection of venous blood by venipuncture"
      }}
    }}
  ],
  "medicalDevices": [
    {{
      "id": "dev_1",
      "name": {{"value": "Prefilled Syringe", "page": 25, "quote": "study drug will be administered via prefilled syringe"}},
      "label": {{"value": "PFS", "page": 25, "quote": "PFS"}},
      "description": {{"value": "Prefilled syringe for subcutaneous injection", "page": 25, "quote": "prefilled syringe for subcutaneous injection"}},
      "deviceType": "Drug Delivery Device",
      "manufacturer": {{"value": "Manufacturer Name", "page": 25, "quote": "manufactured by Manufacturer Name"}},
      "modelNumber": {{"value": "Model-123", "page": 25, "quote": "Model-123"}}
    }}
  ],
  "deviceIdentifiers": [
    {{
      "id": "dev_id_1",
      "text": {{"value": "UDI-12345", "page": 25, "quote": "UDI: UDI-12345"}},
      "scopeId": "org_fda"
    }}
  ],
  "ingredients": [
    {{
      "id": "ing_1",
      "name": {{"value": "Drug Active Ingredient", "page": 18, "quote": "active ingredient Drug Active Ingredient"}},
      "role": "Active",
      "substanceId": "subst_1"
    }}
  ],
  "strengths": [
    {{
      "id": "str_1",
      "value": {{"value": 100, "page": 18, "quote": "100 mg/mL"}},
      "unit": {{"value": "mg", "page": 18, "quote": "100 mg/mL"}},
      "numeratorValue": {{"value": 100, "page": 18, "quote": "100 mg/mL"}},
      "numeratorUnit": {{"value": "mg", "page": 18, "quote": "100 mg/mL"}},
      "denominatorValue": {{"value": 1, "page": 18, "quote": "100 mg/mL"}},
      "denominatorUnit": {{"value": "mL", "page": 18, "quote": "100 mg/mL"}}
    }}
  ],
  "biospecimenRetentions": [
    {{
      "id": "bior_1",
      "name": {{"value": "Retained Biospecimens for Future Research", "page": 30, "quote": "Residual samples will be retained for future research"}},
      "isRetained": true,
      "description": {{"value": "Residual blood and tissue samples will be retained for up to 15 years for future exploratory research.", "page": 30, "quote": "Residual blood and tissue samples will be retained for up to 15 years for future exploratory research."}},
      "includesDNA": {{"value": true, "page": 30, "quote": "samples may be used for genetic/DNA testing"}}
    }}
  ]
}}
```

Valid procedureType values: Diagnostic, Therapeutic, Surgical, Sample Collection, Imaging, Monitoring, Assessment
Valid deviceType values: Drug Delivery Device, Diagnostic Device, Monitoring Device, Implantable Device, Wearable Device
Valid ingredient role values: Active, Inactive, Adjuvant

PROTOCOL TEXT:
{protocol_text}

Extract all procedures, devices, and ingredients mentioned. Include standard medical
codes if identifiable. Wrap every citable scalar field as shown above (`name`,
`label`, `description`, `manufacturer`, `modelNumber`, `text`, `value`, `unit`,
`numeratorValue`, `numeratorUnit`, `denominatorValue`, `denominatorUnit`,
`isRetained`, `includesDNA`); leave `id`, `substanceId`, `scopeId`, `procedureType`,
`deviceType`, `role`, and the nested `code` object as bare values."""


def get_procedures_prompt(protocol_text: str) -> str:
    """Generate the full prompt for procedures extraction."""
    MAX_CHARS = 60_000  # Cap to avoid LLM timeouts on large protocols
    text = protocol_text[:MAX_CHARS]
    return PROCEDURES_USER_PROMPT.format(protocol_text=text)


def get_system_prompt() -> str:
    """Get the system prompt for procedures extraction."""
    return PROCEDURES_SYSTEM_PROMPT
