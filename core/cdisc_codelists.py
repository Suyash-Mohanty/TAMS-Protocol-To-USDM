"""
Local CDISC controlled-terminology lookup.

Resolves free text (e.g. "g", "Tablet", "Crossover") to a term of a specific
CDISC codelist using the official codelists in
core/schema_cache/cdisc_codelists.json (built by
tools/build_cdisc_codelists.py). Matching is exact on the codelist's own
submission values, preferred terms and synonyms — never a "best guess" — so
an unmatched value returns None and the caller decides the fallback.
"""

import json
import re
from itertools import combinations
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

_CODELISTS_FILE = Path(__file__).resolve().parent / "schema_cache" / "cdisc_codelists.json"

UNIT = "C71620"
DOSE_FORM = "C66726"
INTERVENTION_MODEL = "C99076"
INTERVENTION_TYPE = "C99078"
STUDY_INTERVENTION_ROLE = "C207417"
PRODUCT_DESIGNATION = "C207418"
ROUTE = "C66729"
FREQUENCY = "C71113"


@lru_cache(maxsize=1)
def _codelists() -> Dict[str, dict]:
    with open(_CODELISTS_FILE, encoding="utf-8") as f:
        return json.load(f)


def codelist_terms(codelist_id: str) -> List[dict]:
    """All terms ({code, decode, submissionValue, synonyms}) of a codelist."""
    return (_codelists().get(codelist_id) or {}).get("terms", [])


def _norm(text: str) -> str:
    text = str(text).replace("µ", "u").replace("μ", "u")  # micro sign / Greek mu
    return re.sub(r"\s+", " ", text).strip().lower()


def _singular(text: str) -> str:
    return text[:-1] if len(text) > 3 and text.endswith("s") and not text.endswith("ss") else text


_FILLER_WORDS = {"for", "of", "and", "with", "the", "a", "an"}


def _word_key(text: str) -> frozenset:
    """Order/punctuation-insensitive key: "Film-coated tablets" == "TABLET, FILM COATED",
    "Solution for injection" == "INJECTION, SOLUTION"."""
    return frozenset(_singular(w) for w in re.findall(r"[a-z0-9]+", _norm(text)) if w not in _FILLER_WORDS)


def _compact(text: str) -> str:
    """Punctuation-insensitive key: "Crossover" == "CROSS-OVER"."""
    return re.sub(r"[^a-z0-9/%]", "", _norm(text))


def _term_texts(term: dict) -> List[str]:
    return [t for t in [term.get("submissionValue"), term.get("decode"), *term.get("synonyms", [])] if t]


def lookup(codelist_id: str, text: Optional[str], allow_broader: bool = False) -> Optional[dict]:
    """Find the codelist term matching `text`, or None.

    Order: exact submission value (case-sensitive, so unit "g" is Gram and
    not "G"), then case-insensitive submission value, preferred term,
    synonym, NCI code, the same with a trailing plural "s" removed
    ("Tablets" -> "Tablet"), then word-order/punctuation-insensitive matches
    ("Film-coated tablet" -> "TABLET, FILM COATED", "Crossover" ->
    "CROSS-OVER").

    allow_broader: when nothing matches, accept the term whose submission
    value is the longest run of the text's own words ("nasal powder" ->
    "POWDER"). Less specific but still correct; use only for codelists
    where a broader term is acceptable (e.g. dose forms).
    """
    if text is None or not str(text).strip():
        return None
    raw = re.sub(r"\s+", " ", str(text)).strip()
    terms = codelist_terms(codelist_id)

    for term in terms:
        if term.get("submissionValue") == raw:
            return term

    for candidate in dict.fromkeys([_norm(raw), _singular(_norm(raw))]):
        for term in terms:
            if _norm(term.get("submissionValue") or "") == candidate:
                return term
        for term in terms:
            if _norm(term.get("decode") or "") == candidate:
                return term
        for term in terms:
            if any(_norm(s) == candidate for s in term.get("synonyms", [])):
                return term
        for term in terms:
            if term.get("code", "").lower() == candidate:
                return term

    key, compact = _word_key(raw), _compact(raw)
    for term in terms:
        if any(_word_key(t) == key for t in _term_texts(term)):
            return term
    for term in terms:
        if compact and any(_compact(t) == compact for t in _term_texts(term)):
            return term

    if allow_broader:
        words = [w for w in re.findall(r"[a-z0-9]+", _norm(raw)) if w not in _FILLER_WORDS]
        # Largest subset of the text's words first, not only adjacent runs:
        # "solution for SC injection" -> {solution, injection} -> INJECTION, SOLUTION
        words = words[:8]
        for size in range(len(words) - 1, 0, -1):
            for run in combinations(words, size):
                run = list(run)
                sub_key = frozenset(_singular(w) for w in run)
                matches = [t for t in terms if _word_key(t.get("submissionValue") or "") == sub_key]
                if matches:
                    # Prefer the term that is literally these words ("SOLUTION")
                    # over one that only shares them once fillers are ignored
                    # ("FOR SOLUTION")
                    literal = " ".join(run)
                    return next((t for t in matches if _norm(t.get("submissionValue") or "") == literal), matches[0])
    return None


def term_by_code(codelist_id: str, code: str) -> Optional[dict]:
    """The term with NCI code `code` in the codelist, or None."""
    return next((t for t in codelist_terms(codelist_id) if t.get("code") == code), None)


def codelist_for(instance_type: str, attribute: str) -> Optional[str]:
    """The codelist governing `instance_type.attribute` (e.g.
    StudyDefinitionDocumentVersion.status -> C188723), or None."""
    return ((_codelists().get("_attributes") or {}).get(instance_type) or {}).get(attribute)


def effective_date(codelist_id: str) -> Optional[str]:
    return (_codelists().get(codelist_id) or {}).get("effectiveDate")


CDISC_CODE_SYSTEM = "http://www.cdisc.org"


def to_code(term: dict, codelist_id: str) -> dict:
    """Code fields for a codelist term. The decode is the CDISC submission
    value ("Approved", "Protocol", "g"), as in CDISC's own USDM output."""
    return {
        "code": term["code"],
        "decode": term.get("submissionValue") or term.get("decode"),
        "codeSystem": CDISC_CODE_SYSTEM,
        "codeSystemVersion": effective_date(codelist_id) or "",
    }


def conform_code(code_obj: dict, codelist_id: str) -> Optional[bool]:
    """Make a USDM Code dict use a term of `codelist_id`, in place.

    A code already in the codelist is left as is. Otherwise the term is
    re-resolved from the decode, then the code text, by exact match only
    (no broader-term guess). Returns True if changed, False if already
    valid, None if no codelist term matches (left unchanged).
    """
    if not isinstance(code_obj, dict) or not codelist_terms(codelist_id):
        return None
    if term_by_code(codelist_id, code_obj.get("code") or ""):
        return False
    term = lookup(codelist_id, code_obj.get("decode")) or lookup(codelist_id, code_obj.get("code"))
    if not term:
        return None
    code_obj.update(to_code(term, codelist_id))
    return True
