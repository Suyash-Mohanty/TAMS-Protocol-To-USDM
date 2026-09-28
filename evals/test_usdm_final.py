"""Eval: End-to-end USDM output — schema completeness and structural checks."""
import pytest
from evals.helpers import load_usdm, get_study_design, get_study_version


@pytest.fixture(scope="module")
def pipeline_usdm(pipeline_output_dir):
    return load_usdm(pipeline_output_dir)


@pytest.fixture(scope="module")
def pipeline_design(pipeline_usdm):
    return get_study_design(pipeline_usdm)


@pytest.fixture(scope="module")
def pipeline_version(pipeline_usdm):
    return get_study_version(pipeline_usdm)


class TestUSDMStructure:
    def test_has_study(self, pipeline_usdm):
        assert "study" in pipeline_usdm, "USDM must have 'study' key"

    def test_has_versions(self, pipeline_usdm):
        versions = pipeline_usdm["study"].get("versions", [])
        assert len(versions) > 0, "Study must have at least one version"

    def test_has_study_designs(self, pipeline_version):
        designs = pipeline_version.get("studyDesigns", [])
        assert len(designs) > 0, "Version must have at least one studyDesign"

    def test_usdm_version_present(self, pipeline_usdm):
        version = pipeline_usdm.get("usdmVersion", "")
        assert version, "usdmVersion should be present"


class TestRequiredSections:
    """Verify all major USDM sections are populated."""

    REQUIRED_SECTIONS = [
        ("epochs", 1),
        ("encounters", 1),
        ("activities", 1),
        ("objectives", 1),
        ("eligibilityCriteria", 1),
        ("scheduleTimelines", 1),
    ]

    @pytest.mark.parametrize("section,min_count", REQUIRED_SECTIONS)
    def test_section_populated(self, pipeline_design, section, min_count):
        items = pipeline_design.get(section, [])
        assert len(items) >= min_count, (
            f"Section '{section}' has {len(items)} items, expected >= {min_count}"
        )

    OPTIONAL_SECTIONS = [
        "indications",
        "estimands",
        "elements",
        "studyCells",
        "population",
    ]

    @pytest.mark.parametrize("section", OPTIONAL_SECTIONS)
    def test_optional_section_exists(self, pipeline_design, section):
        """Optional sections should at least exist as keys (even if empty)."""
        assert section in pipeline_design, f"Section '{section}' missing from studyDesign"


class TestDocumentedBy:
    """Verify study.documentedBy[] (StudyDefinitionDocument) is populated."""

    def test_has_documented_by(self, pipeline_usdm):
        documents = pipeline_usdm["study"].get("documentedBy", [])
        assert len(documents) >= 1, "study.documentedBy must have at least one document"

    def test_document_required_fields(self, pipeline_usdm):
        doc = pipeline_usdm["study"]["documentedBy"][0]
        assert doc.get("name"), "StudyDefinitionDocument.name is required"
        assert doc.get("templateName"), "StudyDefinitionDocument.templateName is required"
        language = doc.get("language") or {}
        assert language.get("code"), "StudyDefinitionDocument.language must be a Code with a code"
        doc_type = doc.get("type") or {}
        assert doc_type.get("code"), "StudyDefinitionDocument.type must be a Code with a code"

    def test_document_version_fields(self, pipeline_usdm):
        doc = pipeline_usdm["study"]["documentedBy"][0]
        versions = doc.get("versions", [])
        if not versions:
            pytest.skip("No StudyDefinitionDocumentVersion extracted for this protocol")
        version = versions[0]
        assert version.get("version"), "StudyDefinitionDocumentVersion.version is required"
        status = version.get("status") or {}
        assert status.get("code"), "StudyDefinitionDocumentVersion.status must be a Code with a code"


class TestMasking:
    """Verify StudyRole.masking (isMasked/text) is well-formed when present.

    maskedRoles only maps onto existing StudyRole entries (e.g. Sponsor,
    Investigator) by name — protocols whose masked parties are all
    non-organizational (e.g. only "Subject") legitimately have no
    StudyRole.masking set, so this test skips rather than fails when none
    are found.
    """

    def test_masking_fields_well_formed(self, pipeline_version):
        roles = pipeline_version.get("roles", [])
        masked = [r for r in roles if r.get("masking")]
        if not masked:
            pytest.skip("No StudyRole.masking set for this protocol")
        for role in masked:
            masking = role["masking"]
            assert isinstance(masking.get("isMasked"), bool), \
                "Masking.isMasked is required and must be boolean"
            assert masking.get("text"), "Masking.text is required"
            assert masking.get("instanceType") == "Masking"


class TestStrength:
    """Verify Substance.strengths[].numerator is well-formed when present.

    AdministrableProduct.ingredients[] is only built when the extraction
    captured both a strength value and a matching substance for a product —
    protocols where products/substances weren't extracted (or extracted
    without a strength) legitimately have no ingredients, so this test
    skips rather than fails when none are found.
    """

    def test_strength_numerator_well_formed(self, pipeline_version):
        products = pipeline_version.get("administrableProducts", [])
        ingredients = [i for p in products for i in p.get("ingredients", [])]
        if not ingredients:
            pytest.skip("No AdministrableProduct.ingredients set for this protocol")
        for ingredient in ingredients:
            role = ingredient.get("role") or {}
            assert role.get("code"), "Ingredient.role is required and must be a Code"
            substance = ingredient.get("substance") or {}
            assert substance.get("name"), "Substance.name is required"
            strengths = substance.get("strengths", [])
            assert len(strengths) >= 1, "Substance.strengths must have at least one entry"
            for strength in strengths:
                numerator = strength.get("numerator") or {}
                assert isinstance(numerator.get("value"), (int, float)), \
                    "Strength.numerator.value is required and must be numeric"
                assert numerator.get("instanceType") in ("Quantity", "Range"), \
                    "Strength.numerator must be a Quantity or Range"


class TestPlannedAge:
    """Verify StudyDesignPopulation.plannedAge (Range) is well-formed when present.

    plannedAge is only built when both a minimum AND maximum age were
    extracted (Range.minValue/maxValue are both required) — protocols that
    only state one bound, or no age range at all, legitimately have no
    plannedAge, so this test skips rather than fails when none is found.
    """

    def test_planned_age_range_well_formed(self, pipeline_design):
        population = pipeline_design.get("population") or {}
        planned_age = population.get("plannedAge")
        if not planned_age:
            pytest.skip("No StudyDesignPopulation.plannedAge set for this protocol")
        assert planned_age.get("instanceType") == "Range"
        assert isinstance(planned_age.get("isApproximate"), bool), \
            "Range.isApproximate is required and must be boolean"
        for bound in ("minValue", "maxValue"):
            quantity = planned_age.get(bound) or {}
            assert isinstance(quantity.get("value"), (int, float)), \
                f"Range.{bound}.value is required and must be numeric"
            assert quantity.get("instanceType") == "Quantity"


class TestIDIntegrity:
    """Verify internal ID references are consistent."""

    def test_epoch_ids_unique(self, pipeline_design):
        epochs = pipeline_design.get("epochs", [])
        ids = [e.get("id") for e in epochs if e.get("id")]
        assert len(ids) == len(set(ids)), f"Duplicate epoch IDs: {ids}"

    def test_encounter_ids_unique(self, pipeline_design):
        encounters = pipeline_design.get("encounters", [])
        ids = [e.get("id") for e in encounters if e.get("id")]
        assert len(ids) == len(set(ids)), f"Duplicate encounter IDs: {ids}"

    def test_activity_ids_unique(self, pipeline_design):
        activities = pipeline_design.get("activities", [])
        ids = [a.get("id") for a in activities if a.get("id")]
        assert len(ids) == len(set(ids)), f"Duplicate activity IDs: {ids}"

    def test_timeline_epoch_refs_valid(self, pipeline_design):
        """Epoch IDs referenced in timeline instances should exist."""
        epoch_ids = {e.get("id") for e in pipeline_design.get("epochs", [])}
        timelines = pipeline_design.get("scheduleTimelines", [])
        bad_refs = []
        for tl in timelines:
            for inst in tl.get("instances", []):
                eid = inst.get("epochId")
                if eid and eid not in epoch_ids:
                    bad_refs.append(eid)
        assert len(bad_refs) == 0, (
            f"Timeline instances reference non-existent epoch IDs: {set(bad_refs)}"
        )

    def test_timeline_encounter_refs_valid(self, pipeline_design):
        """Encounter IDs referenced in timeline instances should exist."""
        enc_ids = {e.get("id") for e in pipeline_design.get("encounters", [])}
        timelines = pipeline_design.get("scheduleTimelines", [])
        bad_refs = []
        for tl in timelines:
            for inst in tl.get("instances", []):
                eid = inst.get("encounterId")
                if eid and eid not in enc_ids:
                    bad_refs.append(eid)
        assert len(bad_refs) == 0, (
            f"Timeline instances reference non-existent encounter IDs: {set(bad_refs)}"
        )
