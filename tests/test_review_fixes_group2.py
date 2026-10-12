"""
Regression tests for the second group of NCT03421379 (Diabetes) business
review findings, written as protocol-agnostic rules: CDISC study
intervention roles/types and concomitant medications (#14), Administrations
nested under StudyInterventions (#5/#6), schedule Timings anchored to the
main timeline (#18), and BiomedicalConcept linking/pruning (#17).
"""

import pytest

from agents.support.usdm_generator_agent import (
    _link_administrations_to_interventions,
    _link_timings_to_timeline,
    _prune_unreferenced_biomedical_concepts,
)
from extraction.biomedical_concepts.extractor import _source_activity
from extraction.interventions.extractor import (
    _best_product,
    _drop_concomitant,
    _map_intervention_role,
)
from extraction.interventions.schema import (
    AdministrableProduct,
    Administration,
    InterventionRole,
    StudyIntervention,
)


class TestInterventionRoles:

    @pytest.mark.parametrize("text,role", [
        ("Challenge Agent", InterventionRole.CHALLENGE),
        ("Agent used to induce hypoglycemia", InterventionRole.CHALLENGE),
        ("Experimental Intervention", InterventionRole.INVESTIGATIONAL),
        ("Active Comparator", InterventionRole.COMPARATOR),
        ("Rescue Medicine", InterventionRole.RESCUE),
        ("Prohibited medication", InterventionRole.CONCOMITANT),
    ])
    def test_map_role(self, text, role):
        assert _map_intervention_role(text) == role

    @pytest.mark.parametrize("role,code", [
        (InterventionRole.INVESTIGATIONAL, "C41161"),
        (InterventionRole.COMPARATOR, "C68609"),
        (InterventionRole.PLACEBO, "C753"),
        (InterventionRole.CHALLENGE, "C158128"),
        (InterventionRole.RESCUE, "C165835"),
        (InterventionRole.BACKGROUND, "C165822"),
    ])
    def test_role_codes_are_c207417(self, role, code):
        assert StudyIntervention(id="i", name="x", role=role).to_dict()["role"]["code"] == code

    def test_type_is_intervention_type_not_role(self):
        intervention = StudyIntervention(id="i", name="x", role=InterventionRole.COMPARATOR).to_dict()
        assert intervention["type"]["code"] == "C1909"  # DRUG (C99078)
        biologic = StudyIntervention(id="i", name="x", intervention_type="Biologic").to_dict()
        assert biologic["type"]["code"] == "C307"

    def test_concomitant_dropped_with_its_products(self):
        interventions = [
            StudyIntervention(id="i1", name="LY900018", role=InterventionRole.INVESTIGATIONAL),
            StudyIntervention(id="i2", name="Acetaminophen (paracetamol)", role=InterventionRole.CONCOMITANT),
        ]
        products = [AdministrableProduct(id="p1", name="LY900018 nasal powder"),
                    AdministrableProduct(id="p2", name="Acetaminophen")]
        kept_interventions, kept_products = _drop_concomitant(interventions, products)
        assert [i.name for i in kept_interventions] == ["LY900018"]
        assert [p.name for p in kept_products] == ["LY900018 nasal powder"]


class TestAdministrations:

    def test_v4_shape_and_wording_kept(self):
        admin = Administration(id="a", name="GlucaGen 1 mg IM", route_text="Intramuscular",
                               dose="1 mg (reconstituted to 1 mg/mL in 1.1 mL diluent)",
                               dose_frequency="single dose").to_dict()
        assert admin["dose"]["value"] == 1.0
        assert admin["dose"]["unit"]["standardCode"]["code"] == "C28253"
        assert admin["route"]["standardCode"]["code"] == "C28161"
        assert admin["duration"]["instanceType"] == "Duration"  # required in USDM 4.0
        assert "1.1 mL diluent" in admin["description"]

    def test_duration_quantity(self):
        admin = Administration(id="a", name="x", duration="64 weeks").to_dict()
        assert admin["duration"]["durationWillVary"] is False
        assert admin["duration"]["quantity"]["unit"]["standardCode"]["code"] == "C29844"

    def test_product_chosen_by_dose_given(self):
        products = [AdministrableProduct(id=f"p{d:g}", name=f"Eloralintide {d:g} mg injection", strength_value=d)
                    for d in (1.5, 3.0, 6.0, 9.0)] + [AdministrableProduct(id="pp", name="Placebo injection")]
        assert _best_product("Eloralintide 6 mg QW - escalation step 1", "3 mg", products).id == "p3"
        assert _best_product("Eloralintide 9 mg QW - maintenance", "9 mg", products).id == "p9"
        assert _best_product("Placebo QW", "Placebo", products).id == "pp"

    def test_generator_nests_administrations(self):
        usdm = {"study": {
            "versions": [{"studyInterventions": [{"id": "i1", "name": "LY900018"},
                                                 {"id": "i2", "name": "GlucaGen"}],
                          "administrableProducts": [{"id": "p1"}]}],
            "_pendingAdministrations": [
                {"id": "a1", "name": "3 mg nasal dose", "administrableProductId": "p1"},
                {"id": "a2", "name": "GlucaGen 1 mg IM", "administrableProductId": "missing"},
                {"id": "a3", "name": "Unrelated"},
            ],
            "_pendingInterventionAdmins": {"i1": ["a1"]},
        }}
        _link_administrations_to_interventions(usdm)
        i1, i2 = usdm["study"]["versions"][0]["studyInterventions"]
        assert [a["id"] for a in i1["administrations"]] == ["a1"]
        assert [a["id"] for a in i2["administrations"]] == ["a2"]
        assert "administrableProductId" not in i2["administrations"][0]  # dangling ref removed


class TestTimings:

    def _linked(self, timings):
        instances = [{"id": n, "name": n, "epochId": e} for n, e in [
            ("Days -28 to -2", "ep_s"), ("Period 1 Day -1", "ep_1"), ("Period 1 Day 1", "ep_1"),
            ("V2 (Week -2)", "ep_t"), ("V4 (Week 4)", "ep_t"), ("Follow-up/ED", "ep_f")]]
        usdm = {"study": {"_pendingTimings": timings, "versions": [{"studyDesigns": [{
            "epochs": [{"id": "ep_s", "name": "Screening"}, {"id": "ep_1", "name": "Period 1"},
                       {"id": "ep_t", "name": "Treatment"}, {"id": "ep_f", "name": "Follow-up"}],
            "scheduleTimelines": [{"id": "tl", "mainTimeline": True, "instances": instances}],
        }]}]}}
        _link_timings_to_timeline(usdm)
        return usdm["study"]["versions"][0]["studyDesigns"][0]["scheduleTimelines"][0]["timings"]

    def test_anchored_by_visit_label(self):
        [t] = self._linked([{"name": "Admission", "visitName": "Period 1 Day -1", "type": "Fixed Reference",
                             "value": "-P1D", "valueLabel": "Day -1"}])
        assert t["relativeFromScheduledInstanceId"] == "Period 1 Day -1"
        assert t["value"] == "P1D" and t["type"]["code"] == "C201358"
        assert t["relativeToFrom"]["code"] in {"C201352", "C201353", "C201354", "C201355"}

    def test_name_fallback_respects_signed_numbers_and_epochs(self):
        timings = self._linked([
            {"name": "Period 1 Day 1 Dosing", "value": "PT0M"},
            {"name": "Screening Window", "type": "Within", "value": "P28D",
             "windowLower": "-P28D", "windowUpper": "-P2D"},
            {"name": "Systemic glucocorticoid washout (>2 weeks)", "value": "-P90D"},
            {"name": "Total Treatment Period Duration", "value": "P64W"},
        ])
        anchors = {t["name"]: t["relativeFromScheduledInstanceId"] for t in timings}
        assert anchors == {"Period 1 Day 1 Dosing": "Period 1 Day 1", "Screening Window": "Days -28 to -2"}
        screening = next(t for t in timings if t["name"] == "Screening Window")
        assert screening["type"]["code"] == "C201356"  # After: "Within" isn't a C201264 term
        assert screening["windowLower"] == "-P28D"


class TestDiabetesRun1801Findings:
    """Issues found in the first Diabetes run with the group 1/2 changes."""

    def test_substance_from_listed_ingredients_or_intervention_context(self):
        from extraction.interventions.extractor import _match_substances
        from extraction.interventions.schema import Substance
        subs = [Substance(id="s1", name="glucagon"), Substance(id="s2", name="human regular insulin"),
                Substance(id="s3", name="acetaminophen")]
        assert _match_substances("LY900018", subs, ["Glucagon"]) == ["s1"]
        assert _match_substances("GlucaGen", subs, [], "GlucaGen (intramuscular glucagon)") == ["s1"]
        assert _match_substances("Placebo", subs, [], "") == []

    def test_strength_denominator(self):
        from agents.support.usdm_generator_agent import _link_substances_to_products
        usdm = {"study": {
            "versions": [{"administrableProducts": [{"id": "p1", "name": "Human regular insulin (diluted)"}]}],
            "_pendingProductStrengths": [{"productId": "p1", "substanceId": "s2", "value": 0.3, "unit": "U",
                                          "denominatorValue": 1.0, "denominatorUnit": "mL", "name": None}],
            "_pendingSubstances": {"s2": {"id": "s2", "name": "human regular insulin"}},
        }}
        _link_substances_to_products(usdm)
        strength = usdm["study"]["versions"][0]["administrableProducts"][0]["ingredients"][0]["substance"]["strengths"][0]
        assert strength["denominator"]["value"] == 1.0
        assert strength["denominator"]["unit"]["standardCode"]["code"] == "C28254"  # mL
        assert strength["name"].endswith("0.3 U/mL")

    def test_geographic_scopes_not_shared(self):
        from agents.support.usdm_generator_agent import _copy_with_new_ids
        scopes = [{"id": "g1", "type": {"id": "c1", "code": "C68846"}}]
        a, b = _copy_with_new_ids(scopes), _copy_with_new_ids(scopes)
        assert a[0]["id"] != b[0]["id"] != "g1" and a[0]["type"]["id"] != b[0]["type"]["id"]
        assert a[0]["type"]["code"] == "C68846"

    @pytest.mark.parametrize("text,code", [
        ("Diluted solution for IV infusion", "C42986"),  # SOLUTION, not "FOR SOLUTION"
        ("nasal powder", "C42972"),
    ])
    def test_broader_dose_form_prefers_literal_term(self, text, code):
        from core.cdisc_codelists import DOSE_FORM, lookup
        assert (lookup(DOSE_FORM, text) or lookup(DOSE_FORM, text, allow_broader=True))["code"] == code

    def test_dose_form_from_non_adjacent_words(self):
        from core.cdisc_codelists import DOSE_FORM, lookup
        assert lookup(DOSE_FORM, "solution for SC injection", allow_broader=True)["code"] == "C42945"

    def test_intervention_tie_broken_by_coverage(self):
        from extraction.interventions.extractor import _best_intervention
        interventions = [StudyIntervention(id="1", name="Human regular insulin (IV infusion)"),
                         StudyIntervention(id="2", name="IV glucose")]
        assert _best_intervention("IV glucose rescue infusion", interventions).id == "2"

    def test_visit_label_matched_by_visit_number(self):
        from agents.support.usdm_generator_agent import _instance_by_visit
        instances = [{"id": "a", "name": "V1 (Week -5)"}, {"id": "b", "name": "V3 (Week 0, Randomization)"},
                     {"id": "c", "name": "V801 (Week 70)"}]
        assert _instance_by_visit("Visit 1", instances)["id"] == "a"
        assert _instance_by_visit("Visit 801", instances)["id"] == "c"
        assert _instance_by_visit("Visit 2", instances) is None

    def test_intranasal_route(self):
        admin = Administration(id="a", name="x", route_text="Intranasal").to_dict()
        assert admin["route"]["standardCode"]["code"] == "C38284"


class TestDesignTextAndDevices:
    """#13 design rationale/description and version rationale; duplicate devices."""

    def test_version_rationale_from_amendment(self):
        from agents.support.usdm_generator_agent import _set_version_rationale
        usdm = {"study": {"versions": [{"rationale": "Protocol version", "amendments": [
            {"summary": "An exclusion criterion for retinopathy was added due to the risk of fundal hemorrhage."}]}]}}
        _set_version_rationale(usdm)
        assert usdm["study"]["versions"][0]["rationale"].startswith("An exclusion criterion for retinopathy")
        original = {"study": {"versions": [{}]}}
        _set_version_rationale(original)
        assert original["study"]["versions"][0]["rationale"] == "Original protocol version"

    def test_design_sections_from_protocol(self):
        import glob
        from core.pdf_utils import extract_section_text
        from extraction.studydesign.extractor import _OVERALL_DESIGN_TITLE, _RATIONALE_TITLE
        pdfs = glob.glob("input/EliLilly_NCT03421379_Diabetes.pdf")
        if not pdfs:
            pytest.skip("protocol PDF not available")
        rationale = extract_section_text(pdfs[0], _RATIONALE_TITLE)
        overall = extract_section_text(pdfs[0], _OVERALL_DESIGN_TITLE)
        assert rationale.startswith("This study design involves an open-label assessment")
        assert "crossover" in rationale.lower() and "washout" in rationale.lower()
        assert overall.startswith("This is a Phase 3, multicenter, randomized, open-label")

    @pytest.mark.parametrize("a,b", [
        ({"name": "Single-Use Nasal Dosing Device"}, {"name": "LY900018 single-use nasal dosing device"}),
        ({"name": "Continuous Glucose Monitor"}, {"name": "Continuous Glucose Monitor (CGM)"}),
        ({"name": "Dual-Energy X-Ray Absorptiometry Machine", "label": "DXA Machine"}, {"name": "DXA scanner"}),
        ({"name": "Blood Glucose Meter"}, {"name": "Blood glucose (BG) meter"}),
    ])
    def test_same_device(self, a, b):
        from agents.quality.reconciliation_agent import devices_duplicate
        assert devices_duplicate(a, b)

    @pytest.mark.parametrize("a,b", [
        ("12-Lead ECG Machine (Local)", "12-Lead ECG Machine (Central)"),
        ("KwikPen", "KwikPen Demo Device"),
        ("Intravenous Infusion Pump", "Intravenous Cannula / IV Line"),
        ("PET/CT Scanner", "CT Scanner"),
    ])
    def test_different_devices(self, a, b):
        from agents.quality.reconciliation_agent import devices_duplicate
        assert not devices_duplicate({"name": a}, {"name": b})


class TestOpenItems:
    """#3 study cells/elements, #12c section text."""

    def test_cells_keep_arm_specific_elements(self):
        from agents.support.usdm_generator_agent import _remap_study_cells
        epochs = [{"id": "E1", "name": "Screening"}, {"id": "E2", "name": "Period 1"}, {"id": "E3", "name": "Treatment"}]
        design = {
            "arms": [{"id": "A"}],
            "elements": [{"id": f"el{i}", "name": f"Sequence A - {n}"}
                         for i, n in enumerate(["Screening", "Period 1", "Dose Escalation", "Maintenance"])],
            "studyCells": [{"id": f"c{i}", "armId": "A", "epochId": f"epoch_{i + 1}", "elementIds": [f"el{i}"]}
                           for i in range(4)],
        }
        _remap_study_cells(design, epochs)
        cells = {c["epochId"]: c["elementIds"] for c in design["studyCells"]}
        assert cells["E1"] == ["el0"] and cells["E2"] == ["el1"]
        # provisional epochs 3 and 4 have no name match: by position, epoch_3 -> E3;
        # epoch_4 has no epoch of its own and is dropped; E3 keeps its element
        assert cells["E3"][0] == "el2"
        used = {e for c in design["studyCells"] for e in c["elementIds"]}
        assert {e["id"] for e in design["elements"]} == used  # no orphans
        assert len(design["studyCells"]) == 3  # one per arm x epoch

    def test_phases_sharing_an_epoch_share_a_cell(self):
        from agents.support.usdm_generator_agent import _remap_study_cells
        epochs = [{"id": "E1", "name": "Treatment"}]
        design = {"arms": [{"id": "A"}],
                  "elements": [{"id": "x", "name": "Arm - Dose Escalation Treatment"},
                               {"id": "y", "name": "Arm - Maintenance Treatment"}],
                  "studyCells": [{"id": "1", "armId": "A", "epochId": "epoch_1", "elementIds": ["x"]},
                                 {"id": "2", "armId": "A", "epochId": "epoch_2", "elementIds": ["y"]}]}
        _remap_study_cells(design, epochs)
        assert [c["elementIds"] for c in design["studyCells"]] == [["x", "y"]]

    def test_more_phases_than_epochs_mapped_by_name(self):
        # Element phases finer than SoA epochs ("Period 1 Pre-dose", "Period 1
        # Treatment") must land in their epoch, not shift by position
        from agents.support.usdm_generator_agent import _remap_study_cells
        epochs = [{"id": f"E{i}", "name": n} for i, n in enumerate(
            ["Screening", "Period 1", "Wash out", "Period 2", "Follow-up/ED"])]
        phases = ["Screening", "Period 1 Pre-dose (Day -1)", "Period 1 Treatment (Day 1)", "Wash Out",
                  "Period 2 Pre-dose (Day -1)", "Period 2 Treatment (Day 1)", "Follow-up/ED"]
        design = {"arms": [{"id": "A"}],
                  "elements": [{"id": f"el{i}", "name": f"Sequence A - {p}"} for i, p in enumerate(phases)],
                  "studyCells": [{"id": str(i), "armId": "A", "epochId": f"epoch_{i + 1}", "elementIds": [f"el{i}"]}
                                 for i in range(len(phases))]}
        _remap_study_cells(design, epochs)
        cells = {c["epochId"]: c["elementIds"] for c in design["studyCells"]}
        assert cells == {"E0": ["el0"], "E1": ["el1", "el2"], "E2": ["el3"], "E3": ["el4", "el5"], "E4": ["el6"]}

    def test_epoch_match_ignores_spacing(self):
        from agents.support.usdm_generator_agent import _remap_study_cells
        epochs = [{"id": "E1", "name": "Period 1"}, {"id": "E2", "name": "Wash out"}, {"id": "E3", "name": "Period 2"}]
        design = {"arms": [{"id": "A"}],
                  "elements": [{"id": "a", "name": "Seq A - Period 1 Treatment"}, {"id": "b", "name": "Seq A - Washout"},
                               {"id": "c", "name": "Seq A - Period 2 Treatment"}],
                  "studyCells": [{"id": str(i), "armId": "A", "epochId": f"epoch_{i + 3}", "elementIds": [e]}
                                 for i, e in enumerate("abc")]}
        _remap_study_cells(design, epochs)
        assert {c["epochId"]: c["elementIds"] for c in design["studyCells"]} == {"E1": ["a"], "E2": ["b"], "E3": ["c"]}

    def test_generator_admin_fallback_tie_break(self):
        usdm = {"study": {"versions": [{"studyInterventions": [
                    {"id": "i3", "name": "Human regular insulin (IV infusion)"}, {"id": "i4", "name": "IV glucose"}],
                    "administrableProducts": []}],
                "_pendingAdministrations": [{"id": "a4", "name": "IV glucose rescue infusion"}]}}
        _link_administrations_to_interventions(usdm)
        owners = [i["id"] for i in usdm["study"]["versions"][0]["studyInterventions"] if i.get("administrations")]
        assert owners == ["i4"]

    def test_section_text_from_protocol(self):
        import glob
        from core.pdf_utils import extract_numbered_sections
        pdfs = glob.glob("input/EliLilly_NCT03421379_Diabetes.pdf")
        if not pdfs:
            pytest.skip("protocol PDF not available")
        texts = extract_numbered_sections(pdfs[0], [
            ("5", "Study Design"), ("5.1", "Overall Design"), ("5.4", "Scientific Rationale for Study Design"),
            ("6", "Study Population"), ("6.1", "Inclusion Criteria"), ("6.2", "Exclusion Criteria"),
        ])
        assert texts["5.4"].startswith('<div xmlns="http://www.w3.org/1999/xhtml"><p>This study design involves')
        assert "[36]" in texts["6.2"] and "retinopathy" in texts["6.2"]
        assert "[11]" not in texts["6.1"]  # inclusion text stops at the 6.2 heading


class TestBiomedicalConcepts:

    def test_source_activity_must_be_an_input_line(self):
        lines = ["Urine Drug Screen", "Vital Signs (Supine Blood Pressure)"]
        assert _source_activity({"activity": "urine drug screen"}, lines) == "Urine Drug Screen"
        assert _source_activity({"activity": "Urine Drug Screen Safety"}, lines) is None

    def test_unused_bc_linked_or_pruned(self):
        version = {
            "studyDesigns": [{"activities": [
                {"id": "a1", "name": "Urine Drug Screen", "biomedicalConceptIds": ["bc1"]},
                {"id": "a2", "name": "FSH (Female patients only)"},
            ]}],
            "biomedicalConcepts": [{"id": "bc1", "name": "Urine Drug Screen"},
                                   {"id": "bc2", "name": "Urine Drug Screen Safety"},
                                   {"id": "bc3", "name": "FSH"}],
            "bcCategories": [{"id": "c1", "name": "Laboratory Tests", "memberIds": ["bc1", "bc2", "bc3"]},
                             {"id": "c2", "name": "Imaging", "memberIds": ["bc2"]}],
        }
        _prune_unreferenced_biomedical_concepts(version)
        assert [bc["name"] for bc in version["biomedicalConcepts"]] == ["Urine Drug Screen", "FSH"]
        assert version["studyDesigns"][0]["activities"][1]["biomedicalConceptIds"] == ["bc3"]
        assert [c["name"] for c in version["bcCategories"]] == ["Laboratory Tests"]
        assert version["bcCategories"][0]["memberIds"] == ["bc1", "bc3"]

    def test_nothing_pruned_when_linking_failed(self):
        version = {"studyDesigns": [{"activities": [{"id": "a1", "name": "X"}]}],
                   "biomedicalConcepts": [{"id": "bc1", "name": "Y"}], "bcCategories": []}
        _prune_unreferenced_biomedical_concepts(version)
        assert len(version["biomedicalConcepts"]) == 1
