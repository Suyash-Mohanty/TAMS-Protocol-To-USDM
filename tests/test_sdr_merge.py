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


def _ind(i, name, **kw):
    return dict({"id": i, "name": name, "instanceType": "Indication"}, **kw)


def test_unmatched_item_added_and_no_marker_in_output():
    sdr = _doc({"indications": [_ind("a1", "Ulcerative colitis")]})
    ours = _doc({"indications": [_ind("x1", "Ulcerative colitis"), _ind("x2", "Obesity")]})
    merged, report, _ = merge_usdm(sdr, ours)
    names = [a["name"] for a in _design(merged)["indications"]]
    assert names == ["Ulcerative colitis", "Obesity"]
    assert report["added"][0]["item"] == "Obesity"
    assert not set(_design(merged)["indications"][1]) - {"id", "name", "instanceType"}


def test_unmatched_activity_is_not_added_to_sdr_schedule():
    sdr = _doc({"activities": [_act("a1", "Informed Consent")]})
    ours = _doc({"activities": [_act("x1", "Informed Consent"), _act("x2", "Vital Signs")]})
    merged, report, _ = merge_usdm(sdr, ours)
    assert [a["name"] for a in _design(merged)["activities"]] == ["Informed Consent"]
    assert report["not_added"][0]["item"] == "Vital Signs"


def test_references_follow_matched_ids():
    sdr = _doc({"activities": [_act("a1", "Consent")], "encounters": [{"id": "e1", "name": "1", "instanceType": "Encounter"}]})
    ours = _doc({"activities": [_act("x1", "Consent"), _act("x2", "ECG")],
                 "encounters": [{"id": "y1", "name": "V1 (Week -2)", "instanceType": "Encounter"}],
                 "scheduleTimelines": [{"id": "t", "instanceType": "ScheduleTimeline", "name": "Main", "instances": [
                     {"id": "i1", "instanceType": "ScheduledActivityInstance", "name": "i", "encounterId": "y1",
                      "activityIds": ["x1", "x2"]}]}]})
    merged, _, _ = merge_usdm(sdr, ours)
    inst = _design(merged)["scheduleTimelines"][0]["instances"][0]
    # matched visit/activity map to the SDR ids; the not-added activity's link is dropped
    assert inst["encounterId"] == "e1" and inst["activityIds"] == ["a1"]


def test_colliding_ids_are_renamed_and_unique():
    sdr = _doc({"indications": [_ind("a1", "Ulcerative colitis")]})
    ours = _doc({"indications": [_ind("a1", "Obesity")]})
    merged, _, _ = merge_usdm(sdr, ours)
    ids = [a["id"] for a in _design(merged)["indications"]]
    assert len(set(ids)) == 2 and "a1" in ids


def test_dangling_reference_removed():
    # "gone" is a generated activity that is not added (the SDR schedule already lists activities)
    sdr = _doc({"indications": [_ind("a1", "Ulcerative colitis")], "activities": [_act("s1", "Consent")]})
    ours = _doc({"indications": [_ind("x1", "Ulcerative colitis"), _ind("x2", "Obesity", codeIds=["gone"])],
                 "activities": [_act("gone", "ECG")]})
    merged, report, _ = merge_usdm(sdr, ours)
    added = next(a for a in _design(merged)["indications"] if a["name"] == "Obesity")
    assert added["codeIds"] == []                      # "gone" is not in the merged document
    assert report["dangling_removed"]


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
