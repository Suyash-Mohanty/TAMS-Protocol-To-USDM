"""Fixes from the MR01/YDAF business feedback: SDR schedule enriched not extended, endpoints
nested by the protocol's pairing, eligibility from the body sections, dosing product links."""
import os

import pytest

from agents.support.usdm_generator_agent import _ensure_primary_objective
from extraction.interventions.extractor import _best_product, _check_escalation_steps
from extraction.interventions.schema import AdministrableProduct, Administration
from extraction.objectives.extractor import _PLACEHOLDER_RE
from merge.merger import merge_usdm


# ---------------------------------------------------------------- merge: enrich, don't add
def _doc(design):
    return {"usdmVersion": "4.0.0", "study": {"id": "s", "instanceType": "Study", "versions": [{
        "id": "v", "instanceType": "StudyVersion",
        "studyDesigns": [dict({"id": "d", "instanceType": "InterventionalStudyDesign"}, **design)]}]}}


def _sai(i, enc, epoch, acts):
    return {"id": i, "name": i, "instanceType": "ScheduledActivityInstance", "encounterId": enc,
            "epochId": epoch, "activityIds": acts}


def test_schedule_items_are_not_added_when_sdr_has_a_schedule():
    sdr = _doc({
        "epochs": [{"id": "E1", "name": "Treatment", "instanceType": "StudyEpoch"},
                   {"id": "E2", "name": "ED", "instanceType": "StudyEpoch"}],
        "encounters": [{"id": "V1", "name": "1", "instanceType": "Encounter"},
                       {"id": "V16", "name": "16", "instanceType": "Encounter"}],
        "activities": [{"id": "A1", "name": "Vital Signs", "instanceType": "Activity"}],
        "scheduleTimelines": [{"id": "T", "name": "Main", "mainTimeline": True, "instanceType": "ScheduleTimeline",
                               "instances": [_sai("S1", "V1", "E1", ["A1"]), _sai("S16", "V16", "E2", ["A1"])],
                               "timings": [{"id": "TM", "name": "t", "instanceType": "Timing",
                                            "relativeFromScheduledInstanceId": "S1", "value": "P0W"}]}]})
    ours = _doc({
        "epochs": [{"id": "e1", "name": "Treatment", "instanceType": "StudyEpoch"},
                   {"id": "e2", "name": "ED", "instanceType": "StudyEpoch"},
                   {"id": "e3", "name": "Screening", "instanceType": "StudyEpoch"}],
        "encounters": [{"id": "v1", "name": "Visit 1", "instanceType": "Encounter", "label": "Baseline"},
                       {"id": "ved", "name": "ED", "instanceType": "Encounter", "label": "Early discontinuation"},
                       {"id": "vs", "name": "Screening", "instanceType": "Encounter"}],
        "activities": [{"id": "a1", "name": "Vital Signs", "instanceType": "Activity", "label": "VS"},
                       {"id": "a2", "name": "ECG", "instanceType": "Activity"}],
        "scheduleTimelines": [{"id": "t", "name": "Main", "instanceType": "ScheduleTimeline",
                               "instances": [_sai("s1", "v1", "e1", ["a1"]), _sai("sed", "ved", "e2", ["a1"]),
                                             _sai("ss", "vs", "e3", ["a2"])],
                               "timings": [{"id": "tm2", "name": "Follow-up", "instanceType": "Timing",
                                            "relativeFromScheduledInstanceId": "ss", "value": "P4W"}]}]})
    merged, report, _ = merge_usdm(sdr, ours)
    d = merged["study"]["versions"][0]["studyDesigns"][0]
    assert [e["id"] for e in d["epochs"]] == ["E1", "E2"]
    assert [e["id"] for e in d["encounters"]] == ["V1", "V16"]
    assert d["encounters"][1]["label"] == "Early discontinuation"     # ED paired with SDR "16" by epoch
    assert [a["id"] for a in d["activities"]] == ["A1"] and d["activities"][0]["label"] == "VS"
    tl = d["scheduleTimelines"][0]
    assert [i["id"] for i in tl["instances"]] == ["S1", "S16"]
    assert [t["id"] for t in tl["timings"]] == ["TM"]
    assert {r["class"] for r in report["not_added"]} >= {"StudyEpoch", "Encounter", "Activity", "Timing"}


def test_schedule_is_filled_when_sdr_has_none():
    sdr = _doc({"epochs": [{"id": "E1", "name": "Treatment", "instanceType": "StudyEpoch"}]})
    ours = _doc({"epochs": [{"id": "e1", "name": "Treatment", "instanceType": "StudyEpoch"}],
                 "encounters": [{"id": "v1", "name": "Visit 1", "instanceType": "Encounter"}]})
    merged, _, _ = merge_usdm(sdr, ours)
    assert [e["name"] for e in merged["study"]["versions"][0]["studyDesigns"][0]["encounters"]] == ["Visit 1"]


# ---------------------------------------------------------------- objectives / endpoints
def _ep(i, level):
    return {"id": i, "name": i, "text": i, "instanceType": "Endpoint", "level": {"code": level}}


def test_endpoints_nested_by_extracted_pairing_and_ids_kept():
    usdm = {"study": {"_pendingObjectiveEndpoints": {"o1": ["ep1"], "o2": ["ep2", "ep3"], "o3": ["ep4"]},
                      "versions": [{"studyDesigns": [{
                          "objectives": [{"id": "o1", "level": {"code": "C85826"}},
                                         {"id": "o2", "level": {"code": "C85827"}},
                                         {"id": "o3", "level": {"code": "C85827"}}],
                          "endpoints": [_ep("ep1", "C94496"), _ep("ep2", "C139173"),
                                        _ep("ep3", "C139173"), _ep("ep4", "C139173")],
                          "estimands": [{"id": "es", "variableOfInterestId": "ep3"}]}]}]}}
    _ensure_primary_objective(usdm)
    objs = usdm["study"]["versions"][0]["studyDesigns"][0]["objectives"]
    assert [[e["id"] for e in o["endpoints"]] for o in objs] == [["ep1"], ["ep2", "ep3"], ["ep4"]]


def test_placeholder_endpoints_recognised():
    assert _PLACEHOLDER_RE.match("Placeholder31")
    assert _PLACEHOLDER_RE.match("Placeholder - see ep_5 through ep_29")
    assert not _PLACEHOLDER_RE.match("Nausea and vomiting events")


# ---------------------------------------------------------------- dosing
def _prod(name, strength):
    return AdministrableProduct(id=name, name=name, strength_value=strength)


def test_product_link_never_crosses_substances_and_accepts_multiples():
    products = [_prod("Mirikizumab IV", 300), _prod("Mirikizumab SC", 100), _prod("Tirzepatide 5 mg", 5),
                _prod("Tirzepatide 10 mg", 10)]
    assert _best_product("Mirikizumab SC maintenance", "200 mg", products).name == "Mirikizumab SC"
    assert _best_product("Tirzepatide step 2", "5 mg", products).name == "Tirzepatide 5 mg"
    assert _best_product("Unrelated drug", "5 mg", products) is None


def test_escalation_gap_is_reported():
    steps = [Administration(id="1", name="Drug 8 mg arm - step 1", duration="Weeks 0-2"),
             Administration(id="2", name="Drug 8 mg arm - maintenance", duration="Week 6 through Week 52")]
    assert _check_escalation_steps(steps)
    steps[1].duration = "Week 2 through Week 52"
    assert not _check_escalation_steps(steps)


# ---------------------------------------------------------------- eligibility pages
@pytest.mark.skipif(not os.path.exists("input/UAT-IM-MR01.pdf"), reason="protocol PDF not available")
def test_eligibility_pages_come_from_the_body_sections():
    from extraction.eligibility.extractor import find_eligibility_pages
    pages = [p + 1 for p in find_eligibility_pages("input/UAT-IM-MR01.pdf")]
    assert pages[0] == 51 and pages[-1] == 61
    assert not set(pages) & {3, 4, 5}


def test_empty_sdr_amendment_takes_the_latest_generated_one():
    def doc(amendments):
        return {"usdmVersion": "4.0.0", "study": {"id": "s", "instanceType": "Study", "versions": [{
            "id": "v", "instanceType": "StudyVersion", "amendments": amendments}]}}
    sdr = doc([{"id": "A1", "name": "INITIAL", "number": "1", "summary": "", "instanceType": "StudyAmendment",
                "primaryReason": {"id": "r", "code": {"id": "c", "code": "", "decode": "", "instanceType": "Code"},
                                  "instanceType": "StudyAmendmentReason"}}])
    ours = doc([{"id": f"x{n}", "name": f"Amendment {n}", "number": n, "summary": f"Changes {n}",
                 "instanceType": "StudyAmendment"} for n in ("a", "b", "e")])
    merged, report, _ = merge_usdm(sdr, ours)
    amendments = merged["study"]["versions"][0]["amendments"]
    assert [(a["number"], a["summary"]) for a in amendments] == [("1", "Changes e"), ("a", "Changes a"), ("b", "Changes b")]
    assert amendments[0]["name"] == "INITIAL"          # SDR's own values stay
