"""Matching of generated USDM items to the SDR items they describe.

Items are paired in layers: exact key, fuzzy key, (for structural classes) position.
Each class decides what identifies an item; everything is schema-driven, nothing is
protocol specific.
"""
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from .text import norm, similarity, strip_markup

# classes whose whole value is kept as is when SDR already has it
ATOMIC = {"Code", "AliasCode", "Quantity", "Range", "Duration", "Address", "ResponseCode"}

# single containers: a lone generated item is the lone SDR item
SINGLE = {
    "StudyVersion", "InterventionalStudyDesign", "ObservationalStudyDesign",
    "StudyDefinitionDocument", "StudyDesignPopulation", "Masking",
}
# classes whose unmatched leftovers pair by position when the counts agree
POSITIONAL = {"Encounter", "StudyArm", "StudyEpoch"}

# per-class thresholds for a fuzzy match (default FUZZY)
FUZZY = 0.8
THRESHOLDS = {"EligibilityCriterionItem": 0.85, "NarrativeContentItem": 0.9, "Objective": 0.8, "Endpoint": 0.8}
# coded names that differ by a suffix (LBORRES / LBORRESU) are different items: exact keys only
NO_FUZZY = {"BiomedicalConceptProperty"}
# below this an unmatched item counts as new; between it and the threshold it is a possible duplicate
NEW_BELOW = 0.6

_KEY_FIELDS = ("name", "label", "text", "abbreviatedText", "version", "versionIdentifier")


def _code_key(value: Any) -> str:
    if isinstance(value, dict):
        return norm(value.get("code") or value.get("decode"))
    return ""


def _visit_sig(text: Any) -> str:
    """'P1 DAY -1' and 'Period 1, Day -1' both become 'p1d-1'."""
    s = strip_markup(text).lower()
    s = re.sub(r"period\s*", "p", s)
    s = re.sub(r"day\s*", "d", s)
    return re.sub(r"[^a-z0-9\-]", "", s)


_VISIT_NO = re.compile(r"^\s*(?:visit|v)?\s*(\d+)(?!\s*day)", re.I)


def _strip_dot(s: Any) -> str:
    return str(s or "").strip().rstrip(".").lower()


def keys_of(item: Dict[str, Any], cls: str, idmap: Dict[str, str]) -> List[str]:
    """Normalised identifying strings of an item (any shared string is a match)."""
    if cls == "StudyAmendment":
        return [f"n{_strip_dot(item.get('number'))}"] if item.get("number") else []
    if cls == "NarrativeContent":
        keys = [f"s{_strip_dot(item.get('sectionNumber'))}"] if item.get("sectionNumber") else []
        keys += [norm(item.get("sectionTitle") or item.get("name"))]
        return [k for k in keys if k]
    if cls == "StudyIdentifier":
        return [norm(item.get("text"))]
    if cls == "StudyTitle":
        return [k for k in (_code_key(item.get("type")), norm(item.get("text"))) if k]
    if cls == "GovernanceDate":
        return [_code_key(item.get("type")) + norm(item.get("dateValue"))]
    if cls == "GeographicScope":
        code = item.get("code") if isinstance(item.get("code"), dict) else {}
        return [_code_key(item.get("type")) + norm((code.get("standardCode") or {}).get("code") if isinstance(code.get("standardCode"), dict) else "")]
    if cls == "StudyRole":
        return [norm(item.get("name")), _code_key(item.get("code"))]
    if cls == "Abbreviation":
        return [norm(item.get("abbreviatedText"))]
    if cls == "StudyCell":
        return [f"{idmap.get(item.get('armId'), item.get('armId'))}|{idmap.get(item.get('epochId'), item.get('epochId'))}"]
    if cls == "EligibilityCriterion":
        cid = item.get("criterionItemId")
        return [str(idmap.get(cid, cid))] if cid else []
    if cls == "Masking":
        return []
    keys = [norm(item.get(f)) for f in _KEY_FIELDS if item.get(f)]
    if cls in ("Encounter", "StudyEpoch"):
        keys += [_visit_sig(item.get(f)) for f in ("name", "label") if item.get(f)]
        for f in ("name", "label"):
            m = _VISIT_NO.match(str(item.get(f) or ""))
            if m and cls == "Encounter":
                keys.append(f"visit#{int(m.group(1))}")     # '1', 'V1 (Week -5)', 'Visit 1 (Screening)'
    return [k for k in keys if k]


def best_candidate(item: Dict[str, Any], cands: List[Dict[str, Any]], cls: str,
                   idmap: Dict[str, str]) -> Tuple[Optional[Dict[str, Any]], float]:
    """Most similar candidate and its score (1.0 exact key, else text similarity)."""
    mine = keys_of(item, cls, idmap)
    best, score = None, 0.0
    for cand in cands:
        theirs = keys_of(cand, cls, idmap)
        if set(mine) & set(theirs):
            return cand, 1.0
        for a in _fuzzy_texts(item, cls):
            for b in _fuzzy_texts(cand, cls):
                sc = similarity(a, b)
                if sc > score:
                    best, score = cand, sc
    return best, score


def _fuzzy_texts(item: Dict[str, Any], cls: str) -> List[str]:
    if cls in ("StudyCell", "EligibilityCriterion", "StudyIdentifier", "GovernanceDate", "GeographicScope",
               "StudyTitle", "StudyAmendment", "Masking"):
        return []
    if cls in NO_FUZZY:
        return []
    fields = ("name", "label", "text", "abbreviatedText", "sectionTitle") if cls != "Abbreviation" else ("abbreviatedText",)
    out = [str(item[f]) for f in fields if item.get(f)]
    # long free text stays comparable; names stay short
    return [t for t in out if len(t) <= 800]


def threshold(cls: str) -> float:
    return THRESHOLDS.get(cls, FUZZY)
