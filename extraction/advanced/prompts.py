"""
LLM Prompts for Advanced Entities Extraction.

These prompts guide the LLM to extract amendments, geographic scope, and sites.
"""

ADVANCED_EXTRACTION_PROMPT = """You are an expert at extracting protocol amendment and geographic information from clinical trial protocols.

Analyze the provided protocol content and extract advanced protocol entities.

## Required Information

### 1. Protocol Amendments (CRITICAL - extract ALL amendments)
Look for the "Protocol Amendment History" section, typically near the end of the document (section 10.x).
Also check the "Protocol Amendment Summary of Changes Table" which may appear earlier in the document.
For EACH amendment in the history, extract:
- Amendment number (e.g., "1", "2", "3", "3.1 (US)")
- `effectiveDate` — date the amendment became effective (ISO 8601 YYYY-MM-DD if possible)
- `approvalDate` — date the amendment was approved/signed (if distinct from effectiveDate; null if unknown)
- **Summary**: The "Overall Rationale for the Amendment" paragraph that describes WHY the amendment was made. **Extract the EXACT text from the protocol — do NOT rephrase, summarize, or paraphrase. Use the original wording verbatim.**
- Previous and new version numbers
- `primaryReason` — the main reason for the amendment, chosen from the CDISC Amendment Reason list below (use the term EXACTLY as written)
- `secondaryReasons` — any additional reasons from the same list (empty list if none)
- `otherReason` — ONLY when primaryReason is "Other": the protocol's own wording of the reason; otherwise null
- `changes` — one entry per row of the amendment's "Summary of Changes" / "Changes to the Protocol" table (see below)

**CDISC Amendment Reason list (C207415)** — pick the term that best matches the stated rationale:
- "New Safety Information Available" — new safety data, safety committee/DMC feedback, updated safety guidance or risk mitigation
- "New Data Available (Other Than Safety Data)" — new efficacy, PK, scientific or nonclinical data
- "New Regulatory Guidance" — new or changed regulations/guidance
- "Regulatory Agency Request To Amend" — a health authority (FDA, EMA, PMDA, ...) asked for the change
- "IRB/IEC Feedback" — ethics committee or IRB requested the change
- "Investigator/Site Feedback" — feedback from investigators or sites
- "Inconsistency and/or Error In The Protocol" — corrections, clarifications, typos, internal inconsistencies
- "Protocol Design Error" — a flaw in the study design itself
- "Change In Strategy" — sponsor's development/operational strategy changed
- "Change In Standard Of Care" — clinical practice or standard of care changed
- "Recruitment Difficulty" — enrollment problems
- "Manufacturing Change" — drug product manufacturing/formulation change
- "IMP Addition" — a new investigational product is added
- "Not Applicable"
- "Other" — none of the above fit; then fill `otherReason`

**IMPORTANT**: Each amendment should have its own summary text. Look for sections like:
- "Overall Rationale for the Amendment"
- "The main reason for preparation of this amendment was..."
- Summary text appears BEFORE the "Changes to the Protocol" table for each amendment

**Amendment changes**: The "Summary of Changes" table usually has the columns "Section # and Name", "Description of Change" and "Brief Rationale". Create one `changes` entry per table row:
- `sectionNumber` — the section number only (e.g., "5.2"); use "Multiple" if the row covers several sections
- `sectionTitle` — the section name (e.g., "Exclusion Criteria")
- `description` — the "Description of Change" text, VERBATIM; if a row's text continues onto the next page, join it into one entry
- `rationale` — the "Brief Rationale" text, VERBATIM
If the protocol has no changes table for an amendment, return an empty `changes` list — do NOT invent changes.

**CRITICAL**: Do NOT skip Amendment 1. Many protocols have an "Amendment 1" (or "Protocol Amendment 1") that is the first change from the original protocol. If the Protocol Amendment Summary of Changes Table lists Amendment 1 with a date and summary, you MUST include it. Start from the very first amendment listed.

### 2. Geographic Scope
- List of participating countries
- Regions (if mentioned)
- Number of planned sites (if mentioned)

### 3. Study Sites (if listed)
- Site names or numbers
- City and country

## Output Format

Return a JSON object with this exact structure:

```json
{
  "amendments": [
    {
      "number": "1",
      "effectiveDate": "2020-06-15",
      "approvalDate": "2020-06-01",
      "summary": "The main reason for preparation of this amendment was to update procedures outlined in the Schedule of Activities, remove contradictory text on the reporting of serious adverse events, and add details of an interim analysis.",
      "previousVersion": "Original Protocol",
      "newVersion": "1",
      "primaryReason": "Inconsistency and/or Error In The Protocol",
      "secondaryReasons": ["Change In Strategy"],
      "otherReason": null,
      "changes": [
        {
          "sectionNumber": "1.3",
          "sectionTitle": "Schedule of Activities",
          "description": "Added an ECG assessment at Visit 4.",
          "rationale": "Alignment with safety monitoring plan."
        },
        {
          "sectionNumber": "8.3.1",
          "sectionTitle": "Time Period and Frequency for Collecting AE and SAE Information",
          "description": "Removed contradictory text on SAE reporting timelines.",
          "rationale": "Correction of inconsistency."
        }
      ]
    },
    {
      "number": "2",
      "effectiveDate": "2021-03-19",
      "approvalDate": null,
      "summary": "The main reason for preparation of this amendment was to revise the exclusion criterion for a urine drug screen and incorporate COVID vaccination guidance.",
      "previousVersion": "1",
      "newVersion": "2",
      "primaryReason": "Regulatory Agency Request To Amend",
      "secondaryReasons": ["New Safety Information Available"],
      "otherReason": null,
      "changes": [
        {
          "sectionNumber": "5.2",
          "sectionTitle": "Exclusion Criteria",
          "description": "Revised exclusion criterion #12 for urine drug screen.",
          "rationale": "Per FDA request."
        }
      ]
    }
  ],
  "geographicScope": {
    "type": "Global",
    "countries": [
      {"name": "United States", "code": "US"},
      {"name": "Germany", "code": "DE"}
    ],
    "regions": ["North America", "Europe"],
    "plannedSites": 20
  },
  "sites": []
}
```

## Rules

1. **Extract ALL amendments** - There may be 3-10+ amendments in a protocol. Start from Amendment 1 (do NOT skip it).
2. **Amendment summaries are REQUIRED** - Look for "Overall Rationale" or "main reason" text. Copy the text VERBATIM from the protocol — do not rephrase.
3. **Check amendment history section** - Usually in Section 10.x near end of document
4. **Check title page** - May contain current version and date
5. **Standard country codes** - Use ISO 3166-1 alpha-2 codes when possible
6. **Amendment reasons** - primaryReason/secondaryReasons MUST be terms from the CDISC Amendment Reason list above, spelled exactly
7. **Amendment changes** - one entry per row of the Summary of Changes table, text copied verbatim; empty list if there is no table
8. **Return ONLY valid JSON** - no markdown, no explanations

Now analyze the protocol content and extract the advanced entities:
"""


def build_advanced_extraction_prompt(protocol_text: str) -> str:
    """Build the full extraction prompt with protocol content."""
    MAX_CHARS = 60_000  # Cap to avoid LLM timeouts on large protocols
    if len(protocol_text) <= MAX_CHARS:
        text = protocol_text
    else:
        # Keep both head (amendment summary table, title page) and tail
        # (amendment history section near end of document).
        # Head must be large enough to capture the full amendment summary
        # table which can span 10+ pages in protocols with many amendments.
        head_size = 20_000
        tail_size = MAX_CHARS - head_size  # 40_000
        text = (
            protocol_text[:head_size]
            + "\n\n[... middle of document omitted for brevity ...]\n\n"
            + protocol_text[-tail_size:]
        )
    return f"{ADVANCED_EXTRACTION_PROMPT}\n\n---\n\nPROTOCOL CONTENT:\n\n{text}"
