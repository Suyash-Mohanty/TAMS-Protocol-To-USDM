"""
LLM Prompts for Objectives & Endpoints Extraction.

Split into two focused phases for improved reliability:
1. OBJECTIVES_ENDPOINTS_PROMPT - Extract objectives and endpoints (core, always succeeds)
2. ESTIMANDS_PROMPT - Extract estimands with endpoint context (enhancement phase)

This separation improves reliability by:
- Reducing prompt complexity and output size
- Ensuring core objectives/endpoints always extract successfully
- Allowing estimands to reference already-extracted endpoint IDs
- Making each prompt easier to tune independently

Output format follows USDM v4.0 OpenAPI schema requirements.
"""

# =============================================================================
# PHASE 1: Objectives & Endpoints (Core extraction - always runs)
# =============================================================================

OBJECTIVES_ENDPOINTS_PROMPT = """You are an expert at extracting study objectives and endpoints from clinical trial protocols.
Extract ALL objectives and their associated endpoints. Output must conform to USDM v4.0 schema.

## Study Objectives (by level)
- **Primary**: Main purpose of the study
- **Secondary**: Additional goals (safety, tolerability, etc.)
- **Exploratory**: Hypothesis-generating objectives

## Endpoints (matched to objectives)
- **Primary**: Main outcome measures for primary objectives
- **Secondary**: Supporting outcome measures
- **Exploratory**: Additional exploratory measures

## USDM v4.0 Output Format

### Citation requirement — read before producing output

Every scalar field whose value comes from the protocol text (not a structural field
like `id`, `instanceType`, `endpointIds`, `level`, or `purpose`) MUST be written as an
object with three keys instead of a bare value:
```json
"fieldName": {"value": <the actual value>, "page": <0-indexed page number>, "quote": "<exact sentence or phrase from the protocol that states this value>"}
```
- `page` is the 0-indexed page where you found this specific value.
- `quote` must be copied verbatim from the protocol — not a paraphrase. If the value
  is a reasonable default rather than something the protocol explicitly states, set
  `quote` to `null` and `page` to `null`.
- `id`, `instanceType`, `endpointIds`, `level`, and `purpose` are structural/
  classification fields — write these as bare values, exactly as before — do NOT
  wrap these.

```json
{
  "objectives": [
    {
      "id": "obj_1",
      "name": {"value": "Primary Efficacy Objective", "page": 1, "quote": "Primary Objective"},
      "text": {"value": "To evaluate the efficacy of Drug X compared to placebo", "page": 1, "quote": "To evaluate the efficacy of Drug X compared to placebo in reducing disease severity"},
      "level": {"code": "Primary", "codeSystem": "http://www.cdisc.org/USDM/objectiveLevel", "decode": "Primary Objective"},
      "endpointIds": ["ep_1"],
      "instanceType": "Objective"
    }
  ],
  "endpoints": [
    {
      "id": "ep_1",
      "name": {"value": "Primary Efficacy Endpoint", "page": 1, "quote": "Primary Endpoint"},
      "text": {"value": "Change from baseline in disease severity score at Week 12", "page": 1, "quote": "Change from baseline in disease severity score at Week 12"},
      "level": {"code": "Primary", "codeSystem": "http://www.cdisc.org/USDM/endpointLevel", "decode": "Primary Endpoint"},
      "purpose": "Efficacy",
      "instanceType": "Endpoint"
    }
  ]
}
```

## Level Codes
- Primary, Secondary, Exploratory

## Purpose Values
- Efficacy, Safety, Tolerability, Pharmacokinetic, Pharmacodynamic, Biomarker, QualityOfLife

## Rules
1. Every entity MUST have `id` and `instanceType`
2. Use sequential IDs: obj_1, obj_2; ep_1, ep_2
3. Link objectives to endpoints via `endpointIds` array
4. Extract exact text verbatim from protocol
5. Classify correctly by level
6. Be complete - extract ALL objectives and endpoints
7. Each objective's `endpointIds` lists exactly the endpoints the protocol's objectives/endpoints table places beside that objective - an endpoint belongs to one objective unless the protocol repeats it
8. Only endpoints stated in the protocol - never filler or placeholder entries (e.g. "Placeholder", "see ep_5 through ep_29")
9. **Wrap every citable scalar field** - every field value you extract from the
   protocol (not `id`/`instanceType`/`endpointIds`/`level`/`purpose`) must be
   `{"value": ..., "page": ..., "quote": ...}` as shown above. Use `page: null,
   quote: null` only when the value is a reasonable default, not something the
   protocol states.
10. Return ONLY valid JSON - no markdown, no explanations

Now extract objectives and endpoints from the protocol:
"""

# =============================================================================
# PHASE 2: Estimands (Enhancement - runs after objectives/endpoints)
# =============================================================================

ESTIMANDS_PROMPT = """You are an expert at extracting estimands from clinical trial protocols using the ICH E9(R1) framework.

## Previously Extracted Endpoints
{endpoints_context}

## ICH E9(R1) Estimand Framework

An estimand precisely describes the treatment effect. Extract ALL FIVE attributes:

1. **Treatment** - Intervention AND comparator with specific names
2. **Population** - Target patients AND analysis population (ITT, PP, mITT, etc.)
3. **Variable** - The endpoint being measured (MUST reference endpoint ID from above)
4. **Intercurrent Events** - Events affecting interpretation WITH handling strategy
5. **Summary Measure** - Statistical summary (difference in means, hazard ratio, odds ratio, etc.)

## Intercurrent Event Strategies (MUST specify one)
- **Treatment Policy** - Include all data regardless of event
- **Composite** - Event becomes part of outcome
- **Hypothetical** - Estimate as if event hadn't occurred
- **Principal Stratum** - Subset who wouldn't experience event
- **While on Treatment** - Only data while on treatment

## USDM 4.0 Required Output Format

### Citation requirement — read before producing output

Every scalar field whose value comes from the protocol text (not a structural field
like `id`, `instanceType`, `endpointId`, or `strategy`) MUST be written as an object
with three keys instead of a bare value:
```json
"fieldName": {{"value": <the actual value>, "page": <0-indexed page number>, "quote": "<exact sentence or phrase from the protocol that states this value>"}}
```
- `page` is the 0-indexed page where you found this specific value.
- `quote` must be copied verbatim from the protocol — not a paraphrase. If the value
  is a reasonable default rather than something the protocol explicitly states, set
  `quote` to `null` and `page` to `null`.
- `id`, `instanceType`, `endpointId`, and `strategy` are structural/classification
  fields — write these as bare values, exactly as before — do NOT wrap these.

```json
{{
  "estimands": [
    {{
      "id": "est_1",
      "name": {{"value": "Primary Efficacy Estimand", "page": 5, "quote": "primary estimand"}},
      "populationSummary": {{"value": "Adult patients meeting eligibility criteria", "page": 5, "quote": "all randomized adult patients meeting eligibility criteria"}},
      "analysisPopulation": {{"value": "Intent-to-Treat (ITT) Population", "page": 5, "quote": "Intent-to-Treat (ITT) Population"}},
      "treatmentDescription": {{"value": "Drug X 100mg daily vs Placebo", "page": 5, "quote": "Drug X 100 mg once daily compared with placebo"}},
      "interventionNames": ["Drug X 100mg", "Placebo"],
      "variableOfInterest": {{"value": "Change from baseline in severity score at Week 12", "page": 5, "quote": "change from baseline in severity score at Week 12"}},
      "endpointId": "ep_1",
      "summaryMeasure": {{"value": "Difference in least squares means", "page": 5, "quote": "difference in least-squares means"}},
      "intercurrentEvents": [
        {{
          "id": "ice_1",
          "name": {{"value": "Treatment discontinuation", "page": 5, "quote": "treatment discontinuation"}},
          "text": {{"value": "Subject discontinues study treatment before Week 12", "page": 5, "quote": "subjects who discontinue study treatment before Week 12"}},
          "strategy": "Treatment Policy",
          "instanceType": "IntercurrentEvent"
        }},
        {{
          "id": "ice_2",
          "name": {{"value": "Use of rescue medication", "page": 5, "quote": "use of rescue medication"}},
          "text": {{"value": "Subject uses prohibited rescue medication", "page": 5, "quote": "subjects who use prohibited rescue medication"}},
          "strategy": "Hypothetical",
          "instanceType": "IntercurrentEvent"
        }}
      ],
      "instanceType": "Estimand"
    }}
  ]
}}
```

## CRITICAL Rules
1. **MUST link to endpoint IDs** from Phase 1 using endpointId field
2. **MUST include summaryMeasure** - the statistical method (e.g., "Difference in means", "Hazard ratio")
3. **MUST include at least one intercurrentEvent** with strategy
4. **MUST include analysisPopulation** - the population type (ITT, PP, Safety, etc.)
5. **MUST include interventionNames** - list of intervention names being compared
6. Extract at least one estimand for each primary endpoint
7. Include common intercurrent events (discontinuation, rescue medication) even if not explicit
8. **Wrap every citable scalar field** - every field value you extract from the
   protocol (not `id`/`instanceType`/`endpointId`/`strategy`) must be
   `{{"value": ..., "page": ..., "quote": ...}}` as shown above. Use `page: null,
   quote: null` only when the value is a reasonable default, not something the
   protocol states.
9. Return ONLY valid JSON

Now extract estimands from the protocol:
"""

# =============================================================================
# Legacy prompt (kept for backward compatibility)
# =============================================================================

OBJECTIVES_EXTRACTION_PROMPT = OBJECTIVES_ENDPOINTS_PROMPT

# =============================================================================
# Page finder prompt
# =============================================================================

OBJECTIVES_PAGE_FINDER_PROMPT = """Identify pages containing study objectives and endpoints.

Look for:
1. **Synopsis** - Objectives/endpoints summary table
2. **Objectives section** - Usually Section 2 or 3
3. **Endpoints section** - May be combined or separate
4. **Statistical considerations** - May contain estimand framework

Return JSON:
```json
{
  "objectives_pages": [page_numbers],
  "synopsis_page": page_number,
  "endpoints_pages": [page_numbers],
  "confidence": "high/medium/low"
}
```

Pages are 0-indexed. Return ONLY valid JSON.
"""


# =============================================================================
# Prompt builders
# =============================================================================

def build_objectives_extraction_prompt(protocol_text: str, context_hints: str = "") -> str:
    """Build prompt for Phase 1: objectives and endpoints extraction."""
    MAX_CHARS = 40_000  # Cap to avoid LLM timeouts on large protocols
    text = protocol_text[:MAX_CHARS]
    prompt = OBJECTIVES_ENDPOINTS_PROMPT
    if context_hints:
        prompt += f"\n\nCONTEXT FROM PRIOR EXTRACTION:{context_hints}"
    prompt += f"\n\n---\n\nPROTOCOL CONTENT:\n\n{text}"
    return prompt


def build_estimands_prompt(protocol_text: str, endpoints: list, context_hints: str = "") -> str:
    """Build prompt for Phase 2: estimands extraction with endpoint context."""
    MAX_CHARS = 40_000  # Cap to avoid LLM timeouts on large protocols
    text = protocol_text[:MAX_CHARS]
    # Format endpoints for context
    if endpoints:
        endpoints_lines = []
        for ep in endpoints:
            ep_id = ep.get('id', 'unknown')
            ep_name = ep.get('name', '')
            ep_text = ep.get('text', '')[:100]  # Truncate for brevity
            level = ep.get('level', {})
            level_code = level.get('code', '') if isinstance(level, dict) else str(level)
            endpoints_lines.append(f"- {ep_id}: [{level_code}] {ep_name} - {ep_text}")
        endpoints_context = "\n".join(endpoints_lines)
    else:
        endpoints_context = "No endpoints extracted yet."
    
    prompt = ESTIMANDS_PROMPT.format(endpoints_context=endpoints_context)
    if context_hints:
        prompt += f"\n\nADDITIONAL CONTEXT:{context_hints}"
    prompt += f"\n\n---\n\nPROTOCOL CONTENT:\n\n{text}"
    return prompt


def build_page_finder_prompt() -> str:
    """Build prompt for finding objectives pages."""
    return OBJECTIVES_PAGE_FINDER_PROMPT
