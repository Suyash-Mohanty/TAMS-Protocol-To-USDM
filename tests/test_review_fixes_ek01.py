"""Fixes from the J6Z-MC-CD01 review: criteria on a bracket-only line, footnote abbreviations,
SoA table pages, shared non-treatment elements, and cells for SDR-only epochs."""
import re

from agents.support.usdm_generator_agent import _remap_study_cells
from extraction.eligibility.extractor import _CRITERION_LINE_RE
from extraction.narrative.extractor import _ABBREV_PAIR_RE, _FOOTNOTE_ABBREV_RE
from extraction.soa_finder import _SOA_RUNNING_HEADER_RE, _cap_pages, MAX_SOA_PAGES
from merge.merger import merge_usdm


def test_bracket_only_criterion_line_matches():
    assert _CRITERION_LINE_RE.match("[1016] ")
    assert _CRITERION_LINE_RE.match("[34] Have a history")
    assert not _CRITERION_LINE_RE.match("33")


def test_footnote_abbreviation_pairs():
    text = "Abbreviations: ACTH = adrenocorticotropic hormone; CYP = cytochrome P450; IUD = intrauterine devices.\n\nnext"
    body = _FOOTNOTE_ABBREV_RE.search(text).group(1)
    pairs = [_ABBREV_PAIR_RE.match(p).group(1) for p in re.sub(r"\s+", " ", body).split(";") if _ABBREV_PAIR_RE.match(p)]
    assert pairs == ["ACTH", "CYP", "IUD"]


def test_soa_running_header_and_cap_keeps_header_pages():
    assert _SOA_RUNNING_HEADER_RE.search("Study J6Z: SoA Table 3 UV ED")
    assert not _SOA_RUNNING_HEADER_RE.search("see the schedule of activities")
    pages = list(range(0, 40))
    header = list(range(20, 20 + MAX_SOA_PAGES))
    assert _cap_pages(pages, header) == header


def _design(types):
    epochs = [{"id": f"e{i}", "name": n, "type": {"code": c, "decode": d}} for i, (n, c, d) in enumerate(types)]
    arms = [{"id": "a1", "name": "A"}, {"id": "a2", "name": "B"}]
    elements = [{"id": f"x{a}{e['id']}", "name": f"{a} - {e['name']}"} for a in ("a1", "a2") for e in epochs]
    cells = [{"id": f"c{a}{e['id']}", "armId": a, "epochId": e["id"], "elementIds": [f"x{a}{e['id']}"]}
             for a in ("a1", "a2") for e in epochs]
    return {"arms": arms, "epochs": epochs, "elements": elements, "studyCells": cells}, epochs


def test_non_treatment_epochs_share_one_element():
    design, epochs = _design([("Screening", "C71485", "Screening Epoch"), ("Period 1", "C101526", "Treatment Epoch")])
    _remap_study_cells(design, epochs)
    names = {c["epochId"]: [e["name"] for e in design["elements"] if e["id"] in c["elementIds"]] for c in design["studyCells"]}
    screening = [c for c in design["studyCells"] if c["epochId"] == "e0"]
    assert len({tuple(c["elementIds"]) for c in screening}) == 1
    treatment = [c for c in design["studyCells"] if c["epochId"] == "e1"]
    assert len({tuple(c["elementIds"]) for c in treatment}) == 2


def test_merge_adds_cells_for_sdr_only_epochs():
    base = {"usdmVersion": "4.0.0", "study": {"id": "s", "instanceType": "Study", "versions": [{
        "id": "v", "instanceType": "StudyVersion", "studyDesigns": [{
            "id": "d", "instanceType": "InterventionalStudyDesign",
            "epochs": [{"id": "ep1", "name": "Screening", "instanceType": "StudyEpoch"},
                       {"id": "ep2", "name": "Follow-Up", "instanceType": "StudyEpoch"}]}]}]}}
    ours = {"usdmVersion": "4.0.0", "study": {"id": "s", "instanceType": "Study", "versions": [{
        "id": "v", "instanceType": "StudyVersion", "studyDesigns": [{
            "id": "d", "instanceType": "InterventionalStudyDesign",
            "arms": [{"id": "a", "name": "Arm", "instanceType": "StudyArm"}],
            "epochs": [{"id": "x1", "name": "Screening", "instanceType": "StudyEpoch"}]}]}]}}
    merged, _, _ = merge_usdm(base, ours)
    design = merged["study"]["versions"][0]["studyDesigns"][0]
    assert {c["epochId"] for c in design["studyCells"]} == {"ep1", "ep2"}
    assert len(design["elements"]) == 2
