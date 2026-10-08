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

```json
{
  "eligibilityCriteria": [
    {
      "id": "ec_1",
      "name": "Age requirement",
      "identifier": "I1",
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
      "name": "Prior therapy exclusion",
      "identifier": "E1",
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
      "name": "Age requirement",
      "text": "Age ≥ 18 years at the time of signing informed consent",
      "instanceType": "EligibilityCriterionItem"
    },
    {
      "id": "eci_2",
      "name": "Prior therapy exclusion",
      "text": "Prior treatment with any investigational agent within 30 days",
      "instanceType": "EligibilityCriterionItem"
    }
  ],
  "population": {
    "id": "pop_1",
    "name": "Study Population",
    "includesHealthySubjects": false,
    "plannedEnrollmentNumber": {
      "maxValue": 200,
      "instanceType": "Range"
    },
    "plannedMinimumAge": "P18Y",
    "plannedMaximumAge": "P75Y",
    "plannedAgeIsApproximate": false,
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

1. **Every entity must have `id` and `instanceType`** - mandatory
2. **Use sequential IDs** - ec_1, ec_2 for criteria; eci_1, eci_2 for items
3. **Link criteria to items** - criterionItemId must match an item's id
4. **Extract exact text** - Copy criterion text verbatim in the item
5. **Use identifier** - Preserve original numbering (I1, E1, 1, 2, etc.)
6. **Maintain order** - Keep criteria in protocol order
7. **Be complete** - Include sub-criteria in the text
8. **includesHealthySubjects is derived, not a default** - the `false` shown in the
   example below is for a patient population (inclusion criteria require the
   condition under study); set it to `true` instead whenever the protocol enrolls
   healthy volunteers. Base it on what THIS protocol's criteria actually say.
9. **Return ONLY valid JSON** - no markdown fences, no explanations

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
