"""
Regression tests for the NCT03421379 (Diabetes) business review findings,
written as protocol-agnostic rules: reconciliation word guard, CDISC codelist
resolution/conformance, product designation and dose form, study model and
phase, cross-agent entity id collisions, and the page finders for
eligibility continuation, objectives, TOC continuation and abbreviations.
"""

from types import SimpleNamespace

import pytest

from agents.quality.reconciliation_agent import words_differ
from agents.support.usdm_generator_agent import (
    _conform_codes_to_codelists,
    _resolve_ct_code,
    _study_phase_term,
)
from core.cdisc_codelists import (
    DOSE_FORM,
    INTERVENTION_MODEL,
    PRODUCT_DESIGNATION,
    UNIT,
    codelist_for,
    lookup,
)
from extraction.eligibility.extractor import _criteria_continuation_pages
from extraction.interventions.extractor import _derive_designation
from extraction.interventions.schema import (
    AdministrableProduct,
    InterventionRole,
    StudyIntervention,
)
from extraction.narrative.extractor import _acronym_density, _toc_continuation_pages
from extraction.studydesign.extractor import infer_intervention_model


class FakeDoc:
    """Minimal stand-in for a PyMuPDF document: a list of page texts."""

    def __init__(self, pages):
        self._pages = [SimpleNamespace(get_text=lambda t=t: t) for t in pages]

    def __len__(self):
        return len(self._pages)

    def __getitem__(self, i):
        return self._pages[i]


# ---------------------------------------------------------------------------
# Reconciliation: names differing by a distinct word are not duplicates
# ---------------------------------------------------------------------------

class TestWordsDiffer:

    @pytest.mark.parametrize("a,b", [
        ("Inclusion Criteria", "Exclusion Criteria"),
        ("Secondary Pharmacokinetic Estimand", "Secondary Pharmacodynamic Estimand"),
        ("Urine Drug Screen", "Urine Drug Screen Safety"),
        ("Serum Pregnancy Test", "Urine Pregnancy Test"),
        ("Mirikizumab IV", "Mirikizumab SC"),
        ("Contraception Requirement - Females", "Contraception Requirement - Males"),
        ("Primary Efficacy Estimand (Change in Body Weight)",
         "Primary Efficacy Estimand (Percent Change in Body Weight)"),
    ])
    def test_distinct(self, a, b):
        assert words_differ(a, b)

    @pytest.mark.parametrize("a,b", [
        ("Blood Draw", "Blood Draws"),
        ("Haematology Panel", "Hematology Panel"),
        ("Vital Signs*", "Vital Signs"),
        ("Screen", "Screening"),
        ("ECG", "ECG"),
    ])
    def test_variants(self, a, b):
        assert not words_differ(a, b)


# ---------------------------------------------------------------------------
# CDISC codelist lookup and conformance
# ---------------------------------------------------------------------------

class TestCodelists:

    @pytest.mark.parametrize("codelist,text,code", [
        (UNIT, "g", "C48155"),          # Gram — not "G Force"
        (UNIT, "U/mL", "C77607"),
        (UNIT, "µg", "C48152"),
        (DOSE_FORM, "Tablets", "C42998"),
        (DOSE_FORM, "Film-coated tablet", "C42931"),
        (DOSE_FORM, "Solution for injection", "C42945"),
        (DOSE_FORM, "Lyophilized powder for solution for injection", "C42957"),
        (INTERVENTION_MODEL, "Crossover", "C82637"),
        (PRODUCT_DESIGNATION, "NIMP", "C156473"),
    ])
    def test_lookup(self, codelist, text, code):
        assert lookup(codelist, text)["code"] == code

    def test_broader_only_on_request(self):
        assert lookup(DOSE_FORM, "nasal powder") is None
        assert lookup(DOSE_FORM, "nasal powder", allow_broader=True)["code"] == "C42972"

    def test_attribute_map(self):
        assert codelist_for("StudyDefinitionDocumentVersion", "status") == "C188723"
        assert codelist_for("Quantity", "unit") == "C71620"

    def test_resolve_with_codelist_uses_submission_value(self):
        code = _resolve_ct_code("g", UNIT)
        assert (code["code"], code["decode"]) == ("C48155", "g")

    def test_conformance_fixes_wrong_codelist_codes(self):
        usdm = {"study": {"documentedBy": [{
            "instanceType": "StudyDefinitionDocument",
            "type": {"code": "C42651", "decode": "Protocol", "instanceType": "Code"},
            "versions": [{
                "instanceType": "StudyDefinitionDocumentVersion",
                "status": {"code": "C70745", "decode": "Approved", "instanceType": "Code"},
            }],
        }]}}
        stats = _conform_codes_to_codelists(usdm)
        doc = usdm["study"]["documentedBy"][0]
        assert doc["type"]["code"] == "C70817"
        assert doc["versions"][0]["status"]["code"] == "C25425"
        assert stats["fixed"] == 2

    def test_conformance_leaves_unmatched_codes(self):
        usdm = {"instanceType": "StudyIntervention",
                "role": {"code": "C54126", "decode": "Concomitant Medication", "instanceType": "Code"}}
        assert _conform_codes_to_codelists(usdm)["unresolved"] == 1
        assert usdm["role"]["code"] == "C54126"

    @pytest.mark.parametrize("text,code", [
        ("Phase 3", "C15602"), ("PHASE 3", "C15602"), ("Phase III", "C15602"),
        ("phase 2/3", "C15694"), ("Phase 1b", "C199989"), ("Early Phase 1", "C54721"),
    ])
    def test_study_phase(self, text, code):
        assert _study_phase_term(text)["code"] == code


# ---------------------------------------------------------------------------
# Products: designation and dose form
# ---------------------------------------------------------------------------

class TestProducts:

    def _interventions(self):
        return [
            StudyIntervention(id="i1", name="LY900018", role=InterventionRole.INVESTIGATIONAL),
            StudyIntervention(id="i2", name="GlucaGen (Intramuscular Glucagon)", role=InterventionRole.COMPARATOR),
            StudyIntervention(id="i3", name="Human regular insulin (IV infusion)", role=InterventionRole.BACKGROUND),
            StudyIntervention(id="i4", name="Acetaminophen (paracetamol)", role=InterventionRole.CONCOMITANT),
        ]

    @pytest.mark.parametrize("product,designation", [
        ("LY900018 nasal powder", "IMP"),
        ("GlucaGen", "IMP"),              # comparator = IMP (reference product)
        ("Human regular insulin (diluted)", "NIMP"),
        ("Acetaminophen", "NIMP"),
        ("Unlisted product", "IMP"),
    ])
    def test_designation_from_intervention_role(self, product, designation):
        assert _derive_designation(product, self._interventions()) == designation

    def test_product_codes_are_cdisc(self):
        product = AdministrableProduct(id="p", name="LY900018", dose_form_text="nasal powder",
                                       designation="IMP").to_dict()
        assert product["administrableDoseForm"]["instanceType"] == "AliasCode"
        assert product["administrableDoseForm"]["standardCode"]["code"] == "C42972"  # POWDER, not PLASTER
        assert product["productDesignation"]["code"] == "C202579"

    def test_unstated_dose_form_is_cdisc_unknown(self):
        product = AdministrableProduct(id="p", name="Acetaminophen").to_dict()
        assert product["administrableDoseForm"]["standardCode"]["code"] == "C150001"


# ---------------------------------------------------------------------------
# Study model
# ---------------------------------------------------------------------------

class TestInterventionModel:

    @pytest.mark.parametrize("text,model", [
        ("This is a single-dose, 2-treatment, 2-period crossover study", "Crossover"),
        ("a randomized, two-period crossover design", "Crossover"),
        ("The crossover design allows each patient to serve as own control", "Crossover"),
        ("a 2x2 factorial design", "Factorial"),
        ("Patients who progress may cross over to open-label treatment", None),
        ("No crossover to the active arm is permitted", None),
        ("a randomized, parallel-group study", None),
    ])
    def test_infer(self, text, model):
        assert infer_intervention_model(text) == model


# ---------------------------------------------------------------------------
# Page finders
# ---------------------------------------------------------------------------

class TestPageFinders:

    def test_criteria_continue_onto_page_without_heading(self):
        doc = FakeDoc([
            "6.2. Exclusion Criteria\n[17] criterion\n[18] criterion",
            "Header\nPage 29\n[34] alcohol intake\n[35] unsuitable\n[36] retinopathy\n6.3.\nLifestyle and/or Dietary Requirements\ntext",
            "6.3.4. Contraception\ntext",
        ])
        assert _criteria_continuation_pages(doc, 0) == [1]

    def test_criteria_stop_at_next_section(self):
        doc = FakeDoc(["[1] a\n[2] b", "7. Treatments\n1. item"])
        assert _criteria_continuation_pages(doc, 0) == []

    def test_other_section_numbered_list_is_not_followed(self):
        # The last included page already moved on to a new section with its
        # own numbered steps; its continuation is not eligibility criteria.
        doc = FakeDoc([
            "6.2.\nPreparation/Handling/Storage/Accountability\n1. Store kits at 2-8C\n2. Only enrolled participants",
            "4. The Investigator is responsible for accountability\na. Report complaints",
        ])
        assert _criteria_continuation_pages(doc, 0) == []

    def test_long_single_level_list_continues(self):
        doc = FakeDoc([
            "5.2. Exclusion Criteria\n12. Have obesity induced by other disorders\n13. Have type 1 diabetes",
            "21. Have a history of heart failure\n22. Have either",
            "37. Are receiving other treatment\n42. Are enrolled in another study\n5.3.\nLifestyle Considerations",
        ])
        assert _criteria_continuation_pages(doc, 0) == [1, 2]

    def test_toc_continuation(self):
        leaders = "\n".join(f"{i}. Section .......... {i * 3}" for i in range(1, 6))
        doc = FakeDoc(["Table of Contents\n" + leaders, leaders, leaders, "1. Protocol Synopsis\nbody text"])
        assert _toc_continuation_pages(doc, 0) == [1, 2]

    def test_abbreviation_list_density(self):
        abbreviations = "AE\nadverse event\nAUC\narea under the curve\nHIV\nhuman immunodeficiency virus\nPK\npharmacokinetics"
        body = "Patients will fast for at least 8 hours prior to the procedure.\nThey should remain seated.\nBlood samples are drawn."
        assert _acronym_density(abbreviations) >= 0.2 > _acronym_density(body)
