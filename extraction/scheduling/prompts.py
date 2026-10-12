"""
LLM Prompts for Scheduling Logic extraction.
"""

SCHEDULING_SYSTEM_PROMPT = """You are an expert clinical protocol analyst specializing in study timing, 
visit windows, and protocol decision logic.

Your task is to extract:
1. Timing constraints (visit windows, intervals between visits)
2. Transition rules (criteria for moving between study phases)
3. Conditions for branching or adaptive designs
4. Early termination and discontinuation criteria

Return valid JSON only."""

SCHEDULING_USER_PROMPT = """Extract all Scheduling Logic from the following protocol text.

**Timing to extract:**
- Visit windows (e.g., "Day 1 ± 3 days")
- Intervals between visits (e.g., "4 weeks after previous visit")
- Time relative to events (e.g., "within 7 days of screening")
For every timing give `visit`: the visit it applies to, using the visit/encounter label exactly as written in the Schedule of Activities column header (e.g., "Period 1 Day -1", "V4 (Week 4)", "Follow-up/ED"), and `relativeToVisit`: the visit it is measured from (e.g. the dosing or randomization visit), also as written in the SoA; use null when not tied to a specific visit.
Only extract timings of scheduled visits and assessments. Do NOT extract eligibility look-back or washout periods (e.g., "no insulin within 90 days before screening") — those belong to the eligibility criteria.

**Transition Rules to extract:**
- Criteria for epoch transitions (e.g., screening to treatment)
- Discontinuation criteria
- Rescue therapy rules
- Dose modification triggers

**Conditions to extract:**
- Eligibility conditions beyond inclusion/exclusion
- Response-based decisions
- Safety stopping rules
- Interim analysis conditions

**Schedule Exits to extract:**
- Early termination criteria
- Study completion criteria
- Protocol deviations leading to exit

### Citation requirement — read before producing output

Every scalar field whose value comes from the protocol text (not a structural field
like `id`, `timingType`, `relativeTo`, `unit`, `transitionType`, `exitType`,
`conditionId`/`conditionIds`, `fromElementId`, `toElementId`, `timepointId`, or
`defaultTransitionId`) MUST be written as an object with three keys instead of a
bare value:
```json
"fieldName": {{"value": <the actual value>, "page": <0-indexed page number>, "quote": "<exact sentence or phrase from the protocol that states this value>"}}
```
- `page` is the 0-indexed page where you found this specific value (not the whole
  section's page range).
- `quote` must be copied verbatim from the protocol — not a paraphrase.
- If a value is a reasonable default rather than something the protocol states, set
  `quote` and `page` to `null`.
- Structural/linking/classification fields (`id`, `timingType`, `relativeTo`, `unit`,
  `transitionType`, `exitType`, `conditionId`/`conditionIds`, `fromElementId`,
  `toElementId`, `timepointId`, `defaultTransitionId`) stay bare, exactly as before —
  do NOT wrap these.

Return JSON in this exact format:
```json
{{
  "timings": [
    {{
      "id": "timing_1",
      "name": {{"value": "Screening Window", "page": 12, "quote": "Screening Period (Day -28 to Day -1)"}},
      "visit": {{"value": "Screening (Day -28 to -1)", "page": 12, "quote": "Screening (Day -28 to -1)"}},
      "relativeToVisit": {{"value": "Day 1", "page": 12, "quote": "relative to Day 1 (randomization)"}},
      "timingType": "Within",
      "value": {{"value": 28, "page": 12, "quote": "within 28 days prior to randomization"}},
      "unit": "days",
      "relativeTo": "Randomization",
      "windowLower": {{"value": -28, "page": 12, "quote": "Day -28 to Day -1"}},
      "windowUpper": {{"value": -1, "page": 12, "quote": "Day -28 to Day -1"}}
    }},
    {{
      "id": "timing_2",
      "name": {{"value": "Week 4 Visit Window", "page": 14, "quote": "Visit 4 (Week 4 ± 3 days)"}},
      "visit": {{"value": "Week 4", "page": 14, "quote": "Visit 4 (Week 4 ± 3 days)"}},
      "relativeToVisit": {{"value": "Day 1", "page": 14, "quote": "relative to Day 1"}},
      "timingType": "At",
      "value": {{"value": 28, "page": 14, "quote": "Week 4 ± 3 days"}},
      "unit": "days",
      "relativeTo": "Randomization",
      "windowLower": {{"value": -3, "page": 14, "quote": "Week 4 ± 3 days"}},
      "windowUpper": {{"value": 3, "page": 14, "quote": "Week 4 ± 3 days"}}
    }}
  ],
  "conditions": [
    {{
      "id": "cond_1",
      "name": {{"value": "Response Criteria", "page": 20, "quote": "Response Criteria"}},
      "description": {{"value": "Criteria for determining treatment response", "page": 20, "quote": "criteria for determining treatment response"}},
      "text": {{"value": "50% reduction in primary endpoint from baseline", "page": 20, "quote": "a 50% reduction in the primary endpoint from baseline"}}
    }}
  ],
  "transitionRules": [
    {{
      "id": "trans_1",
      "name": {{"value": "Screen to Treatment Transition", "page": 15, "quote": "Transition from Screening to Treatment"}},
      "transitionType": "Epoch Transition",
      "fromElementId": "epoch_screening",
      "toElementId": "epoch_treatment",
      "text": {{"value": "Subject must meet all eligibility criteria", "page": 15, "quote": "the subject must meet all eligibility criteria"}}
    }},
    {{
      "id": "trans_2",
      "name": {{"value": "Discontinuation for Safety", "page": 22, "quote": "Discontinuation for Safety Reasons"}},
      "transitionType": "Discontinuation",
      "text": {{"value": "ALT > 5x ULN requires treatment discontinuation", "page": 22, "quote": "ALT greater than 5x ULN requires discontinuation of study treatment"}}
    }}
  ],
  "scheduleExits": [
    {{
      "id": "exit_1",
      "name": {{"value": "Early Termination", "page": 25, "quote": "Early Termination Visit"}},
      "exitType": "Early Termination",
      "description": {{"value": "Subject may discontinue for any reason", "page": 25, "quote": "a subject may discontinue from the study for any reason"}}
    }},
    {{
      "id": "exit_2",
      "name": {{"value": "Study Completion", "page": 26, "quote": "End of Study Visit"}},
      "exitType": "Completion",
      "description": {{"value": "Completion of all protocol-required visits", "page": 26, "quote": "completion of all protocol-required visits"}}
    }}
  ],
  "decisionInstances": [
    {{
      "id": "dec_1",
      "name": {{"value": "Response Assessment Decision", "page": 18, "quote": "Response Assessment and Decision Point"}},
      "timepointId": "pt_week12",
      "conditionIds": ["cond_1"],
      "description": {{"value": "Decision point for response-based continuation", "page": 18, "quote": "a decision point for response-based continuation of treatment"}}
    }}
  ]
}}
```

Valid timingType values: Before, After, Within, At, Between
Valid relativeTo values: Study Start, Randomization, First Dose, Last Dose, Previous Visit, Screening, Baseline, End of Treatment
Valid transitionType values: Epoch Transition, Arm Transition, Discontinuation, Early Termination, Rescue Therapy, Dose Modification

## Rules

1. **Wrap every citable scalar field** - every value you extract from the protocol
   (not `id`/`timingType`/`relativeTo`/`unit`/`transitionType`/`exitType`/
   `conditionId`/`conditionIds`/`fromElementId`/`toElementId`/`timepointId`/
   `defaultTransitionId`) must be `{{"value": ..., "page": ..., "quote": ...}}` as
   shown above. Use `page: null, quote: null` only when the value is a reasonable
   default, not something the protocol states.
2. **Return ONLY valid JSON** - no markdown fences, no explanations

PROTOCOL TEXT:
{protocol_text}

Extract all timing constraints, conditions, and transition rules. Focus on quantitative timing information."""


def get_scheduling_prompt(protocol_text: str) -> str:
    """Generate the full prompt for scheduling extraction."""
    MAX_CHARS = 60_000  # Cap to avoid LLM timeouts on large protocols
    text = protocol_text[:MAX_CHARS]
    return SCHEDULING_USER_PROMPT.format(protocol_text=text)


def get_system_prompt() -> str:
    """Get the system prompt for scheduling extraction."""
    return SCHEDULING_SYSTEM_PROMPT
