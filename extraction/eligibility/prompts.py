"""
LLM Prompts for Eligibility Criteria Extraction.

These prompts guide the LLM to extract inclusion and exclusion criteria
from protocol Section 4-5.

Output format follows USDM v4.0 OpenAPI schema requirements.
"""

ELIGIBILITY_EXTRACTION_PROMPT = """You are an expert at extracting eligibility criteria from clinical trial protocols.
Your output must conform to USDM v4.0 schema specifications.

Analyze the provided protocol section and extract ALL inclusion and exclusion criteria.

## Required Information

### 1. Inclusion Criteria
Extract every inclusion criterion. These typically:
- Start with "Participants must..." or "Eligible participants..."
- Are numbered (1, 2, 3... or I1, I2, I3...)
- Define who CAN participate in the study

### 2. Exclusion Criteria  
Extract every exclusion criterion. These typically:
- Start with "Participants must not..." or "Excluded if..."
- Are numbered (1, 2, 3... or E1, E2, E3...)
- Define who CANNOT participate in the study

### 3. Population Information (if available)
- Target enrollment number
- Age range (minimum/maximum)
- Sex/Gender requirements
- Whether the study population includes healthy subjects (volunteers without the
  disease/condition under study) as opposed to only patients with the condition.
  Look at the title, objectives, and eligibility criteria for explicit language such
  as "healthy volunteers," "healthy subjects," or "normal volunteers" (→ true) versus
  "patients with [condition]," "participants diagnosed with [condition]" (→ false).
  Set includesHealthySubjects to true or false based on this — do not default to
  false if the protocol doesn't make it explicit; infer it from whether the
  inclusion criteria require the disease/condition under study.

## USDM v4.0 Output Format (MUST follow exactly)

USDM separates criteria into two linked entities:
1. **EligibilityCriterion** - The criterion with category (Inclusion/Exclusion)
2. **EligibilityCriterionItem** - The reusable text content

Every entity MUST have `id` and `instanceType` fields.

### Citation requirement — read before producing output

Every scalar field whose value comes from the protocol text (not a structural field
like `id`, `instanceType`, or `criterionItemId`) MUST be written as an object with
three keys instead of a bare value:
```json
"fieldName": {"value": <the actual value>, "page": <0-indexed page number>, "quote": "<exact sentence or phrase from the protocol that states this value>"}
```
- `page` is the 0-indexed page number where you found this specific value (not the
  whole section's page range).
- `quote` must be copied verbatim from the protocol — not a paraphrase. If the value
  is a reasonable default rather than something the protocol explicitly states (e.g.
  `includesHealthySubjects: false` when the protocol is simply silent on healthy
  volunteers), set `quote` to `null` and `page` to `null`.
- `id`, `instanceType`, `criterionItemId`, and other purely structural/linking fields
  are written as bare values, exactly as before — do NOT wrap these.

```json
{
  "eligibilityCriteria": [
    {
      "id": "ec_1",
      "name": {"value": "Age requirement", "page": 14, "quote": "Inclusion Criteria"},
      "identifier": {"value": "I1", "page": 14, "quote": "1."},
      "category": {
        "code": "Inclusion",
        "codeSystem": "http://www.cdisc.org/USDM/criterionCategory",
        "decode": "Inclusion Criterion"
      },
      "criterionItemId": "eci_1",
      "instanceType": "EligibilityCriterion"
    },
    {
      "id": "ec_2",
      "name": {"value": "Prior therapy exclusion", "page": 16, "quote": "Exclusion Criteria"},
      "identifier": {"value": "E1", "page": 16, "quote": "1."},
      "category": {
        "code": "Exclusion",
        "codeSystem": "http://www.cdisc.org/USDM/criterionCategory",
        "decode": "Exclusion Criterion"
      },
      "criterionItemId": "eci_2",
      "instanceType": "EligibilityCriterion"
    }
  ],
  "eligibilityCriterionItems": [
    {
      "id": "eci_1",
      "name": {"value": "Age requirement", "page": 14, "quote": "Inclusion Criteria"},
      "text": {"value": "Age ≥ 18 years at the time of signing informed consent", "page": 14, "quote": "Age ≥ 18 years at the time of signing informed consent"},
      "instanceType": "EligibilityCriterionItem"
    },
    {
      "id": "eci_2",
      "name": {"value": "Prior therapy exclusion", "page": 16, "quote": "Exclusion Criteria"},
      "text": {"value": "Prior treatment with any investigational agent within 30 days", "page": 16, "quote": "Prior treatment with any investigational agent within 30 days of randomization"},
      "instanceType": "EligibilityCriterionItem"
    }
  ],
  "population": {
    "id": "pop_1",
    "name": {"value": "Study Population", "page": null, "quote": null},
    "includesHealthySubjects": {"value": false, "page": null, "quote": null},
    "plannedEnrollmentNumber": {"value": 200, "page": 13, "quote": "Approximately 200 participants will be enrolled"},
    "plannedMinimumAge": {"value": "P18Y", "page": 14, "quote": "Age ≥ 18 years"},
    "plannedMaximumAge": {"value": "P75Y", "page": 14, "quote": "and ≤ 75 years at screening"},
    "plannedAgeIsApproximate": {"value": false, "page": 14, "quote": "Age ≥ 18 years"},
    "plannedSex": [
      {"code": "Male", "codeSystem": "http://www.cdisc.org/USDM/sex", "decode": "Male"},
      {"code": "Female", "codeSystem": "http://www.cdisc.org/USDM/sex", "decode": "Female"}
    ],
    "criterionIds": ["ec_1", "ec_2"],
    "instanceType": "StudyDesignPopulation"
  }
}
```

## Category Codes
- Inclusion = Inclusion Criterion (who CAN participate)
- Exclusion = Exclusion Criterion (who CANNOT participate)

## ID Linking Pattern
- Each EligibilityCriterion has a `criterionItemId` pointing to its EligibilityCriterionItem
- Use matching IDs: ec_1 → eci_1, ec_2 → eci_2, etc.

## Age Format
- Use ISO 8601 duration: P18Y = 18 years, P6M = 6 months
- Set plannedAgeIsApproximate to true only if the protocol states the age bound with approximation wording (e.g. "approximately 18 years", "around 65 years"). Default to false when the age is stated as an exact cutoff (e.g. "18 years or older").

## Rules

1. **Every entity must have `id` and `instanceType`** - mandatory, written as bare values
2. **Use sequential IDs** - ec_1, ec_2 for criteria; eci_1, eci_2 for items
3. **Link criteria to items** - criterionItemId must match an item's id (bare value, not wrapped)
4. **Extract exact text** - Copy criterion text verbatim into the item's `text.value`,
   and repeat that same verbatim text as `text.quote`
5. **Use identifier** - Preserve original numbering (I1, E1, 1, 2, etc.)
6. **Maintain order** - Keep criteria in protocol order
7. **Be complete** - Include sub-criteria in the text
8. **includesHealthySubjects is derived, not a default** - the `value: false` shown in
   the example below is for a patient population (inclusion criteria require the
   condition under study); set `value` to `true` instead whenever the protocol enrolls
   healthy volunteers. Base it on what THIS protocol's criteria actually say. If the
   protocol doesn't explicitly address this, set `value: false`, `page: null`, `quote: null`.
9. **Wrap every citable scalar field** - every field value you extract from the
   protocol (not `id`/`instanceType`/`criterionItemId`/`category`) must be
   `{"value": ..., "page": ..., "quote": ...}` as shown above. Use `page: null,
   quote: null` only when the value is a reasonable default, not something the
   protocol states.
10. **Return ONLY valid JSON** - no markdown fences, no explanations

Now analyze the protocol content and extract the eligibility criteria:
"""


ELIGIBILITY_PAGE_FINDER_PROMPT = """Analyze these PDF pages and identify which pages contain eligibility criteria.

Look for pages that contain:
1. **Inclusion Criteria section** - Usually labeled "Inclusion Criteria" or "Eligibility - Inclusion"
2. **Exclusion Criteria section** - Usually labeled "Exclusion Criteria" or "Eligibility - Exclusion"
3. **Study Population section** - May contain eligibility information

These are typically found in:
- Section 4: Study Population
- Section 5: Eligibility Criteria
- Synopsis section (summary of I/E criteria)

Return a JSON object:
```json
{
  "eligibility_pages": [page_numbers],
  "inclusion_start_page": page_number,
  "exclusion_start_page": page_number,
  "confidence": "high/medium/low",
  "notes": "any relevant observations"
}
```

Pages are 0-indexed. Return ONLY valid JSON.
"""


def build_eligibility_extraction_prompt(protocol_text: str, context_hints: str = "") -> str:
    """Build the full extraction prompt with protocol content and optional context hints."""
    MAX_CHARS = 60_000  # Cap to avoid LLM timeouts on large protocols
    text = protocol_text[:MAX_CHARS]
    prompt = ELIGIBILITY_EXTRACTION_PROMPT
    if context_hints:
        prompt += f"\n\nCONTEXT FROM PRIOR EXTRACTION:{context_hints}"
    prompt += f"\n\n---\n\nPROTOCOL CONTENT:\n\n{text}"
    return prompt


def build_page_finder_prompt() -> str:
    """Build prompt for finding eligibility pages."""
    return ELIGIBILITY_PAGE_FINDER_PROMPT
