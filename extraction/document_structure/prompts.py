"""
LLM Prompts for Document Structure extraction.
Phase 12: DocumentContentReference, CommentAnnotation, StudyDefinitionDocumentVersion
"""

DOCUMENT_STRUCTURE_SYSTEM_PROMPT = """You are an expert clinical protocol analyst specializing in document structure and cross-references.

Your task is to extract:
1. Cross-references between protocol sections
2. Footnotes and annotations
3. Document version information

Return valid JSON only."""

DOCUMENT_STRUCTURE_USER_PROMPT = """Extract Document Structure information from the following protocol text.

**Document Content References to extract:**
- Cross-references to other sections (e.g., "See Section 5.2")
- References to tables, figures, appendices
- Internal links between protocol components

**Comment Annotations to extract:**
- Footnotes (marked with *, †, ‡, numbers, or letters)
- Notes and clarifications
- Important comments in margins or boxes

**Document Version Info to extract:**
- Protocol version number
- Version date
- Amendment numbers if applicable
- Document status (Draft, Final, Approved)

### Citation requirement — read before producing output

Every scalar field whose value comes from the protocol text (not a structural field
like `id`, `sectionNumber`, `targetId`, or `annotationType`/`status` codes) MUST be
written as an object with three keys instead of a bare value:
```json
"fieldName": {{"value": <the actual value>, "page": <0-indexed page number>, "quote": "<exact sentence or phrase from the protocol that states this value>"}}
```
- `page` is the 0-indexed page number where you found this specific value.
- `quote` must be copied verbatim from the protocol — not a paraphrase. If you cannot
  find a specific supporting quote, set `quote` to `null` and `page` to `null` rather
  than guessing.
- `id`, `sectionNumber`, `targetId`, `annotationType`, and `status` are structural/
  linking fields and stay bare — do NOT wrap those.

Return JSON in this exact format:
```json
{{
  "contentReferences": [
    {{
      "id": "ref_1",
      "name": {{"value": "Eligibility Reference", "page": 10, "quote": "See Section 5.2 for exclusion criteria"}},
      "sectionNumber": "5.2",
      "sectionTitle": {{"value": "Exclusion Criteria", "page": 10, "quote": "5.2. Exclusion Criteria"}},
      "description": {{"value": "Reference to exclusion criteria from inclusion section", "page": 10, "quote": "See Section 5.2 for exclusion criteria"}}
    }}
  ],
  "annotations": [
    {{
      "id": "annot_1",
      "text": {{"value": "Subjects must fast for at least 8 hours prior to PK sampling", "page": 15, "quote": "*Subjects must fast for at least 8 hours prior to PK sampling"}},
      "annotationType": "Footnote",
      "sourceSection": {{"value": "Schedule of Activities", "page": 15, "quote": "Schedule of Activities"}},
      "pageNumber": 15
    }}
  ],
  "documentVersions": [
    {{
      "id": "ver_1",
      "versionNumber": {{"value": "4.0", "page": 0, "quote": "Version 4.0"}},
      "versionDate": {{"value": "2020-06-15", "page": 0, "quote": "15 June 2020"}},
      "status": "Final",
      "amendmentNumber": {{"value": "Amendment 3", "page": 0, "quote": "Amendment 3"}},
      "description": {{"value": "Protocol Amendment 3 incorporating regulatory feedback", "page": 0, "quote": "incorporating regulatory feedback"}}
    }}
  ]
}}
```

Valid annotationType values: Footnote, Comment, Note, Clarification, Reference
Valid status values: Draft, Final, Approved

PROTOCOL TEXT:
{protocol_text}

Extract all cross-references, footnotes/annotations, and version information.
Wrap every citable scalar field as shown above (`name`, `sectionTitle`, `description`,
`text`, `sourceSection`, `versionNumber`, `versionDate`, `amendmentNumber`); leave
`id`, `sectionNumber`, `targetId`, `pageNumber`, `annotationType`, and `status` as
bare values."""


def get_document_structure_prompt(protocol_text: str) -> str:
    """Generate the full prompt for document structure extraction."""
    MAX_CHARS = 40_000  # Cap to avoid LLM timeouts on large protocols
    text = protocol_text[:MAX_CHARS]
    return DOCUMENT_STRUCTURE_USER_PROMPT.format(protocol_text=text)


def get_system_prompt() -> str:
    """Get the system prompt for document structure extraction."""
    return DOCUMENT_STRUCTURE_SYSTEM_PROMPT
