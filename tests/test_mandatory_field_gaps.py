"""
Tests for the four pipeline gaps found against the business "mandatory fields" list:
protocol sections (NarrativeContent), transition rules, conditions and key dates.

All rules are protocol-agnostic and run on small synthetic structures.
"""

import pytest

from agents.support.usdm_generator_agent import (
    _attach_document_version_dates,
    _build_document_contents,
    _build_quantity_range,
    _classify_document_versions,
    _link_conditions,
    _link_transition_rules,
    _post_normalize_cleanup,
)
from extraction.advanced.extractor import _build_advanced_data, _to_iso_date


def _approved():
    return {"code": "C25425", "decode": "Approved"}


def _final():
    return {"code": "C25508", "decode": "Final"}


# ---------------------------------------------------------------------------
# Gap 1: protocol sections -> NarrativeContent hierarchy
# ---------------------------------------------------------------------------

def _sections_usdm(doc_versions, amendments=({"number": "a", "newVersion": "YDAF(a)", "previousVersion": "Original Protocol"},)):
    return {"study": {
        "documentedBy": [{"id": "doc", "versions": doc_versions}],
        "versions": [{
            "id": "sv", "versionIdentifier": "1",
            "narrativeContentItems": [
                {"id": "nc_1", "name": "Study Design", "text": "Study Design", "instanceType": "NarrativeContentItem"},
                {"id": "nci_1_1", "name": "Overall Design", "text": '<div xmlns="http://www.w3.org/1999/xhtml"><p>x</p></div>',
                 "instanceType": "NarrativeContentItem"},
                {"id": "nci_1_2", "name": "Overall Design", "text": "", "instanceType": "NarrativeContentItem"},
            ],
        }],
        "_pendingSections": [
            {"id": "nci_1_1", "name": "Overall Design", "sectionNumber": "4.1", "sectionTitle": "Overall Design",
             "childIds": [], "order": 0, "topLevel": False},
            {"id": "nc_1", "name": "Study Design", "sectionNumber": "4", "sectionTitle": "Study Design",
             "childIds": ["nci_1_1", "nci_1_2"], "order": 0, "topLevel": True},
            {"id": "nci_1_2", "name": "Overall Design", "sectionNumber": "4.2", "sectionTitle": "Overall Design",
             "childIds": [], "order": 1, "topLevel": False},
        ],
        "_amendmentInfo": [dict(a) for a in amendments],
    }}


class TestProtocolSections:

    def _versions(self):
        return [
            {"id": "dv_orig", "version": "YDAF", "status": _final(), "instanceType": "StudyDefinitionDocumentVersion"},
            {"id": "dv_cur", "version": "YDAF(a)", "status": _approved(), "instanceType": "StudyDefinitionDocumentVersion"},
        ]

    def test_hierarchy_and_links(self):
        usdm = _sections_usdm(self._versions())
        _build_document_contents(usdm)
        contents = usdm["study"]["documentedBy"][0]["versions"][1]["contents"]
        assert [c["sectionNumber"] for c in contents] == ["4", "4.1", "4.2"]  # parent then children
        top, first, second = contents
        assert top["childIds"] == [first["id"], second["id"]]
        assert "previousId" not in top and top["nextId"] == first["id"]
        assert first["previousId"] == top["id"] and first["nextId"] == second["id"]
        assert "nextId" not in second
        assert (top["displaySectionNumber"], top["displaySectionTitle"]) == (True, True)
        assert [c["contentItemId"] for c in contents] == ["nc_1", "nci_1_1", "nci_1_2"]
        assert all(c["instanceType"] == "NarrativeContent" for c in contents)

    def test_names_unique_and_items_xhtml(self):
        usdm = _sections_usdm(self._versions())
        _build_document_contents(usdm)
        contents = usdm["study"]["documentedBy"][0]["versions"][1]["contents"]
        assert len({c["name"] for c in contents}) == len(contents)  # duplicate "Overall Design" disambiguated
        for item in usdm["study"]["versions"][0]["narrativeContentItems"]:
            assert item["text"].lstrip().startswith("<div")  # plain titles wrapped, XHTML left alone
        assert usdm["study"]["versions"][0]["documentVersionIds"] == ["dv_cur"]

    def test_current_version_is_the_amendments_not_the_last_listed(self):
        versions = list(reversed(self._versions()))  # order is not reliable
        usdm = _sections_usdm(versions)
        _build_document_contents(usdm)
        holders = [v["version"] for v in usdm["study"]["documentedBy"][0]["versions"] if v.get("contents")]
        assert holders == ["YDAF(a)"]

    def test_unique_approved_version_without_amendment_info(self):
        usdm = _sections_usdm(self._versions(), amendments=())
        _build_document_contents(usdm)
        holders = [v["version"] for v in usdm["study"]["documentedBy"][0]["versions"] if v.get("contents")]
        assert holders == ["YDAF(a)"]

    def test_document_without_versions_gets_one(self):
        usdm = _sections_usdm([], amendments=())
        _build_document_contents(usdm)
        [version] = usdm["study"]["documentedBy"][0]["versions"]
        assert version["version"] == "1" and len(version["contents"]) == 3
        assert version["status"]["code"] == "C25508"


# ---------------------------------------------------------------------------
# Gap 2: transition rules
# ---------------------------------------------------------------------------

def _design():
    epochs = [{"id": "E1", "name": "Screening"}, {"id": "E2", "name": "Period 1"},
              {"id": "E3", "name": "Wash out"}, {"id": "E4", "name": "Period 2"},
              {"id": "E5", "name": "Follow-up/ED"}, {"id": "E6", "name": "Additional Follow-up for TE ADA"}]
    names = {"E1": ["Screening"], "E2": ["Period 1 Pre-dose", "Period 1 Treatment"], "E3": ["Washout"],
             "E4": ["Period 2 Pre-dose", "Period 2 Treatment"], "E5": ["Follow-up/ED"],
             "E6": ["Additional Follow-up for TE ADA"]}
    elements, cells = [], []
    for arm in ("A", "B"):
        for epoch in epochs:
            ids = []
            for i, phase in enumerate(names[epoch["id"]]):
                eid = f"{arm}_{epoch['id']}_{i}"
                elements.append({"id": eid, "name": f"Seq {arm} - {phase}"})
                ids.append(eid)
            cells.append({"id": f"c_{arm}_{epoch['id']}", "armId": arm, "epochId": epoch["id"], "elementIds": ids})
    return {"arms": [{"id": "A"}, {"id": "B"}], "epochs": epochs, "elements": elements, "studyCells": cells,
            "encounters": [{"id": "v1", "name": "Visit 1 (Screening)"}, {"id": "v2", "name": "Visit 2 (Baseline)"}]}


def _rules_usdm(rules):
    return {"study": {"versions": [{"studyDesigns": [_design()]}], "_pendingTransitionRules": rules}}


class TestTransitionRules:

    def _els(self, usdm):
        return {e["id"]: e for e in usdm["study"]["versions"][0]["studyDesigns"][0]["elements"]}

    def test_rule_ends_last_and_starts_first_element_in_every_arm(self):
        usdm = _rules_usdm([{"id": "t1", "name": "Screening to Period 1", "text": "Randomized after screening",
                             "fromElementId": "epoch_screening", "toElementId": "epoch_period1"}])
        _link_transition_rules(usdm)
        els = self._els(usdm)
        for arm in ("A", "B"):
            assert els[f"{arm}_E1_0"]["transitionEndRule"]["text"] == "Randomized after screening"
            assert els[f"{arm}_E2_0"]["transitionStartRule"]["name"] == "Screening to Period 1"
            assert "transitionStartRule" not in els[f"{arm}_E2_1"]  # only the first element of the epoch
        assert els["A_E1_0"]["transitionEndRule"]["id"] != els["B_E1_0"]["transitionEndRule"]["id"]  # no shared ids

    def test_phase_names_finer_than_epochs(self):
        usdm = _rules_usdm([{"id": "t1", "name": "Pre-dose to treatment", "text": "t",
                             "fromElementId": "epoch_period1_pre_dose", "toElementId": "epoch_period1_treatment"}])
        _link_transition_rules(usdm)
        els = self._els(usdm)
        assert "transitionEndRule" in els["A_E2_0"] and "transitionStartRule" in els["A_E2_1"]

    def test_closest_epoch_name_wins(self):
        usdm = _rules_usdm([{"id": "t1", "name": "To follow-up", "text": "t",
                             "fromElementId": "epoch_period2", "toElementId": "epoch_followup"}])
        _link_transition_rules(usdm)
        els = self._els(usdm)
        assert "transitionStartRule" in els["A_E5_0"] and "transitionStartRule" not in els["A_E6_0"]

    def test_visit_rules_go_on_encounters_and_unlinked_rules_are_not_forced(self):
        usdm = _rules_usdm([
            {"id": "t1", "name": "V1 to V2", "text": "t", "fromElementId": "visit_1", "toElementId": "visit_2"},
            {"id": "t2", "name": "General discontinuation", "text": "t"},
        ])
        _link_transition_rules(usdm)
        design = usdm["study"]["versions"][0]["studyDesigns"][0]
        assert design["encounters"][0]["transitionEndRule"]["name"] == "V1 to V2"
        assert design["encounters"][1]["transitionStartRule"]["name"] == "V1 to V2"
        assert not any("transitionStartRule" in e or "transitionEndRule" in e for e in design["elements"])

    def test_one_rule_per_slot_first_wins(self):
        usdm = _rules_usdm([
            {"id": "t1", "name": "First", "text": "1", "fromElementId": "epoch_screening", "toElementId": "epoch_period1"},
            {"id": "t2", "name": "Second", "text": "2", "fromElementId": "epoch_screening", "toElementId": "epoch_period1"},
        ])
        _link_transition_rules(usdm)
        assert self._els(usdm)["A_E1_0"]["transitionEndRule"]["name"] == "First"


# ---------------------------------------------------------------------------
# Gap 3: conditions
# ---------------------------------------------------------------------------

class TestConditions:

    def test_conditions_placed_with_label_and_no_guessed_links(self):
        usdm = {"study": {"versions": [{}], "_pendingConditions": [
            {"id": "c1", "name": "Plasma Glucose Range", "text": "Admission only if PG is 90 to 250 mg/dL", "description": "d"},
            {"id": "c2", "name": "Only a name", "text": ""},
            {"id": "c3", "name": "", "text": "no name"},
            {"id": "c4", "name": "Has label", "label": "Short", "text": "t"},
        ]}}
        _link_conditions(usdm)
        conds = usdm["study"]["versions"][0]["conditions"]
        assert [c["name"] for c in conds] == ["Plasma Glucose Range", "Only a name", "Has label"]
        assert conds[0]["label"] == "Plasma Glucose Range" and conds[2]["label"] == "Short"
        assert conds[1]["text"] == "Only a name"  # text falls back to the name
        assert all("appliesToIds" not in c and "contextIds" not in c for c in conds)
        assert all(c["instanceType"] == "Condition" for c in conds)


# ---------------------------------------------------------------------------
# Gap 4: key dates
# ---------------------------------------------------------------------------

class TestKeyDates:

    @pytest.mark.parametrize("text,iso", [
        ("09-Sep-2025", "2025-09-09"), ("09 Sep 2025", "2025-09-09"), ("September 9, 2025", "2025-09-09"),
        ("2025-09-09", "2025-09-09"), ("15_Jan_2020", "2020-01-15"),
        ("Sep 2025", None), ("2025", None), ("09/09/2025", None), ("not dated", None), (None, None),
    ])
    def test_iso_date(self, text, iso):
        assert _to_iso_date(text) == iso  # ambiguous or partial dates are never guessed

    def test_original_protocol_date_entity(self):
        gd = _build_advanced_data({"amendments": [], "originalProtocolDate": "09-Sep-2025"}).original_protocol_date
        assert gd["dateValue"] == "2025-09-09" and gd["type"]["code"] == "C215664"  # Issued Date
        assert gd["documentVersionLabel"] == "Original" and gd["instanceType"] == "GovernanceDate"
        assert _build_advanced_data({"amendments": []}).original_protocol_date is None

    def _usdm(self, doc_versions):
        return {"study": {"documentedBy": [{"versions": doc_versions}], "versions": [{}],
                          "_pendingDocVersionDates": [{"id": "gd", "name": "Original Protocol Issued Date",
                                                       "dateValue": "2025-09-09", "documentVersionLabel": "Original"}]}}

    def _where(self, usdm):
        found = [v["version"] for v in usdm["study"]["documentedBy"][0]["versions"] if v.get("dateValues")]
        return found, usdm["study"]["versions"][0].get("dateValues")

    def test_attached_to_the_version_labelled_original(self):
        usdm = self._usdm([{"version": "Original"}, {"version": "Amendment a", "contents": [1]}])
        _attach_document_version_dates(usdm)
        assert self._where(usdm) == (["Original"], None)
        date = usdm["study"]["documentedBy"][0]["versions"][0]["dateValues"][0]
        assert "documentVersionLabel" not in date  # staging key removed

    def test_two_versions_without_label_uses_the_non_current_one(self):
        usdm = self._usdm([{"version": "YDAF(a)", "contents": [1]}, {"version": "YDAF"}])
        _attach_document_version_dates(usdm)
        assert self._where(usdm) == (["YDAF"], None)

    def test_single_version_holds_the_date(self):
        usdm = self._usdm([{"version": "1.0", "contents": [1]}])
        _attach_document_version_dates(usdm)
        assert self._where(usdm) == (["1.0"], None)

    def test_unidentifiable_original_falls_back_to_study_version(self):
        usdm = self._usdm([{"version": "1.0"}, {"version": "2.0"}, {"version": "3.0", "contents": [1]}])
        _attach_document_version_dates(usdm)
        found, study_dates = self._where(usdm)
        assert found == [] and len(study_dates) == 1


def test_staging_keys_never_reach_the_output():
    study = {"_pendingSections": [1], "_amendmentInfo": [{"number": "a"}], "_pendingTransitionRules": [1],
             "_pendingConditions": [1], "_pendingDocVersionDates": [1], "versions": [{"studyDesigns": [{}]}]}
    _post_normalize_cleanup({"study": study})
    assert not [k for k in study if k.startswith("_pending") or k == "_amendmentInfo"]


# ---------------------------------------------------------------------------
# Which document version is current / original (labels differ from amendments')
# ---------------------------------------------------------------------------

class TestDocumentVersionRoles:

    def _mr01(self):
        versions = [{"version": v, "status": _approved()} for v in ("e", "d", "c", "b", "a", "1.0")]
        chain = [{"number": n, "newVersion": f"Amendment {n}",
                  "previousVersion": "Original Protocol" if n == "a" else f"Amendment {chr(ord(n) - 1)}"}
                 for n in "abcde"]
        return versions, chain

    def test_amendment_letters_match_version_letters(self):
        versions, chain = self._mr01()
        current, original = _classify_document_versions(versions, chain)
        assert (current["version"], original["version"]) == ("e", "1.0")

    def test_independent_of_listing_order(self):
        versions, chain = self._mr01()
        current, original = _classify_document_versions(list(reversed(versions)), list(reversed(chain)))
        assert (current["version"], original["version"]) == ("e", "1.0")

    def test_version_label_equal_to_new_version(self):
        versions = [{"version": "YDAF", "status": _final()}, {"version": "YDAF(a)", "status": _approved()}]
        current, original = _classify_document_versions(
            versions, [{"number": "a", "newVersion": "YDAF(a)", "previousVersion": "Original Protocol"}])
        assert (current["version"], original["version"]) == ("YDAF(a)", "YDAF")

    def test_no_amendments(self):
        current, original = _classify_document_versions([{"version": "Initial Protocol", "status": _approved()}], [])
        assert current is original and current["version"] == "Initial Protocol"
        assert _classify_document_versions([], []) == (None, None)


# ---------------------------------------------------------------------------
# Planned enrollment: valid Quantity/Range from whatever the model returned
# ---------------------------------------------------------------------------

class TestPlannedCounts:

    @pytest.mark.parametrize("raw,value", [(200, 200.0), ("1,035", 1035.0), ("approximately 75 patients", 75.0),
                                           ({"value": 60}, 60.0), ({"maxValue": 200}, 200.0)])
    def test_single_number_is_a_quantity(self, raw, value):
        built = _build_quantity_range(raw)
        assert built["instanceType"] == "Quantity" and built["value"] == value and built["id"]

    def test_stated_range_is_a_range_of_quantities(self):
        built = _build_quantity_range({"minValue": 220, "maxValue": 180})
        assert built["instanceType"] == "Range" and built["isApproximate"] is False
        assert (built["minValue"]["value"], built["maxValue"]["value"]) == (180.0, 220.0)
        assert built["minValue"]["id"] and built["maxValue"]["id"]

    @pytest.mark.parametrize("raw", [None, True, "none stated", {"maxValue": {"instanceType": "Range"}, "instanceType": "Range"}])
    def test_malformed_values_give_nothing_rather_than_an_invalid_object(self, raw):
        assert _build_quantity_range(raw) is None
