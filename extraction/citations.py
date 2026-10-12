"""
Shared helpers for per-field citations (page + verbatim quote).

Every extraction module's prompt asks the LLM to wrap citable scalar fields as
    {"value": <actual value>, "page": <0-indexed page>, "quote": "<exact protocol text>"}
instead of a bare value, so each field's source can be traced back to the
protocol document. These helpers unwrap that shape for the extractor's normal
dataclass-building code, and separately collect the page/quote data into a
per-entity citations dict that flows through agents/extraction/<module>_agent.py
-> ContextStore -> ProvenanceAgent -> the final <protocol>_citations.json
sidecar file (see agents/support/provenance_agent.py).

Piloted on extraction/eligibility/; this module exists so the same unwrap/
collect logic isn't copy-pasted into every extractor.py as the pattern rolls
out to the other extraction modules.
"""

from typing import Any, Dict, Optional


def unwrap(field_val: Any, default: Any = None) -> Any:
    """Pull .value out of a {"value", "page", "quote"} citation wrapper.

    Tolerates a bare scalar/list/dict if the LLM didn't wrap it (older
    prompt format, or the model ignoring the wrapping instruction), so
    extraction never breaks just because a citation is missing.
    """
    if isinstance(field_val, dict) and 'value' in field_val:
        return field_val.get('value', default)
    return field_val if field_val is not None else default


def citation(field_val: Any) -> Optional[Dict[str, Any]]:
    """Pull {"page", "quote"} out of a citation-wrapped field, or None."""
    if isinstance(field_val, dict) and ('page' in field_val or 'quote' in field_val):
        page = field_val.get('page')
        quote = field_val.get('quote')
        if page is None and quote is None:
            return None
        return {"page": page, "quote": quote}
    return None


def collect_citation(citations: Dict[str, Dict[str, Dict[str, Any]]],
                      entity_id: str, field_name: str, field_val: Any) -> None:
    """Record field_val's citation under citations[entity_id][field_name], if present."""
    cite = citation(field_val)
    if cite:
        citations.setdefault(entity_id, {})[field_name] = cite
