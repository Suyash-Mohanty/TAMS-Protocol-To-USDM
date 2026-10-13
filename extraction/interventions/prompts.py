"""
LLM Prompts for Interventions & Products Extraction.

These prompts guide the LLM to extract study interventions and products
from protocol investigational product sections.
"""

INTERVENTIONS_EXTRACTION_PROMPT = """You are an expert at extracting study intervention information from clinical trial protocols.

Analyze the provided protocol section and extract ALL study interventions, products, and administration details.

## Required Information

### 1. Study Interventions
For each intervention give a `role` (CDISC study intervention role) and a `type`:
- `role` — one of:
  - "Experimental Intervention" — the investigational product(s) under study
  - "Active Comparator" — an active reference treatment the investigational product is compared against
  - "Placebo"
  - "Challenge Agent" — given per protocol to provoke the condition the study treats or measures (e.g. insulin infused to induce hypoglycemia, an allergen challenge), not as treatment
  - "Rescue Medicine" — given when the study treatment fails or for safety rescue
  - "Background Treatment" — standard-of-care treatment all participants continue alongside the study treatment
  - "Additional Required Treatment" — other treatment the protocol requires participants to receive
  - "Diagnostic" — an agent used for diagnosis/imaging
  - "Concomitant Medication" — permitted, restricted or prohibited medications and prior medications to wash out (listed so they are not mistaken for study interventions)
- `type` — one of "Drug", "Biologic", "Device", "Procedure", "Dietary Supplement", "Behavioral Therapy", "Radiation", "Genetic", "Diagnostic Test", "Combination Product"

### 2. Products (AdministrableProduct)
For each product extract:
- Product name (generic and/or trade name) exactly as the protocol states it. Do not add a dose form, route or formulation to the name unless the protocol itself uses it as part of the product name or to tell two products apart (e.g. "Mirikizumab IV" vs "Mirikizumab SC"); never guess a form such as "tablet/capsule" that the protocol does not state
- activeIngredients — the active substance name(s) the product contains, matching names in "substances" (e.g. a product "GlucaGen" or "LY900018 nasal powder" contains "glucagon"); empty for placebo
- Dose form — as the protocol words it, keeping detail (e.g. "film-coated tablet", "lyophilized powder for solution for injection", "nasal powder", "solution for injection"); omit if the protocol doesn't state it
- designation — "IMP" if the product is being tested or used as a reference in the trial (investigational product, active comparator, placebo); "NIMP" for auxiliary products used per protocol but not under test (challenge agents such as insulin used to induce hypoglycemia, rescue, background or concomitant medication)
- Strength as a separate numeric value and unit — e.g. for "15 mg" use strengthValue: 15, strengthUnit: "mg". Do not combine them into one string.
- For a concentration (amount per volume, e.g. "1 mg/mL", "100 U/mL", "0.3 U/mL after dilution"), also give the denominator: strengthDenominatorValue: 1, strengthDenominatorUnit: "mL"
- Strength name/label — ONLY if the protocol itself gives this specific strength a distinct designation (e.g., "Low Dose Tablet", "High Dose Tablet", "Formulation A") use strengthName for that exact text. Do not invent one if the protocol doesn't name it; omit strengthName entirely in that case.
- Manufacturer (if mentioned)

### 3. Active Substances
- Generic name of active ingredient
- Substance codes if available (UNII, CAS)

### 4. Administration Details
- Dose escalation / titration: give one administration per step with the dose ACTUALLY RECEIVED in that step, starting from the protocol's stated starting dose (e.g. "start at 2 mg and step up every 2 weeks to the assigned dose of 2, 4 or 8 mg": the 8 mg arm is 2 mg weeks 0-2, 4 mg weeks 2-4, then 8 mg from week 4; the 4 mg arm is 2 mg weeks 0-2, then 4 mg from week 2). Steps of one arm follow each other without gaps or overlaps, and the maintenance administration starts when that arm reaches its target dose - not at the end of the longest arm's escalation. Name each step by the arm and step (e.g. "<drug> 8 mg arm - step 1") and state its weeks in the duration
- Dose (e.g., "15 mg", "100 mg/m2")
- Frequency (e.g., "once daily", "every 2 weeks")
- Route (oral, IV, SC, IM, etc.)
- Duration of treatment

### 5. Medical Devices (if applicable)
- Device name
- Manufacturer
- Purpose

## Output Format

Return a JSON object with this exact structure:

### Citation requirement — read before producing output

Every scalar field whose value comes from the protocol text (not a structural field
like `id`, `instanceType`, `role`, `type`, `designation`, `route`, or `activeIngredients`)
MUST be written as an object with three keys instead of a bare value:
```json
"fieldName": {"value": <the actual value>, "page": <0-indexed page number>, "quote": "<exact sentence or phrase from the protocol that states this value>"}
```
- `page` is the 0-indexed page number where you found this specific value (not the
  whole section's page range).
- `quote` must be copied verbatim from the protocol — not a paraphrase. If the value
  is a reasonable default rather than something the protocol explicitly states, set
  `quote` to `null` and `page` to `null`.
- `id`, `instanceType`, `role`, `type`, `designation`, `route`, and `activeIngredients`
  are classification/linking fields chosen from a controlled vocabulary — write these
  as bare values, exactly as before — do NOT wrap these.

```json
{
  "interventions": [
    {
      "name": {"value": "ALXN1840", "page": 2, "quote": "ALXN1840"},
      "role": "Experimental Intervention",
      "type": "Drug",
      "description": {"value": "Investigational product for Wilson disease", "page": 2, "quote": "ALXN1840 is being developed for the treatment of Wilson disease"}
    },
    {
      "name": {"value": "Placebo", "page": 2, "quote": "matching placebo"},
      "role": "Placebo",
      "type": "Drug",
      "description": {"value": "Matching placebo tablets", "page": 2, "quote": "matching placebo tablets"}
    },
    {
      "name": {"value": "Paracetamol/acetaminophen", "page": 10, "quote": "paracetamol/acetaminophen"},
      "role": "Concomitant Medication",
      "type": "Drug",
      "description": {"value": "Permitted for mild pain relief", "page": 10, "quote": "permitted for the treatment of mild pain"}
    }
  ],
  "products": [
    {
      "name": {"value": "ALXN1840 tablets", "page": 3, "quote": "ALXN1840 film-coated tablets"},
      "doseForm": {"value": "Film-coated tablet", "page": 3, "quote": "film-coated tablet"},
      "designation": "IMP",
      "activeIngredients": ["bis-choline tetrathiomolybdate"],
      "strengthValue": {"value": 15, "page": 3, "quote": "15 mg"},
      "strengthUnit": {"value": "mg", "page": 3, "quote": "15 mg"},
      "manufacturer": {"value": "Alexion Pharmaceuticals", "page": 3, "quote": "manufactured by Alexion Pharmaceuticals"}
    }
  ],
  "substances": [
    {
      "name": {"value": "bis-choline tetrathiomolybdate", "page": 3, "quote": "bis-choline tetrathiomolybdate"},
      "description": {"value": "Active pharmaceutical ingredient", "page": null, "quote": null}
    }
  ],
  "administrations": [
    {
      "name": {"value": "ALXN1840 15 mg daily", "page": 4, "quote": "ALXN1840 15 mg once daily"},
      "dose": {"value": "15 mg", "page": 4, "quote": "15 mg"},
      "frequency": {"value": "once daily", "page": 4, "quote": "once daily"},
      "route": "Oral",
      "duration": {"value": "24 weeks", "page": 4, "quote": "for 24 weeks"}
    },
    {
      "name": {"value": "ALXN1840 30 mg daily", "page": 4, "quote": "ALXN1840 30 mg once daily"},
      "dose": {"value": "30 mg", "page": 4, "quote": "30 mg"},
      "frequency": {"value": "once daily", "page": 4, "quote": "once daily"},
      "route": "Oral",
      "duration": {"value": "After Day 29", "page": 4, "quote": "from Day 29 onward"}
    }
  ],
  "devices": []
}
```

## Rules

1. **Extract from IP section** - Usually Section 5 or 6 (Investigational Product)
2. **Include all dosing regimens** - Different doses, titration steps, dose escalation
3. **Extract concomitant medications** - Look in "Concomitant Medications" or "Prior and Concomitant Therapy" sections for permitted/prohibited medications
4. **Use standard terminology**:
   - Roles: exactly as listed in section 1 (CDISC study intervention roles)
   - Routes: "Oral", "Intravenous", "Subcutaneous", "Intramuscular", "Topical", "Inhalation"
   - Forms: "Tablet", "Capsule", "Solution", "Injection", "Cream", "Patch"
5. **Be precise with doses** - Include units (mg, mg/kg, mg/m2, etc.)
6. **Only set strengthName when the protocol names the strength distinctly** - most protocols don't; leave it unset rather than fabricating a label
7. **Wrap every citable scalar field** - every field value you extract from the
   protocol (not `id`/`instanceType`/`role`/`type`/`designation`/`route`/
   `activeIngredients`) must be `{"value": ..., "page": ..., "quote": ...}` as shown
   above. Use `page: null, quote: null` only when the value is a reasonable default,
   not something the protocol states.
8. **Return ONLY valid JSON** - no markdown, no explanations

Now analyze the protocol content and extract the interventions:
"""


INTERVENTIONS_PAGE_FINDER_PROMPT = """Analyze these PDF pages and identify which pages contain intervention/product information.

Look for pages that contain:
1. **Investigational Product section** - Usually Section 5 or 6
2. **Study Treatment section**
3. **Dose and Administration section**
4. **Product description/formulation**
5. **Concomitant Medications section** - Permitted/prohibited medications
6. **Prior and Concomitant Therapy section**

Return a JSON object:
```json
{
  "intervention_pages": [page_numbers],
  "confidence": "high/medium/low",
  "notes": "any relevant observations"
}
```

Pages are 0-indexed. Return ONLY valid JSON.
"""


def build_interventions_extraction_prompt(protocol_text: str, context_hints: str = "") -> str:
    """Build the full extraction prompt with protocol content and optional context hints."""
    prompt = INTERVENTIONS_EXTRACTION_PROMPT
    if context_hints:
        prompt += f"\n\nCONTEXT FROM PRIOR EXTRACTION:{context_hints}"
    prompt += f"\n\n---\n\nPROTOCOL CONTENT:\n\n{protocol_text}"
    return prompt


def build_page_finder_prompt() -> str:
    """Build prompt for finding intervention pages."""
    return INTERVENTIONS_PAGE_FINDER_PROMPT
