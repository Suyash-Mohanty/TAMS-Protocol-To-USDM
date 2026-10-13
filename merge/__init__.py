"""Merge of a generated USDM onto an SDR-published USDM (SDR values always win)."""
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional

from .mandatory import coverage, pdf_text, write_xlsx
from .merger import MergeInvariantError, Merger, merge_usdm


def find_sdr_file(pdf_stem: str, sdr_dir: str = "SDR") -> Optional[str]:
    """The SDR JSON whose name starts with the protocol (PDF) name; None unless exactly one."""
    folder = Path(sdr_dir)
    if not folder.is_dir():
        return None
    hits = [p for p in folder.glob("*.json") if p.name.lower().startswith(pdf_stem.lower())]
    return str(hits[0]) if len(hits) == 1 else None


def remap_citations(citations_path: Path, merged: Dict[str, Any], merger: Merger) -> Dict[str, int]:
    """Re-key the per-field citations sidecar to the merged USDM and keep only citations of
    values that are ours in it.

    Citations are written before the merge, keyed by our ids. An item of ours matched to an
    SDR item now carries the SDR id, and there only the attributes we filled hold our values
    (SDR's own values have no citation from our extraction); an item we added keeps all its
    citations; items not in the merged document (not added) lose theirs.
    """
    data = json.loads(citations_path.read_text(encoding="utf-8"))
    final_ids = {i for i in _ids(merged)}
    kept: Dict[str, Any] = {}
    dropped_fields = 0
    for entity_id, entry in (data.get("citations") or {}).items():
        final_id = merger.idmap.get(entity_id, entity_id)
        fields = dict((entry or {}).get("fields") or {})
        if final_id not in final_ids:
            dropped_fields += len(fields)
            continue
        if final_id not in merger.added_ids:          # an SDR item: only the attributes we filled
            ours = {k: v for k, v in fields.items() if (final_id, k) in merger.filled_fields}
            dropped_fields += len(fields) - len(ours)
            fields = ours
        if fields:
            target = kept.setdefault(final_id, {"instanceType": entry.get("instanceType"), "fields": {}})
            target["fields"].update(fields)
    data["citations"] = kept
    tmp = citations_path.with_name(citations_path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, citations_path)
    return {"entities_kept": len(kept), "fields_kept": sum(len(e["fields"]) for e in kept.values()),
            "fields_dropped": dropped_fields}


def _ids(node: Any):
    if isinstance(node, dict):
        if isinstance(node.get("id"), str):
            yield node["id"]
        for v in node.values():
            yield from _ids(v)
    elif isinstance(node, list):
        for v in node:
            yield from _ids(v)


def merge_files(sdr_path: str, ours_path: str, out_dir: str, pdf_path: Optional[str] = None) -> Dict[str, Any]:
    """Merge, overwrite the generated <stem>_usdm.json with the merged USDM, write merge_report.json and mandatory_fields_report.(json|xlsx)."""
    sdr = json.loads(Path(sdr_path).read_text(encoding="utf-8"))
    ours = json.loads(Path(ours_path).read_text(encoding="utf-8"))
    merged, report, merger = merge_usdm(sdr, ours)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    merged_path = Path(ours_path)      # one USDM per protocol: the merged result replaces the generated file
    # write beside it, then swap in: the generated file is never left half-written
    tmp_path = merged_path.with_name(merged_path.name + ".tmp")
    tmp_path.write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp_path, merged_path)
    cov = coverage(merged, sdr, merger, pdf_text(pdf_path))
    report["sdr_file"], report["generated_file"] = Path(sdr_path).name, Path(ours_path).name
    citations_path = merged_path.with_name(merged_path.name.replace("_usdm.json", "_citations.json"))
    if citations_path.exists():
        report["citations"] = remap_citations(citations_path, merged, merger)
    (out / "merge_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "mandatory_fields_report.json").write_text(json.dumps(cov, indent=2, ensure_ascii=False), encoding="utf-8")
    try:
        write_xlsx(cov, str(out / "mandatory_fields_report.xlsx"))
    except Exception:
        pass
    return {"merged": str(merged_path), "summary": report["summary"], "coverage": {k: cov[k] for k in ("total", "ok", "na", "gaps")}}
