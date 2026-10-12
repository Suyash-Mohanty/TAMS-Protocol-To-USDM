"""
Regression tests for the mandatory "09.22 Outstanding Fields" (Activity
Management field analysis): StudyRole.code/name, StudyChange.name/summary,
StudyAmendmentReason.code, Substance.name/strengths and Strength.name.

Cases are taken from protocol J3R-MC-YDAF.
"""

import pytest

from agents.quality.reconciliation_agent import clean_entity_name, numbers_differ
from agents.support.usdm_generator_agent import (
    _link_change_sections_to_document,
    _link_substances_to_products,
    _map_study_role,
)
from extraction.advanced.schema import (
    StudyAmendment,
    resolve_amendment_reason,
)
from extraction.interventions.extractor import _parse_interventions_response
from extraction.metadata.extractor import _map_role_code, detect_governance_roles
from extraction.metadata.schema import StudyRole, StudyRoleCode


# ---------------------------------------------------------------------------
# Reconciliation: footnote cleaning and numeric guard
# ---------------------------------------------------------------------------

class TestReconciliationNames:

    @pytest.mark.parametrize("name", [
        "Short-term insulin (rescue)",
        "Oral antihyperglycemic medications (AHMs)",
        "Insulin (non-rescue)",
        "glucagon (synthetic human)",
    ])
    def test_parenthesised_words_not_truncated(self, name):
        assert clean_entity_name(name) == name

    def test_separate_footnote_letter_still_removed(self):
        assert clean_entity_name("Vital Signs a)") == "Vital Signs"

    def test_different_strengths_are_distinct(self):
        assert numbers_differ("Eloralintide 1.5 mg injection", "Eloralintide 3 mg injection")
        assert numbers_differ("GLP-1 receptor agonists", "GIP/GLP receptor agonists")

    def test_same_numbers_can_merge(self):
        assert not numbers_differ("Eloralintide 3 mg injection", "Eloralintide 3 mg injections")
        assert not numbers_differ("Blood Draw", "Blood Draws")


# ---------------------------------------------------------------------------
# Substance / Strength
# ---------------------------------------------------------------------------

def _usdm_with_products(doses):
    products = [{"id": f"prod_{i}", "name": f"Eloralintide {d} mg injection",
                 "instanceType": "AdministrableProduct"} for i, d in enumerate(doses)]
    return {
        "study": {
            "versions": [{"administrableProducts": products}],
            "_pendingProductStrengths": [
                {"productId": f"prod_{i}", "substanceId": "sub_1", "value": d, "unit": "mg", "name": None}
                for i, d in enumerate(doses)
            ],
            "_pendingSubstances": {"sub_1": {"id": "sub_1", "name": "Eloralintide (LY3841136)"}},
        }
    }


class TestProductSubstanceLinks:

    def _products(self, raw_products, raw_substances):
        data = _parse_interventions_response({
            "interventions": [], "products": raw_products, "substances": raw_substances,
        })
        return {p.name: p.substance_ids for p in data.products}

    def test_every_strength_product_linked_to_shared_substance(self):
        links = self._products(
            [{"name": f"Eloralintide {d} mg prefilled syringe", "strengthValue": d, "strengthUnit": "mg"}
             for d in (1.5, 3, 6, 9)] + [{"name": "Placebo prefilled syringe"}],
            [{"id": "sub_1", "name": "eloralintide"}],
        )
        assert all(links[f"Eloralintide {d} mg prefilled syringe"] == ["sub_1"] for d in (1.5, 3, 6, 9))
        assert links["Placebo prefilled syringe"] == []

    def test_match_by_name_with_multiple_substances(self):
        links = self._products(
            [{"name": "Drug A 10 mg tablet"}, {"name": "Drug B 5 mg tablet"}, {"name": "LY3841136 injection"}],
            [{"id": "sub_a", "name": "Drug A"}, {"id": "sub_b", "name": "Drug B"},
             {"id": "sub_c", "name": "Eloralintide (LY3841136)"}],
        )
        assert links == {"Drug A 10 mg tablet": ["sub_a"], "Drug B 5 mg tablet": ["sub_b"],
                         "LY3841136 injection": ["sub_c"]}


class TestStrengths:

    def test_one_strength_per_product_named_from_dose(self):
        usdm = _usdm_with_products([1.5, 3, 6, 9])
        _link_substances_to_products(usdm)
        products = usdm["study"]["versions"][0]["administrableProducts"]
        names = [p["ingredients"][0]["substance"]["strengths"][0]["name"] for p in products]
        assert names == ["Eloralintide 1.5 mg", "Eloralintide 3 mg", "Eloralintide 6 mg", "Eloralintide 9 mg"]

    def test_strength_name_uses_product_casing(self):
        usdm = _usdm_with_products([3])
        usdm["study"]["_pendingSubstances"]["sub_1"]["name"] = "eloralintide"
        _link_substances_to_products(usdm)
        product = usdm["study"]["versions"][0]["administrableProducts"][0]
        assert product["ingredients"][0]["substance"]["name"] == "Eloralintide"
        assert product["ingredients"][0]["substance"]["strengths"][0]["name"] == "Eloralintide 3 mg"

    def test_substance_code_suffix_kept(self):
        usdm = _usdm_with_products([3])
        usdm["study"]["_pendingSubstances"]["sub_1"]["name"] = "eloralintide (LY3841136)"
        _link_substances_to_products(usdm)
        product = usdm["study"]["versions"][0]["administrableProducts"][0]
        assert product["ingredients"][0]["substance"]["name"] == "Eloralintide (LY3841136)"

    def test_substance_ids_unique_across_products(self):
        usdm = _usdm_with_products([1.5, 3])
        _link_substances_to_products(usdm)
        products = usdm["study"]["versions"][0]["administrableProducts"]
        ids = [p["ingredients"][0]["substance"]["id"] for p in products]
        assert len(set(ids)) == 2
        assert all(p["ingredients"][0]["substance"]["name"] == "Eloralintide (LY3841136)" for p in products)


# ---------------------------------------------------------------------------
# StudyAmendmentReason / StudyChange
# ---------------------------------------------------------------------------

class TestAmendmentReason:

    @pytest.mark.parametrize("text,term", [
        ("New Safety Information Available", "New Safety Information Available"),
        ("new safety information available", "New Safety Information Available"),
        ("Safety", "New Safety Information Available"),
        ("Regulatory", "New Regulatory Guidance"),
        ("FDA request", "Regulatory Agency Request To Amend"),
        ("Administrative", "Inconsistency and/or Error In The Protocol"),
        ("Recruitment", "Recruitment Difficulty"),
        ("Budget reallocation", "Other"),
    ])
    def test_resolve(self, text, term):
        assert resolve_amendment_reason(text) == term

    def test_blank_is_none(self):
        assert resolve_amendment_reason("") is None
        assert resolve_amendment_reason(None) is None

    def test_primary_and_secondary_coded(self):
        amend = StudyAmendment(
            id="amend_1", number="a", summary="Address safety committee feedback.",
            primary_reason="New Safety Information Available",
            secondary_reasons=["Inconsistency and/or Error In The Protocol"],
        ).to_dict()
        assert amend["primaryReason"]["code"]["code"] == "C207609"
        assert "otherReason" not in amend["primaryReason"]
        assert [r["code"]["code"] for r in amend["secondaryReasons"]] == ["C207603"]

    def test_other_keeps_protocol_wording(self):
        amend = StudyAmendment(
            id="amend_1", number="1", primary_reason="Other", other_reason="Budget reallocation",
        ).to_dict()
        assert amend["primaryReason"]["code"]["code"] == "C17649"
        assert amend["primaryReason"]["otherReason"] == "Budget reallocation"


class TestStudyChanges:

    def _amendment(self):
        return StudyAmendment(
            id="amend_1", number="a",
            summary="Address feedback received from an internal safety committee.",
            primary_reason="New Safety Information Available",
            changes=[
                {"sectionNumber": "5.2", "sectionTitle": "Exclusion Criteria",
                 "description": "Exclusion Criterion #16: removed exception for short-term insulin.",
                 "rationale": "Updated internal safety guidance."},
                {"sectionNumber": "6.9.3", "sectionTitle": "Prohibited Medications",
                 "description": "Updated Note regarding short-term insulin use.",
                 "rationale": "Updated internal safety guidance."},
                {"sectionNumber": "", "sectionTitle": "", "description": ""},  # empty row skipped
            ],
        ).to_dict()

    def test_one_change_per_row(self):
        changes = self._amendment()["changes"]
        assert [c["name"] for c in changes] == [
            "Section 5.2 Exclusion Criteria", "Section 6.9.3 Prohibited Medications",
        ]
        assert changes[0]["summary"].startswith("Exclusion Criterion #16")
        assert changes[0]["rationale"] == "Updated internal safety guidance."
        section = changes[0]["changedSections"][0]
        assert (section["sectionNumber"], section["sectionTitle"]) == ("5.2", "Exclusion Criteria")
        assert section["instanceType"] == "DocumentContentReference"

    def test_no_table_no_changes(self):
        amend = StudyAmendment(id="amend_1", number="1").to_dict()
        assert "changes" not in amend  # generator adds its fallback change

    def test_changed_sections_point_at_document(self):
        usdm = {"study": {
            "documentedBy": [{"id": "doc_1"}],
            "versions": [{"amendments": [self._amendment()]}],
        }}
        _link_change_sections_to_document(usdm)
        for change in usdm["study"]["versions"][0]["amendments"][0]["changes"]:
            assert change["changedSections"][0]["appliesToId"] == "doc_1"


# ---------------------------------------------------------------------------
# StudyRole
# ---------------------------------------------------------------------------

YDAF_TEXT = """
Sponsor Name: Eli Lilly and Company
Medical Monitor Name and Contact Information will be provided separately.
confirmed by the central laboratory at screening (Visit 1).
The investigator or authorized study personnel are responsible for study intervention accountability.
An independent DMC will be established for interim safety monitoring. A statistical analysis
center independent from the Sponsor will perform the data analysis for the DMC.
10.1.5.1. Clinical Endpoint Committee
An independent CEC with membership external to the Sponsor will be responsible for event adjudication.
10.1.5.2. Data Monitoring Committee
"""


class TestStudyRoles:

    def test_detect_governance_roles_ydaf(self):
        roles = dict((code, name) for name, code in detect_governance_roles(YDAF_TEXT))
        assert roles[StudyRoleCode.INDEPENDENT_DMC] == "Independent Data Monitoring Committee"
        assert StudyRoleCode.DATA_MONITORING_COMMITTEE not in roles
        assert roles[StudyRoleCode.ADJUDICATION_COMMITTEE] == "Clinical Endpoint Committee"
        assert roles[StudyRoleCode.MEDICAL_EXPERT] == "Medical Monitor"
        assert roles[StudyRoleCode.LABORATORY] == "Central Laboratory"
        assert roles[StudyRoleCode.STATISTICIAN] == "Statistical Analysis Center"
        assert roles[StudyRoleCode.INVESTIGATOR] == "Investigator"

    @pytest.mark.parametrize("code,expected", [
        (StudyRoleCode.SPONSOR, "C70793"),
        (StudyRoleCode.INDEPENDENT_DMC, "C142578"),
        (StudyRoleCode.ADJUDICATION_COMMITTEE, "C78726"),
        (StudyRoleCode.MEDICAL_EXPERT, "C51876"),
        (StudyRoleCode.LABORATORY, "C37984"),
        (StudyRoleCode.INVESTIGATOR, "C25936"),
        (StudyRoleCode.PRINCIPAL_INVESTIGATOR, "C19924"),
        (StudyRoleCode.STATISTICIAN, "C51877"),
        (StudyRoleCode.CRO, "C215662"),
    ])
    def test_role_codes_from_c215480(self, code, expected):
        assert StudyRole(id="r", name="x", code=code).to_dict()["code"]["code"] == expected

    def test_map_role_code_word_boundaries(self):
        assert _map_role_code("Pharmacovigilance") != StudyRoleCode.PRINCIPAL_INVESTIGATOR
        assert _map_role_code("PI") == StudyRoleCode.PRINCIPAL_INVESTIGATOR
        assert _map_role_code("Data Monitoring Committee") == StudyRoleCode.DATA_MONITORING_COMMITTEE

    @pytest.mark.parametrize("name,code", [
        ("Sponsor", "C70793"),
        ("Co-Sponsor", "C215669"),
        ("Independent Data Monitoring Committee", "C142578"),
        ("Data Monitoring Committee", "C142489"),
        ("Clinical Endpoint Committee", "C78726"),
        ("Medical Monitor", "C51876"),
        ("Central Laboratory", "C37984"),
        ("Principal Investigator", "C19924"),
        ("Investigator", "C25936"),
        ("CRO", "C215662"),
    ])
    def test_generator_maps_role_names(self, name, code):
        assert _map_study_role(name)[0] == code

    def test_registry_is_not_a_role(self):
        assert _map_study_role("Registry", "C93453") is None
