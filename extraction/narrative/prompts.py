"""
LLM Prompts for Document Structure & Narrative Extraction.

These prompts guide the LLM to extract document structure and abbreviations.
"""

ABBREVIATIONS_EXTRACTION_PROMPT = """You are an expert at extracting abbreviations from clinical trial protocols.

Analyze the provided protocol content and extract ALL abbreviations and their definitions.

## Required Information

Extract abbreviations from:
1. **Abbreviations list/table** - Usually near the beginning of the protocol
2. **In-text definitions** - First use with expansion in parentheses
3. **Common clinical abbreviations** - ECG, BP, HbA1c, etc.

### Citation requirement — read before producing output

Every scalar field whose value comes from the protocol text MUST be written as an
object with three keys instead of a bare value:
```json
"fieldName": {"value": <the actual value>, "page": <0-indexed page number>, "quote": "<exact sentence or phrase from the protocol that states this value>"}
```
- `page` is the 0-indexed page number where you found this specific value.
- `quote` must be copied verbatim from the protocol — not a paraphrase. If you cannot
  find a specific supporting quote, set `quote` to `null` and `page` to `null` rather
  than guessing.

## Output Format

Return a JSON object with this exact structure:

```json
{
  "abbreviations": [
    {
      "abbreviation": {"value": "ECG", "page": 7, "quote": "ECG Electrocardiogram"},
      "expansion": {"value": "Electrocardiogram", "page": 7, "quote": "ECG Electrocardiogram"}
    },
    {
      "abbreviation": {"value": "HbA1c", "page": 7, "quote": "HbA1c Glycated Hemoglobin"},
      "expansion": {"value": "Glycated Hemoglobin", "page": 7, "quote": "HbA1c Glycated Hemoglobin"}
    },
    {
      "abbreviation": {"value": "ICF", "page": 7, "quote": "ICF Informed Consent Form"},
      "expansion": {"value": "Informed Consent Form", "page": 7, "quote": "ICF Informed Consent Form"}
    }
  ]
}
```

## Rules

1. **Extract exact text** - Use the expansion as written in the protocol
2. **Include all abbreviations** - Even common ones like BP, HR, etc.
3. **Handle variations** - "ECG/EKG" should be separate entries
4. **Case sensitive** - Preserve original case (HbA1c not HBAIC)
5. **Wrap every citable scalar field** - both `abbreviation` and `expansion` must be
   `{"value": ..., "page": ..., "quote": ...}` as shown above.
6. **Return ONLY valid JSON** - no markdown, no explanations

Now analyze the protocol content and extract the abbreviations:
"""


STRUCTURE_EXTRACTION_PROMPT = """You are an expert at extracting document structure from clinical trial protocols.

Analyze the provided protocol content and extract the section structure.

## Required Information

### 1. Document Information
- Protocol title
- Version number
- Version date
- Document language — use the language explicitly stated on the title/cover page if present (e.g., "Language: French"). If it is not stated, detect it yourself from the actual protocol content provided below and report that language (e.g., "French", "German", "Japanese") — do not assume English
- Template/authoring name (e.g., "Sponsor", "ICH", a CRO name — only if explicitly stated on the title/cover page)

### 2. Major Sections
For each section extract:
- Section number (e.g., "1", "2.1", "5.1.2")
- Section title
- Section type (Synopsis, Objectives, Study Design, Eligibility, Treatment, etc.)

### Citation requirement — read before producing output

Every scalar field whose value comes from the protocol text (not a structural field
like `number` or `type`) MUST be written as an object with three keys instead of a
bare value:
```json
"fieldName": {"value": <the actual value>, "page": <0-indexed page number>, "quote": "<exact sentence or phrase from the protocol that states this value>"}
```
- `page` is the 0-indexed page number where you found this specific value.
- `quote` must be copied verbatim from the protocol — not a paraphrase. If you cannot
  find a specific supporting quote (e.g. a section title taken straight from the TOC
  with no distinctive sentence), set `quote` to `null` and `page` to `null` rather
  than guessing.
- `number` and `type` are structural/linking fields and stay bare — do NOT wrap those.

## Output Format

Return a JSON object with this exact structure:

```json
{
  "document": {
    "title": {"value": "A Phase 2, Open-Label Study...", "page": 0, "quote": "A Phase 2, Open-Label Study of..."},
    "version": {"value": "3.0", "page": 0, "quote": "Version 3.0"},
    "versionDate": {"value": "2020-06-15", "page": 0, "quote": "15 June 2020"},
    "language": {"value": "English", "page": null, "quote": null},
    "templateName": {"value": "Sponsor", "page": 0, "quote": "Sponsor Protocol Template"}
  },
  "sections": [
    {
      "number": "1",
      "title": {"value": "Introduction", "page": 2, "quote": "1. INTRODUCTION"},
      "type": "Introduction"
    },
    {
      "number": "2",
      "title": {"value": "Study Objectives", "page": 3, "quote": "2. STUDY OBJECTIVES"},
      "type": "Objectives"
    },
    {
      "number": "3",
      "title": {"value": "Study Design", "page": 4, "quote": "3. STUDY DESIGN"},
      "type": "Study Design",
      "subsections": [
        {"number": "3.1", "title": {"value": "Overview of Study Design", "page": 4, "quote": "3.1. Overview of Study Design"}},
        {"number": "3.2", "title": {"value": "Rationale for Study Design", "page": 5, "quote": "3.2. Rationale for Study Design"}}
      ]
    }
  ]
}
```

## Section Types
Use these standard types:
- Synopsis
- Introduction
- Objectives
- Study Design
- Study Population
- Eligibility Criteria
- Treatment
- Study Procedures
- Assessments
- Safety
- Statistics
- Ethics
- References
- Appendix
- Other

## Rules

1. **Extract from TOC** - Use table of contents if available
2. **Include all levels** - Main sections and subsections
3. **Preserve numbering** - Keep original section numbers
4. **Wrap every citable scalar field** - every field value you extract from the
   protocol (not `number`/`type`) must be `{"value": ..., "page": ..., "quote": ...}`
   as shown above. Use `page: null, quote: null` only when no specific supporting
   quote is available.
5. **Return ONLY valid JSON** - no markdown, no explanations

Now analyze the protocol content and extract the structure:
"""


def build_abbreviations_extraction_prompt(protocol_text: str) -> str:
    """Build the full extraction prompt with protocol content."""
    MAX_CHARS = 40_000  # Cap to avoid LLM timeouts on large protocols
    text = protocol_text[:MAX_CHARS]
    return f"{ABBREVIATIONS_EXTRACTION_PROMPT}\n\n---\n\nPROTOCOL CONTENT:\n\n{text}"


def build_structure_extraction_prompt(protocol_text: str) -> str:
    """Build the full extraction prompt with protocol content."""
    MAX_CHARS = 40_000  # Cap to avoid LLM timeouts on large protocols
    text = protocol_text[:MAX_CHARS]
    return f"{STRUCTURE_EXTRACTION_PROMPT}\n\n---\n\nPROTOCOL CONTENT:\n\n{text}"
