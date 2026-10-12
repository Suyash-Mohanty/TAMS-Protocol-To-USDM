"""
LLM Prompts for Study Design Structure Extraction.

These prompts guide the LLM to extract study design elements
from protocol synopsis and study design sections.
"""

STUDY_DESIGN_EXTRACTION_PROMPT = """You are an expert at extracting study design information from clinical trial protocols.

Analyze the provided protocol section and extract the study design structure.

## Required Information

### 1. Study Design Type
- Is this Interventional or Observational?
- If Interventional: Treatment, Prevention, Diagnostic, Supportive Care, Screening, Health Services Research, Basic Science?
- Intervention model (`model`) — exactly one of "Parallel", "Crossover", "Single Group", "Factorial", "Sequential":
  - Crossover: each participant receives more than one treatment in sequence across periods (e.g., "2-period crossover", treatment sequences AB/BA, washout between periods)
  - Parallel: each participant receives one treatment, groups run side by side
  - Single Group: all participants receive the same intervention (one arm)
  - Factorial: two or more interventions evaluated in combination (e.g., 2x2)
  - Sequential: groups/cohorts enrolled one after another (e.g., dose-escalation cohorts)

### 2. Blinding
- Open Label, Single Blind, Double Blind, Triple Blind, or Quadruple Blind?
- Who is blinded? (Subject, Investigator, Outcome Assessor, Caregiver, Data Analyst)

### 3. Randomization
- Randomized or Non-Randomized?
- Allocation ratio (e.g., 1:1, 2:1, 1:1:1)
- Stratification factors (e.g., age, disease severity, site)

### 4. Control Type
- Placebo, Active Control, Dose Comparison, No Treatment, Historical Control?

### 5. Study Arms
Extract treatment arms - but DISTINGUISH between:
- **Parallel Arms**: Different treatments given to DIFFERENT subjects (e.g., Drug A vs Placebo)
- **Within-Subject Titration**: Same subjects receive sequential doses (e.g., 15mg for 4 weeks, then titrated to 30mg)

**CRITICAL**: If the protocol describes dose escalation/titration where ALL subjects start at one dose and increase to another:
- This is NOT two separate arms
- Model as ONE arm with "isTitration": true and "doseEpochs" array
- Look for phrases: "titrated up", "dose escalation", "following X period", "after Day X increase"

For each arm extract:
- Arm name
- Arm type (Experimental, Active Comparator, Placebo Comparator, No Intervention)
- Description
- isTitration (true/false)
- doseEpochs (if titration): [{dose, startDay, endDay}]

### 6. Study Cohorts (if any)
Sub-populations within the study (NOT dose levels):
- Cohort name
- Defining characteristic (e.g., treatment-naive vs experienced)

### 7. Study Phases/Epochs (if described)
- Screening, Treatment, Follow-up, etc.
- For titration studies, include dose-level epochs (e.g., "15mg Treatment", "30mg Treatment")

## Output Format

Return a JSON object with this exact structure:

### Citation requirement — read before producing output

Every scalar field whose value comes from the protocol text (not a structural/
classification field like `type`, `model`, `schema`, `maskedRoles`, `randomizationType`,
`controlType`, `trialIntentTypes`, `stratificationFactors`, `therapeuticAreas`, or
`isTitration`) MUST be written as an object with three keys instead of a bare value:
```json
"fieldName": {"value": <the actual value>, "page": <0-indexed page number>, "quote": "<exact sentence or phrase from the protocol that states this value>"}
```
- `page` is the 0-indexed page number where you found this specific value (not the
  whole section's page range).
- `quote` must be copied verbatim from the protocol — not a paraphrase. If the value
  is a reasonable default rather than something the protocol explicitly states, set
  `quote` to `null` and `page` to `null`.
- Classification fields chosen from a controlled vocabulary (`type`, `model`,
  blinding `schema`, `maskedRoles`, `randomizationType`, `controlType`,
  `trialIntentTypes`, `stratificationFactors`, `therapeuticAreas`, `isTitration`)
  stay bare values, exactly as before — do NOT wrap these.

```json
{
  "studyDesign": {
    "type": "Interventional",
    "model": "Single Group",
    "trialIntentTypes": ["Treatment"],
    "description": {"value": "All participants receive ALXN1840 with dose titration", "page": 1, "quote": "All participants will receive ALXN1840 with dose titration from 15 mg to 30 mg"},
    "blinding": {
      "schema": "Open Label",
      "maskedRoles": []
    },
    "randomization": {
      "type": "Non-Randomized",
      "allocationRatio": null,
      "stratificationFactors": []
    },
    "controlType": null,
    "therapeuticAreas": ["Hepatology"]
  },
  "arms": [
    {
      "name": {"value": "ALXN1840 Treatment", "page": 1, "quote": "ALXN1840 Treatment Arm"},
      "type": "Experimental Arm",
      "description": {"value": "All participants receive ALXN1840 with dose titration from 15mg to 30mg", "page": 1, "quote": "All participants will receive ALXN1840 with dose titration from 15 mg to 30 mg"},
      "isTitration": true,
      "doseEpochs": [
        {"dose": {"value": "15 mg/day", "page": 1, "quote": "15 mg/day"}, "startDay": {"value": 1, "page": 1, "quote": "Day 1"}, "endDay": {"value": 28, "page": 1, "quote": "Day 28"}, "description": {"value": "Initial dose period", "page": 1, "quote": "initial 15 mg dose period"}},
        {"dose": {"value": "30 mg/day", "page": 1, "quote": "30 mg/day"}, "startDay": {"value": 29, "page": 1, "quote": "Day 29"}, "endDay": {"value": null, "page": null, "quote": null}, "description": {"value": "Titrated dose period", "page": 1, "quote": "titrated to 30 mg thereafter"}}
      ]
    }
  ],
  "cohorts": [
    {
      "name": {"value": "Treatment-naive", "page": 2, "quote": "treatment-naive participants"},
      "characteristic": {"value": "Participants who have not received prior WD therapy", "page": 2, "quote": "participants who have not received prior Wilson disease therapy"}
    },
    {
      "name": {"value": "Previously treated", "page": 2, "quote": "previously treated participants"},
      "characteristic": {"value": "Participants with prior chelator or zinc therapy", "page": 2, "quote": "participants with prior chelator or zinc therapy"}
    }
  ],
  "epochs": [
    {"name": {"value": "Screening", "page": 1, "quote": "Screening Period"}, "description": {"value": "Up to 21 days", "page": 1, "quote": "up to 21 days"}},
    {"name": {"value": "15mg Treatment Period", "page": 1, "quote": "15 mg Treatment Period"}, "description": {"value": "Days 1-28, initial dose", "page": 1, "quote": "Days 1 to 28"}},
    {"name": {"value": "30mg Treatment Period", "page": 1, "quote": "30 mg Treatment Period"}, "description": {"value": "Day 29 onwards, titrated dose", "page": 1, "quote": "from Day 29 onward"}},
    {"name": {"value": "Follow-up", "page": 1, "quote": "Follow-up Period"}, "description": {"value": "4 weeks after last dose", "page": 1, "quote": "4 weeks after the last dose"}}
  ]
}
```

### Example 2: Parallel Arms (for comparison)
If the study randomizes subjects to DIFFERENT doses (not titration):
```json
{
  "arms": [
    {
      "name": {"value": "Low Dose Arm", "page": 1, "quote": "Low Dose Arm"},
      "type": "Experimental Arm",
      "description": {"value": "Randomized to receive 15mg for entire study", "page": 1, "quote": "randomized to receive 15 mg for the entire study"},
      "isTitration": false
    },
    {
      "name": {"value": "High Dose Arm", "page": 1, "quote": "High Dose Arm"},
      "type": "Experimental Arm",
      "description": {"value": "Randomized to receive 30mg for entire study", "page": 1, "quote": "randomized to receive 30 mg for the entire study"},
      "isTitration": false
    }
  ]
}
```

## Rules

1. **Extract from design section** - Usually Section 3 or Synopsis
2. **Classify arms correctly** - Experimental vs Comparator based on study drug vs control
3. **Identify cohorts** - Sub-groups based on prior treatment, disease severity, etc.
4. **Use standard terminology** - Use USDM-compliant codes where possible
5. **CRITICAL: Detect titration** - If ALL subjects go through sequential doses, use ONE arm with isTitration=true
6. **Wrap every citable scalar field** - every field value you extract from the
   protocol (not `type`/`model`/`schema`/`maskedRoles`/`randomizationType`/
   `controlType`/`trialIntentTypes`/`stratificationFactors`/`therapeuticAreas`/
   `isTitration`) must be `{"value": ..., "page": ..., "quote": ...}` as shown above.
   Use `page: null, quote: null` only when the value is a reasonable default, not
   something the protocol states.
7. **Return ONLY valid JSON** - no markdown, no explanations

Now analyze the protocol content and extract the study design:
"""


DESIGN_PAGE_FINDER_PROMPT = """Analyze these PDF pages and identify which pages contain study design information.

Look for pages that contain:
1. **Synopsis** - Usually has study design overview table
2. **Study Design section** - Usually Section 3
3. **Randomization/Blinding description**
4. **Treatment arms description**

Return a JSON object:
```json
{
  "design_pages": [page_numbers],
  "synopsis_page": page_number,
  "confidence": "high/medium/low",
  "notes": "any relevant observations"
}
```

Pages are 0-indexed. Return ONLY valid JSON.
"""


def build_study_design_extraction_prompt(protocol_text: str, context_hints: str = "") -> str:
    """Build the full extraction prompt with protocol content and optional context hints."""
    prompt = STUDY_DESIGN_EXTRACTION_PROMPT
    if context_hints:
        prompt += f"\n\nCONTEXT FROM PRIOR EXTRACTION:{context_hints}"
    prompt += f"\n\n---\n\nPROTOCOL CONTENT:\n\n{protocol_text}"
    return prompt


def build_page_finder_prompt() -> str:
    """Build prompt for finding study design pages."""
    return DESIGN_PAGE_FINDER_PROMPT
