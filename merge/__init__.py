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
    (out / "merge_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "mandatory_fields_report.json").write_text(json.dumps(cov, indent=2, ensure_ascii=False), encoding="utf-8")
    try:
        write_xlsx(cov, str(out / "mandatory_fields_report.xlsx"))
    except Exception:
        pass
    return {"merged": str(merged_path), "summary": report["summary"], "coverage": {k: cov[k] for k in ("total", "ok", "na", "gaps")}}
