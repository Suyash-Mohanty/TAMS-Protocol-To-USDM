"""Coverage report of the reference mandatory-field list against a merged USDM.

The list (core/schema_cache/mandatory_fields.json, exported from the business Excel by
tools/build_mandatory_fields.py) is a reference for the report only; it never steers the merge.
"""
import collections
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .merger import Merger

FIELDS_FILE = Path(__file__).resolve().parent.parent / "core" / "schema_cache" / "mandatory_fields.json"


def load_fields(path: Optional[Path] = None) -> List[Dict[str, Any]]:
    return json.loads((path or FIELDS_FILE).read_text(encoding="utf-8"))


def _populated(v: Any) -> bool:
    return v not in (None, "", [], {})


def _nodes(doc: Any) -> Dict[str, List[Dict[str, Any]]]:
    out: Dict[str, List[Dict[str, Any]]] = collections.defaultdict(list)

    def walk(o):
        if isinstance(o, dict):
            if o.get("instanceType"):
                out[o["instanceType"]].append(o)
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(doc)
    return out


def pdf_text(pdf_path: Optional[str]) -> str:
    if not pdf_path or not Path(pdf_path).exists():
        return ""
    try:
        import fitz
        with fitz.open(pdf_path) as doc:
            return "\n".join(page.get_text() for page in doc)
    except Exception:
        return ""


# 'cohort' as a study group (Cohort A, cohort 2, expansion cohort, enrolled/assigned cohort), not the
# epidemiology 'cohort study' cited in a protocol's background
_STUDY_COHORT = re.compile(
    r"\bcohorts?\s+(?:[A-Z]\b|\d+\b|[IVX]+\b)"
    r"|\b(?:expansion|dose[- ]escalation|sentinel|extension)\s+cohorts?\b"
    r"|\bcohorts?\b[^.]{0,60}\b(?:enrol\w*|assign\w*|randomi\w*|will\s+be\s+dosed)\b"
    r"|\b(?:enrol\w*|assign\w*|randomi\w*)\b[^.]{0,60}\bcohorts?\b")

# a mandatory field can be legitimately absent when the protocol has no such content
_NA_RULES = {
    "Cohort": (lambda t: not _STUDY_COHORT.search(t), "protocol describes no study cohorts"),
    "Blinding": (lambda t: not re.search(r"double[- ]blind|single[- ]blind|\bblinded\b|masked", t, re.I)
                 or re.search(r"open[- ]label", t, re.I) and not re.search(r"double[- ]blind|single[- ]blind", t, re.I),
                 "open-label protocol, no blinding"),
    "Range": (lambda t: not re.search(r"\b\d+\s*(?:to|-|–|and)\s*\d+\s*(?:years|yrs)", t, re.I),
              "protocol states no closed numeric range"),
    "Amendment": (lambda t: not re.search(r"(summary|overview|description)\s+of\s+(the\s+)?(changes|amendment)|amendment\s+summary", t, re.I),
                  "protocol has no amendment"),
    "Amendment change": (lambda t: not re.search(r"(summary|overview|description)\s+of\s+(the\s+)?(changes|amendment)|amendment\s+summary", t, re.I),
                         "protocol has no amendment"),
    "Amendment reason": (lambda t: not re.search(r"(summary|overview|description)\s+of\s+(the\s+)?(changes|amendment)|amendment\s+summary", t, re.I),
                         "protocol has no amendment"),
}


def coverage(merged: Dict[str, Any], sdr: Dict[str, Any], merger: Merger, text: str = "",
             fields: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    fields = fields if fields is not None else load_fields()
    m_nodes, s_nodes = _nodes(merged), _nodes(sdr)
    s_pop: Dict[str, Set[str]] = collections.defaultdict(set)      # field -> ids of SDR nodes holding it
    for nodes in s_nodes.values():
        for n in nodes:
            for k, v in n.items():
                if _populated(v) and not isinstance(v, (dict, list)) or (isinstance(v, (dict, list)) and _populated(v)):
                    s_pop[k].add(str(n.get("id")))
    rows = []
    for f in fields:
        inst = [n for c in f["classes"] for n in m_nodes.get(c, [])]
        pop = [n for n in inst if _populated(n.get(f["field"]))]
        from_sdr = sum(1 for n in pop if str(n.get("id")) in s_pop[f["field"]])
        status = "ABSENT" if not inst else "FULL" if len(pop) == len(inst) else "PARTIAL" if pop else "NONE"
        source = ("SDR" if from_sdr == len(pop) else "GENERATED" if from_sdr == 0 else "BOTH") if pop else "-"
        verdict = "OK" if status == "FULL" else "GAP"
        note = ""
        rule = _NA_RULES.get(f["group"])
        if status != "FULL" and rule and text and rule[0](text):
            verdict, note = "NA", rule[1]
        rows.append({"area": f["area"], "group": f["group"], "field": f["field"], "status": status,
                     "populated": len(pop), "instances": len(inst), "source": source, "verdict": verdict, "note": note})
    counts = collections.Counter(r["verdict"] for r in rows)
    return {"total": len(rows), "ok": counts["OK"], "na": counts["NA"], "gaps": counts["GAP"], "rows": rows}


def write_xlsx(report: Dict[str, Any], path: str) -> None:
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Mandatory fields"
    ws.append(["Area", "Group", "Field", "Verdict", "Status", "Populated", "Instances", "Source", "Note"])
    for r in report["rows"]:
        ws.append([r["area"], r["group"], r["field"], r["verdict"], r["status"], r["populated"],
                   r["instances"], r["source"], r["note"]])
    wb.save(path)
