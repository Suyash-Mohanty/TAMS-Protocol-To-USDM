"""Merge a generated USDM v4 document onto an SDR-published one.

Rules (the SDR document is the base and always wins):
- every attribute the SDR document holds a value for keeps that value, verbatim;
- an attribute the SDR document left empty is filled from the generated document;
- generated items with no SDR counterpart are added (unless they only restate an SDR item);
- nothing is marked in the merged JSON - provenance lives in the returned report.
"""
import copy
import re
import uuid
from typing import Any, Dict, List, Optional, Set, Tuple

from .matching import ATOMIC, NEW_BELOW, POSITIONAL, SINGLE, best_candidate, keys_of, threshold
from .text import norm as _norm
from .text import is_empty, norm

# keys of the generated document that are never copied over
_SKIP_KEYS = {"id", "instanceType", "extensionAttributes"}
# processing order inside one object: lower first (matching of later keys needs earlier id pairs)
_RANK = {"documentedBy": -2, "contents": -1, "studyDesigns": 2, "studyCells": 3, "scheduleTimelines": 3,
         "eligibilityCriteria": 2, "instances": 3, "narrativeContentItems": 1, "encounters": 1, "timings": 4}
# The SDR schedule is authoritative: where the SDR document already lists items of these
# classes, generated items only enrich the matching SDR items - unmatched ones are not added
_ENRICH_ONLY = {"StudyEpoch", "Encounter", "Timing", "ScheduledActivityInstance", "Activity"}
# A filled-in item that lost one of these references (its target was not added) is incomplete
_REQUIRED_REFS = {"Timing": ("relativeFromScheduledInstanceId",), "StudyCell": ("armId", "epochId")}
_LINK_KEYS = ("previousId", "nextId")


class MergeInvariantError(Exception):
    """An SDR value changed during the merge."""


def _is_ref_key(key: str) -> bool:
    return key != "id" and (key.endswith("Id") or key.endswith("Ids"))


class Merger:
    def __init__(self, sdr: Dict[str, Any], ours: Dict[str, Any]):
        self.sdr_original = sdr
        self.merged = copy.deepcopy(sdr)
        self.ours = _separate_content_ids(copy.deepcopy(ours))
        self.sdr_ids = _collect_ids(sdr)
        self.ours_ids = _collect_ids(ours)
        self.idmap: Dict[str, str] = {}
        self.taken: List[Tuple[Any, Any]] = []        # (container, key|item) filled from ours
        self.child_unions: List[Tuple[list, list]] = []
        self.added_roots: List[Dict[str, Any]] = []
        self.report: Dict[str, Any] = {
            "matched": [], "added": [], "possible_duplicates": [], "filled": [], "conflicts": [],
            "skipped_schedule": [], "dangling_removed": [], "not_added": [], "incomplete_removed": [],
        }
        # encounter -> epoch, read from each document's scheduled instances (Encounter has no epochId)
        self.sdr_enc_epoch = _encounter_epochs(sdr)
        self.ours_enc_epoch = _encounter_epochs(ours)
        self.filled_fields: Set[Tuple[str, str]] = set()   # (node id, field) filled from ours
        self.added_ids: Set[str] = set()

    # ------------------------------------------------------------------ run
    def run(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        self._merge_dict(self.merged, self.ours, "$", None)
        self._finalise()
        self._prune_orphan_concepts()
        self._complete_study_cells()
        self._verify()
        self._summarise()
        return self.merged, self.report

    # ------------------------------------------------------------ dict merge
    def _merge_dict(self, s: Dict[str, Any], o: Dict[str, Any], path: str, cls: Optional[str]) -> None:
        for key in sorted((k for k in o if k not in _SKIP_KEYS), key=lambda k: _RANK.get(k, 0)):
            ov = o[key]
            if is_empty(ov):
                continue
            sv = s.get(key)
            here = f"{path}.{key}"
            if key not in s or is_empty(sv):
                s[key] = copy.deepcopy(ov)
                self.taken.append((s, key))
                self._note_fill(s, key, path, cls)
            elif isinstance(sv, dict) and isinstance(ov, dict):
                if (sv.get("instanceType") or ov.get("instanceType")) in ATOMIC:
                    # the same code may only lack attributes (version, system...): fill those
                    if _norm(sv.get("code")) and _norm(sv.get("code")) == _norm(ov.get("code")):
                        for k, v in ov.items():
                            if k not in _SKIP_KEYS and is_empty(sv.get(k)) and not is_empty(v):
                                sv[k] = copy.deepcopy(v)
                                self.taken.append((sv, k))
                                self._note_fill(sv, k, here, sv.get("instanceType"))
                    else:
                        self._conflict(here, sv, ov)
                else:
                    self._merge_dict(sv, ov, here, sv.get("instanceType") or ov.get("instanceType"))
            elif isinstance(sv, list) and isinstance(ov, list):
                self._merge_list(sv, ov, here, key)
            else:
                self._conflict(here, sv, ov)

    def _note_fill(self, node: Dict[str, Any], key: str, path: str, cls: Optional[str]) -> None:
        self.filled_fields.add((str(node.get("id")), key))
        self.report["filled"].append({"path": f"{path}.{key}", "class": cls or node.get("instanceType")})

    def _conflict(self, path: str, sv: Any, ov: Any) -> None:
        if norm(sv) != norm(ov) and not isinstance(sv, (dict, list)):
            self.report["conflicts"].append({"path": path, "sdr": str(sv)[:200], "generated": str(ov)[:200]})

    # ------------------------------------------------------------ list merge
    def _merge_list(self, s: list, o: list, path: str, key: str) -> None:
        if all(not isinstance(v, dict) for v in o) and all(not isinstance(v, dict) for v in s):
            if key == "childIds":
                self.child_unions.append((s, o))
            return
        cls = next((v.get("instanceType") for v in s + o if isinstance(v, dict) and v.get("instanceType")), key)
        if cls == "ScheduledActivityInstance":
            self._merge_instances(s, o, path)
            return
        pairs, rest = self._pair(s, o, cls)
        for sv, ov, how in pairs:
            self.idmap[ov["id"]] = sv["id"]
            self.report["matched"].append({"class": cls, "sdr": _label(sv), "generated": _label(ov), "by": how})
            self._merge_dict(sv, ov, f"{path}[{_label(sv)}]", cls)
        sdr_has_items = any(isinstance(v, dict) for v in s)
        for ov in rest:
            if cls in _ENRICH_ONLY and sdr_has_items:
                self.report["not_added"].append({"class": cls, "item": _label(ov), "path": path,
                                                 "reason": "the SDR schedule is authoritative; no SDR item matches"})
                continue
            best, score = best_candidate(ov, [v for v in s if isinstance(v, dict)], cls, self.idmap)
            if best is not None and score >= max(NEW_BELOW, threshold(cls)) and cls not in ("StudyCell", "EligibilityCriterion"):
                self.idmap[ov["id"]] = best["id"]
                self.report["possible_duplicates"].append(
                    {"class": cls, "generated": _label(ov), "similar_sdr": _label(best), "similarity": round(score, 2)})
                continue
            self._add(s, ov, cls, path)

    def _add(self, s: list, ov: Dict[str, Any], cls: str, path: str) -> None:
        item = copy.deepcopy(ov)
        s.append(item)
        self.taken.append((s, item))
        self.added_roots.append(item)
        self.report["added"].append({"class": cls, "item": _label(ov), "path": path})

    def _pair(self, s: list, o: list, cls: str):
        s_items = [v for v in s if isinstance(v, dict)]
        o_items = [v for v in o if isinstance(v, dict)]
        by_id = {v.get("id"): v for v in s_items}
        used: Set[int] = set()
        pairs, rest = [], []

        def take(ov, sv, how):
            used.add(id(sv))
            pairs.append((sv, ov, how))

        # pairs fixed earlier (e.g. narrative items via their matched contents)
        todo = []
        for ov in o_items:
            sv = by_id.get(self.idmap.get(ov.get("id")))
            if sv is not None and id(sv) not in used:
                take(ov, sv, "linked")
            else:
                todo.append(ov)
        # exact keys
        left = []
        for ov in todo:
            cand = [v for v in s_items if id(v) not in used]
            mine = set(keys_of(ov, cls, self.idmap))
            hit = next((v for v in cand if mine & set(keys_of(v, cls, self.idmap))), None)
            if hit is not None:
                take(ov, hit, "key")
            else:
                left.append(ov)
        # fuzzy, best score first
        scored = []
        for ov in left:
            for sv in s_items:
                if id(sv) in used:
                    continue
                _, sc = best_candidate(ov, [sv], cls, self.idmap)
                if sc >= threshold(cls):
                    scored.append((sc, id(ov), ov, sv))
        scored.sort(key=lambda t: -t[0])
        done: Set[int] = set()
        for sc, oid, ov, sv in scored:
            if oid in done or id(sv) in used:
                continue
            done.add(oid)
            take(ov, sv, f"similar {sc:.2f}")
        left = [ov for ov in left if id(ov) not in done]
        free = [sv for sv in s_items if id(sv) not in used]
        # an empty SDR placeholder item takes the next unmatched generated item
        if left and free:
            for sv in [v for v in free if is_empty(v)]:
                if left:
                    take(left.pop(0), sv, "placeholder")
            free = [sv for sv in s_items if id(sv) not in used]
        # an SDR amendment with no content (no summary, changes or reasons) and no number match is
        # a placeholder: it takes the latest generated amendment; the others are added beside it
        if left and free and cls == "StudyAmendment":
            for sv in [v for v in free if _amendment_is_placeholder(v)]:
                if left:
                    latest = max(left, key=lambda a: _natural_key(a.get("number")))
                    left.remove(latest)
                    take(latest, sv, "placeholder amendment")
            free = [sv for sv in s_items if id(sv) not in used]
        # visits of the same (matched) epoch pair in order when both sides list as many there
        # (SDR "16" / generated "ED" in the early-discontinuation epoch)
        if left and free and cls == "Encounter":
            for epoch in {self.sdr_enc_epoch.get(v.get("id")) for v in free} - {None}:
                mine = [ov for ov in left if self.idmap.get(self.ours_enc_epoch.get(ov.get("id"))) == epoch]
                theirs = [sv for sv in free if self.sdr_enc_epoch.get(sv.get("id")) == epoch]
                if mine and len(mine) == len(theirs):
                    for ov, sv in zip(mine, theirs):
                        take(ov, sv, "same epoch")
            left = [ov for ov in left if all(ov is not p[1] for p in pairs)]
            free = [sv for sv in s_items if id(sv) not in used]
        # structural fallbacks
        if left and free:
            if cls in POSITIONAL and len(left) == len(free):
                for ov, sv in zip(left, free):
                    take(ov, sv, "position")
                left = []
            elif cls in SINGLE or (len(left) == 1 and len(free) == 1 and cls in ("StudyDefinitionDocumentVersion", "StudyDefinitionDocument", "StudyAmendment")):
                if len(left) == 1 and len(free) == 1:
                    take(left[0], free[0], "only one")
                    left = []
            elif cls == "ScheduleTimeline":
                main = next((v for v in free if v.get("mainTimeline")), None)
                if main is not None and left:
                    take(left.pop(0), main, "main timeline")
        return pairs, left

    # ---------------------------------------------------- scheduled instances
    def _merge_instances(self, s: list, o: list, path: str) -> None:
        sdr_by_enc: Dict[Any, List[Dict[str, Any]]] = {}
        for v in s:
            if isinstance(v, dict):
                sdr_by_enc.setdefault(v.get("encounterId"), []).append(v)
        used: Set[int] = set()
        for ov in [v for v in o if isinstance(v, dict)]:
            enc = self.idmap.get(ov.get("encounterId"), ov.get("encounterId"))
            acts = {self.idmap.get(a, a) for a in ov.get("activityIds") or []}
            cands = [v for v in sdr_by_enc.get(enc, []) if id(v) not in used]
            hit = next((v for v in cands if acts and acts & set(v.get("activityIds") or [])), None) \
                or next((v for v in cands if not v.get("activityIds")), None)
            if hit is not None:
                used.add(id(hit))
                self.idmap[ov["id"]] = hit["id"]
                self.report["matched"].append({"class": "ScheduledActivityInstance", "sdr": _label(hit),
                                               "generated": _label(ov), "by": "encounter+activity"})
                self._merge_dict(hit, ov, f"{path}[{_label(hit)}]", "ScheduledActivityInstance")
            elif sdr_by_enc.get(enc):
                # the SDR document already defines this visit's schedule
                self.report["skipped_schedule"].append({"encounter": enc, "activities": sorted(acts)})
            elif enc in self.sdr_ids:
                self.report["skipped_schedule"].append({"encounter": enc, "activities": sorted(acts)})
            elif sdr_by_enc:
                self.report["not_added"].append({"class": "ScheduledActivityInstance", "item": _label(ov), "path": path,
                                                 "reason": "the SDR schedule is authoritative; no SDR item matches"})
            else:
                self._add(s, ov, "ScheduledActivityInstance", path)

    # -------------------------------------------------------------- finalise
    def _finalise(self) -> None:
        # a taken value is wrapped in a one-key proxy so scalar reference fields remap too
        proxies = []
        for container, key in self.taken:
            if isinstance(container, dict):
                proxies.append((container, key, {key: container[key]}))
            else:
                proxies.append((container, None, {"_": key}))
        nodes = [p[2] for p in proxies]
        # unmatched generated ids that clash with an unrelated SDR id get a new one
        for node in nodes:
            for nid in _collect_ids(node):
                if nid in self.sdr_ids and nid not in self.idmap:
                    self.idmap[nid] = f"{nid}_{uuid.uuid4().hex[:8]}"
        for node in nodes:
            _remap(node, self.idmap)
        self.added_ids = set()
        for node in nodes:
            self.added_ids |= _collect_ids(node)
        for container, key, proxy in proxies:
            if key is not None:
                container[key] = proxy[key]
        final_ids = _collect_ids(self.merged)
        for container, key, proxy in proxies:
            self._drop_dangling(proxy, final_ids)
            if key is not None:
                if key in proxy:
                    container[key] = proxy[key]
                else:
                    del container[key]
        self._remove_incomplete(proxies)
        for s_list, o_list in self.child_unions:
            for ref in o_list:
                ref = self.idmap.get(ref, ref)
                if ref in self.added_ids and ref not in s_list:
                    s_list.append(ref)

    def _remove_incomplete(self, proxies) -> None:
        """Drop filled-in items that lost a reference they cannot do without (a timing whose
        'relative from' instance was not added) - an incomplete item is worse than none."""
        def broken(item: Any) -> bool:
            need = _REQUIRED_REFS.get(item.get("instanceType")) if isinstance(item, dict) else None
            return bool(need) and any(not item.get(k) for k in need)

        for container, key, proxy in proxies:
            if key is None:          # an added list item
                item = proxy["_"]
                if broken(item) and item in container:
                    container.remove(item)
                    self.report["incomplete_removed"].append({"class": item.get("instanceType"), "item": _label(item)})
            elif isinstance(container.get(key), list):
                kept = [v for v in container[key] if not broken(v)]
                for v in container[key]:
                    if broken(v):
                        self.report["incomplete_removed"].append({"class": v.get("instanceType"), "item": _label(v)})
                container[key] = kept

    def _prune_orphan_concepts(self) -> None:
        """Added biomedical concepts that no activity (or other item) uses - their generated
        activities were not added to the SDR schedule - are dropped, and so are added concept
        categories left without members."""
        for version in self.merged.get("study", {}).get("versions", []):
            concepts = version.get("biomedicalConcepts") or []
            categories = version.get("bcCategories") or []
            added = {c.get("id") for c in concepts if c.get("id") in self.added_ids and c.get("id") not in self.sdr_ids}
            if not added:
                continue
            used: Set[str] = set()

            def refs(o, inside_category=False):
                if isinstance(o, dict):
                    in_cat = inside_category or o.get("instanceType") == "BiomedicalConceptCategory" or o is categories
                    for k, v in o.items():
                        if _is_ref_key(k) and not in_cat:
                            used.update(x for x in (v if isinstance(v, list) else [v]) if isinstance(x, str))
                        else:
                            refs(v, in_cat)
                elif isinstance(o, list):
                    for v in o:
                        refs(v, inside_category)
            refs({k: v for k, v in self.merged.items()})
            orphans = added - used
            if not orphans:
                continue
            version["biomedicalConcepts"] = [c for c in concepts if c.get("id") not in orphans]
            for cat in categories:
                if cat.get("id") in self.added_ids and isinstance(cat.get("memberIds"), list):
                    cat["memberIds"] = [m for m in cat["memberIds"] if m not in orphans]
            version["bcCategories"] = [c for c in categories
                                       if not (c.get("id") in self.added_ids and c.get("id") not in self.sdr_ids
                                               and not c.get("memberIds") and not c.get("childIds"))]
            self.report["incomplete_removed"].append(
                {"class": "BiomedicalConcept", "count": len(orphans), "reason": "used by no activity in the SDR schedule"})

    def _complete_study_cells(self) -> None:
        """Every arm x epoch of a design with arms needs a cell: epochs that only the SDR document
        lists (e.g. unscheduled visit, early discontinuation, follow-up) get one cell per arm, all
        sharing one generic element named after the epoch."""
        for version in self.merged.get("study", {}).get("versions", []):
            for design in version.get("studyDesigns", []):
                arms, epochs = design.get("arms") or [], design.get("epochs") or []
                if not arms or not epochs:
                    continue
                cells = design.setdefault("studyCells", [])
                covered = {(c.get("armId"), c.get("epochId")) for c in cells}
                elements = design.setdefault("elements", [])
                for epoch in epochs:
                    missing = [a for a in arms if (a.get("id"), epoch.get("id")) not in covered]
                    if not missing:
                        continue
                    element = next((e for e in elements if e.get("name") == epoch.get("name")), None)
                    if element is None:
                        element = {"id": str(uuid.uuid4()), "name": epoch.get("name") or "Element",
                                   "instanceType": "StudyElement"}
                        elements.append(element)
                        self.report["added"].append({"class": "StudyElement", "item": element["name"],
                                                     "path": "generic element for an SDR epoch"})
                    for arm in missing:
                        cells.append({"id": str(uuid.uuid4()), "armId": arm["id"], "epochId": epoch["id"],
                                      "elementIds": [element["id"]], "instanceType": "StudyCell"})
                        self.report["added"].append({"class": "StudyCell", "item": f"{arm.get('name')} x {epoch.get('name')}",
                                                     "path": "arm x epoch gap"})

    def _drop_dangling(self, node: Any, final_ids: Set[str]) -> None:
        if isinstance(node, dict):
            for key in list(node):
                val = node[key]
                if key in _LINK_KEYS:
                    if isinstance(val, str) and val not in self.added_ids:
                        del node[key]
                    continue
                if _is_ref_key(key):
                    if isinstance(val, str) and (val in self.ours_ids and val not in final_ids):
                        self.report["dangling_removed"].append({"key": key, "value": val})
                        del node[key]
                    elif isinstance(val, list):
                        keep = [v for v in val if not (isinstance(v, str) and v in self.ours_ids and v not in final_ids)]
                        if len(keep) != len(val):
                            self.report["dangling_removed"].append({"key": key, "count": len(val) - len(keep)})
                            node[key] = keep
                    continue
                self._drop_dangling(val, final_ids)
        elif isinstance(node, list):
            for v in node:
                self._drop_dangling(v, final_ids)

    # ---------------------------------------------------------------- verify
    def _verify(self) -> None:
        problems: List[str] = []
        _check(self.sdr_original, self.merged, "$", problems)
        if problems:
            raise MergeInvariantError("; ".join(problems[:10]))
        import collections
        before = collections.Counter(_all_ids(self.sdr_original))
        after = collections.Counter(_all_ids(self.merged))
        dupes = {i for i, n in after.items() if n > 1 and n > before.get(i, 0)}
        if dupes:
            raise MergeInvariantError(f"duplicate ids after merge: {sorted(dupes)[:5]}")
        self.report["invariant"] = "SDR values preserved; ids unique"

    def _summarise(self) -> None:
        by_class: Dict[str, Dict[str, int]] = {}
        for kind in ("matched", "added", "possible_duplicates"):
            for row in self.report[kind]:
                by_class.setdefault(row["class"], {}).setdefault(kind, 0)
                by_class[row["class"]][kind] += 1
        self.report["summary"] = {
            "matched": len(self.report["matched"]), "added": len(self.report["added"]),
            "possible_duplicates": len(self.report["possible_duplicates"]),
            "attributes_filled": len(self.report["filled"]), "conflicts": len(self.report["conflicts"]),
            "schedule_cells_skipped": len(self.report["skipped_schedule"]),
            "dangling_references_removed": len(self.report["dangling_removed"]),
            "not_added_sdr_schedule": len(self.report["not_added"]),
            "incomplete_removed": len(self.report["incomplete_removed"]),
            "by_class": by_class,
        }


# ------------------------------------------------------------------ helpers
def _label(item: Dict[str, Any]) -> str:
    for f in ("name", "label", "abbreviatedText", "sectionNumber", "version", "versionIdentifier", "number", "text", "id"):
        if item.get(f):
            return str(item[f])[:80]
    return str(item.get("id"))


def _separate_content_ids(doc: Any) -> Any:
    """A NarrativeContent must not share its id with a NarrativeContentItem; re-id the
    contents (and the childIds/previousId/nextId links between them) when it does."""
    item_ids = set()

    def gather(o):
        if isinstance(o, dict):
            if o.get("instanceType") == "NarrativeContentItem" and o.get("id"):
                item_ids.add(o["id"])
            for v in o.values():
                gather(v)
        elif isinstance(o, list):
            for v in o:
                gather(v)

    def fix(o):
        if isinstance(o, dict):
            contents = o.get("contents")
            if isinstance(contents, list) and any(isinstance(c, dict) and c.get("id") in item_ids for c in contents):
                new = {c["id"]: f"{c['id']}_c" for c in contents if isinstance(c, dict) and c.get("id") in item_ids}
                for c in contents:
                    if not isinstance(c, dict):
                        continue
                    c["id"] = new.get(c["id"], c["id"])
                    for key in ("previousId", "nextId"):
                        if c.get(key) in new:
                            c[key] = new[c[key]]
                    if isinstance(c.get("childIds"), list):
                        c["childIds"] = [new.get(x, x) for x in c["childIds"]]
            for v in o.values():
                fix(v)
        elif isinstance(o, list):
            for v in o:
                fix(v)

    gather(doc)
    fix(doc)
    return doc


def _amendment_is_placeholder(amendment: Dict[str, Any]) -> bool:
    """An amendment that states nothing: no summary, changes or reasons (its number aside)."""
    return all(is_empty(amendment.get(k)) for k in ("summary", "changes", "primaryReason", "secondaryReasons"))


def _natural_key(value: Any) -> tuple:
    """Order amendment numbers naturally: 2 < 10, a < b < e."""
    return tuple((0, int(t), "") if t.isdigit() else (1, 0, t)
                 for t in re.findall(r"\d+|[a-z]+", str(value or "").lower()))


def _encounter_epochs(doc: Any) -> Dict[str, str]:
    """encounter id -> epoch id, from the scheduled activity instances of every timeline."""
    out: Dict[str, str] = {}

    def walk(o):
        if isinstance(o, dict):
            if o.get("instanceType") == "ScheduledActivityInstance" and o.get("encounterId") and o.get("epochId"):
                out.setdefault(o["encounterId"], o["epochId"])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(doc)
    return out


def _taken_value(container: Any, key: Any) -> Any:
    return container[key] if isinstance(container, dict) else key


def _collect_ids(node: Any) -> Set[str]:
    out: Set[str] = set()
    for i in _all_ids(node):
        out.add(i)
    return out


def _all_ids(node: Any):
    if isinstance(node, dict):
        if isinstance(node.get("id"), str):
            yield node["id"]
        for v in node.values():
            yield from _all_ids(v)
    elif isinstance(node, list):
        for v in node:
            yield from _all_ids(v)


def _remap(node: Any, idmap: Dict[str, str]) -> None:
    if isinstance(node, dict):
        for key, val in node.items():
            if key == "id" or _is_ref_key(key) or key in _LINK_KEYS:
                if isinstance(val, str):
                    node[key] = idmap.get(val, val)
                elif isinstance(val, list):
                    node[key] = [idmap.get(v, v) if isinstance(v, str) else v for v in val]
                    continue
            _remap(node[key], idmap)
    elif isinstance(node, list):
        for v in node:
            _remap(v, idmap)


def _check(sdr: Any, merged: Any, path: str, problems: List[str]) -> None:
    """Every non-empty SDR value must be unchanged in the merged document."""
    if is_empty(sdr):
        return
    if isinstance(sdr, dict):
        if not isinstance(merged, dict):
            problems.append(f"{path}: object replaced")
            return
        for k, v in sdr.items():
            if k not in merged:
                if not is_empty(v):
                    problems.append(f"{path}.{k}: removed")
            else:
                _check(v, merged[k], f"{path}.{k}", problems)
    elif isinstance(sdr, list):
        if not isinstance(merged, list):
            problems.append(f"{path}: list replaced")
            return
        if all(not isinstance(v, dict) for v in sdr):
            if merged[:len(sdr)] != sdr:
                problems.append(f"{path}: list values changed")
            return
        index = {m.get("id"): m for m in merged if isinstance(m, dict)}
        for i, v in enumerate(sdr):
            if isinstance(v, dict) and v.get("id") in index:
                _check(v, index[v["id"]], f"{path}[{v['id']}]", problems)
            elif isinstance(v, dict) and not is_empty(v):
                problems.append(f"{path}[{i}]: item lost")
    elif sdr != merged:
        problems.append(f"{path}: {sdr!r} -> {merged!r}")


def merge_usdm(sdr: Dict[str, Any], ours: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any], "Merger"]:
    merger = Merger(sdr, ours)
    merged, report = merger.run()
    return merged, report, merger
