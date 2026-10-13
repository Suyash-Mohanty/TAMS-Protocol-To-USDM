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


def _norm_text(text: Any) -> str:
    """Lower-case letters and digits only, so line breaks, bullets and spacing don't matter."""
    import re
    return re.sub(r"[^a-z0-9]+", "", str(text or "").lower())


def verify_citation_pages(citations_data: Dict[str, Any], pdf_path: str) -> Dict[str, int]:
    """Set each citation's page (0-indexed) to the PDF page its quote is actually on.

    The page the model reports is read from page labels in the text it was given, so it can be
    off (e.g. 1-based labels against the 0-indexed convention) or simply wrong. The quote is
    looked up in the PDF; where it occurs on several pages, the one nearest the reported page
    wins. A quote that can't be found keeps the reported page. Modifies citations_data in place.
    """
    import fitz

    with fitz.open(pdf_path) as doc:
        pages = [_norm_text(page.get_text()) for page in doc]
    stats = {"checked": 0, "corrected": 0, "confirmed": 0, "not_found": 0, "adjusted_from_sibling": 0}
    for entry in (citations_data.get("citations") or {}).values():
        unresolved = []          # (cite, reported page) not locatable on their own
        shifts = {}              # reported page -> verified page, within this item
        for cite in _iter_citations(entry.get("fields") or {}):
            reported = cite.get("page") if isinstance(cite.get("page"), int) else None
            quote = _norm_text(cite.get("quote"))
            if len(quote) < 4:
                unresolved.append((cite, reported))
                continue
            stats["checked"] += 1
            probe = quote[:80]
            hits = [i for i, text in enumerate(pages) if probe in text]
            if not hits and len(quote) > 40:
                probe = quote[:40]
                hits = [i for i, text in enumerate(pages) if probe in text]
            if not hits:
                stats["not_found"] += 1
                unresolved.append((cite, reported))
                continue
            best = min(hits, key=lambda i: abs(i - reported)) if reported is not None else hits[0]
            if reported is not None:
                shifts.setdefault(reported, best)
            if best == reported:
                stats["confirmed"] += 1
            else:
                cite["page"] = best
                stats["corrected"] += 1
        # a short quote ("1.") or one not found sits where the item's other quotes from the
        # same reported page were verified to be
        for cite, reported in unresolved:
            if reported in shifts and shifts[reported] != reported:
                cite["page"] = shifts[reported]
                stats["adjusted_from_sibling"] += 1
    return stats


def _iter_citations(fields: Dict[str, Any]):
    """{page, quote} dicts, including nested ones (e.g. plannedAge.minValue)."""
    for value in fields.values():
        if isinstance(value, dict):
            if "quote" in value or "page" in value:
                yield value
            else:
                yield from _iter_citations(value)
