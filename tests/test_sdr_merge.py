"""SDR merge: SDR values always win, gaps are filled, new items added, no markers."""
import copy

import pytest

from merge.merger import MergeInvariantError, merge_usdm
from merge.text import is_empty, similarity


def _doc(design):
    return {"usdmVersion": "4.0.0", "study": {"id": "s", "name": "S", "instanceType": "Study",
            "versions": [{"id": "v", "versionIdentifier": "1", "instanceType": "StudyVersion",
                          "studyDesigns": [dict({"id": "d", "instanceType": "InterventionalStudyDesign"}, **design)]}]}}


def _design(merged):
    return merged["study"]["versions"][0]["studyDesigns"][0]


def _act(i, name, **kw):
    return dict({"id": i, "name": name, "instanceType": "Activity"}, **kw)


def test_sdr_value_is_never_replaced_and_empty_is_filled():
    sdr = _doc({"description": "SDR text", "rationale": "", "activities": [_act("a1", "Informed Consent", label="")]})
    ours = _doc({"description": "other text", "rationale": "Our rationale",
                 "activities": [_act("x1", "Informed consent", label="Consent")]})
    merged, report, _ = merge_usdm(sdr, ours)
    d = _design(merged)
    assert d["description"] == "SDR text"
    assert d["rationale"] == "Our rationale"
    assert d["activities"][0]["id"] == "a1" and d["activities"][0]["label"] == "Consent"
    assert len(d["activities"]) == 1
    assert report["conflicts"][0]["sdr"] == "SDR text"


def test_unmatched_item_added_and_no_marker_in_output():
    sdr = _doc({"activities": [_act("a1", "Informed Consent")]})
    ours = _doc({"activities": [_act("x1", "Informed Consent"), _act("x2", "Vital Signs")]})
    merged, report, _ = merge_usdm(sdr, ours)
    names = [a["name"] for a in _design(merged)["activities"]]
    assert names == ["Informed Consent", "Vital Signs"]
    assert report["added"][0]["item"] == "Vital Signs"
    assert not set(_design(merged)["activities"][1]) - {"id", "name", "instanceType"}


def test_references_follow_matched_ids():
    sdr = _doc({"activities": [_act("a1", "Consent")], "encounters": [{"id": "e1", "name": "1", "instanceType": "Encounter"}]})
    ours = _doc({"activities": [_act("x1", "Consent"), _act("x2", "ECG")],
                 "encounters": [{"id": "y1", "name": "V1 (Week -2)", "instanceType": "Encounter"}],
                 "scheduleTimelines": [{"id": "t", "instanceType": "ScheduleTimeline", "name": "Main", "instances": [
                     {"id": "i1", "instanceType": "ScheduledActivityInstance", "name": "i", "encounterId": "y1", "activityIds": ["x2"]}]}]})
    merged, _, _ = merge_usdm(sdr, ours)
    d = _design(merged)
    ecg = next(a for a in d["activities"] if a["name"] == "ECG")
    inst = d["scheduleTimelines"][0]["instances"][0]
    assert inst["encounterId"] == "e1" and inst["activityIds"] == [ecg["id"]]


def test_colliding_ids_are_renamed_and_unique():
    sdr = _doc({"activities": [_act("a1", "Consent")]})
    ours = _doc({"activities": [_act("a1", "Vital Signs")], "arms": [{"id": "arm", "name": "A", "instanceType": "StudyArm"}]})
    merged, _, _ = merge_usdm(sdr, ours)
    ids = [a["id"] for a in _design(merged)["activities"]]
    assert len(set(ids)) == 2 and "a1" in ids


def test_dangling_reference_removed():
    sdr = _doc({"activities": [_act("a1", "Consent")]})
    ours = _doc({"activities": [_act("x1", "Consent"), _act("x2", "ECG", biomedicalConceptIds=["gone"])]})
    ours["study"]["versions"][0]["biomedicalConcepts"] = [{"id": "gone", "name": "X", "instanceType": "BiomedicalConcept"}]
    sdr_ids = {"a1"}
    merged, _, _ = merge_usdm(sdr, ours)
    ecg = next(a for a in _design(merged)["activities"] if a["name"] == "ECG")
    assert ecg["biomedicalConceptIds"] == ["gone"]       # the concept was added too, so the link stays
    assert any(b["id"] == "gone" for b in merged["study"]["versions"][0]["biomedicalConcepts"])


def test_atomic_code_kept_whole():
    code = lambda c, d: {"id": "c", "code": c, "decode": d, "codeSystem": "x", "codeSystemVersion": "1", "instanceType": "Code"}
    sdr = _doc({"model": code("C1", "Parallel")})
    ours = _doc({"model": code("C2", "Crossover")})
    merged, _, _ = merge_usdm(sdr, ours)
    assert _design(merged)["model"]["decode"] == "Parallel"


def test_empty_sdr_input_is_not_modified():
    sdr = _doc({"activities": [_act("a1", "Consent")]})
    before = copy.deepcopy(sdr)
    merge_usdm(sdr, _doc({"activities": [_act("x", "Consent")]}))
    assert sdr == before


def test_invariant_detects_change():
    from merge.merger import _check
    problems = []
    _check({"a": "1", "b": ["x"]}, {"a": "2", "b": ["x", "y"]}, "$", problems)
    assert problems == ["$.a: '1' -> '2'"]


def test_text_helpers():
    assert is_empty('<div xmlns="http://www.w3.org/1999/xhtml"></div>')
    assert is_empty({"id": "x", "instanceType": "Code", "code": ""})
    assert not is_empty(False)
    assert similarity("Period 1", "Period 2") < 0.8
    assert similarity("GlucaGen", "GlucaGen (intramuscular glucagon)") >= 0.85
