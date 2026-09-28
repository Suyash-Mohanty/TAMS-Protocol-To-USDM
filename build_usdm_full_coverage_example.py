"""Build docs/usdm_full_coverage_example.json.

A synthetic maximal-coverage USDM v4.0 reference: one hand-constructed
entity of every entity type the extraction pipeline and USDMGeneratorAgent
currently support, run through the real generator code (not reimplemented).

This is a snapshot of *current capability*, not a realistic protocol —
narrative/descriptive text fields (name, text, description, label, etc.)
are minimal generic placeholders. Fields the generator needs a real typed
value for to exercise its logic (IDs, codes, numbers, booleans, dates) are
filled in for real, since leaving those empty would just make the entity
fail to place or skip the feature entirely.

Re-run any time the generator's capabilities change:
    python build_usdm_full_coverage_example.py
"""
import sys
import uuid
from pathlib import Path
from typing import Any, Dict

from agents.base import AgentTask
from agents.context_store import ContextEntity, ContextStore, EntityProvenance
from agents.support.usdm_generator_agent import USDMGeneratorAgent

from extraction.advanced.schema import GeographicScope, StudyAmendment
from extraction.biomedical_concepts.schema import (
    BiomedicalConcept,
    BiomedicalConceptCategory,
    BiomedicalConceptProperty,
)
from extraction.document_structure.schema import (
    CommentAnnotation,
    StudyDefinitionDocumentVersion,
)
from extraction.eligibility.schema import (
    CriterionCategory,
    EligibilityCriterion,
    EligibilityCriterionItem,
    StudyDesignPopulation,
)
from extraction.interventions.schema import (
    AdministrableProduct,
    DoseForm,
    InterventionRole,
    MedicalDevice,
    Substance,
    StudyIntervention,
)
from extraction.metadata.schema import (
    GovernanceDate,
    Indication,
    IdentifierType,
    Organization,
    OrganizationType,
    StudyIdentifier,
    StudyPhase,
    StudyRole,
    StudyRoleCode,
    StudyTitle,
    TitleType,
)
from extraction.narrative.schema import (
    Abbreviation,
    NarrativeContentItem,
    StudyDefinitionDocument,
)
from extraction.objectives.schema import (
    AnalysisPopulation,
    Endpoint,
    EndpointLevel,
    Estimand,
    Objective,
    ObjectiveLevel,
)
from extraction.scheduling.schema import ScheduleTimelineExit
from extraction.studydesign.schema import (
    ArmType,
    BlindingSchema,
    InterventionalStudyDesign,
    StudyArm,
    StudyCell,
    StudyElement,
)


def _entity(store: ContextStore, entity_type: str, data: Dict[str, Any]) -> None:
    if "id" not in data:
        data["id"] = f"{entity_type}_{uuid.uuid4().hex[:8]}"
    store.add_entity(ContextEntity(
        id=data["id"],
        entity_type=entity_type,
        data=data,
        provenance=EntityProvenance(
            entity_id=data["id"],
            source_agent_id="build_usdm_full_coverage_example",
            confidence_score=1.0,
        ),
    ))


def build_store() -> ContextStore:
    store = ContextStore()

    # -- Organizations & roles ------------------------------------------------
    _entity(store, "organization", Organization(
        id="org_sponsor", name="Sample Sponsor",
        type=OrganizationType.PHARMACEUTICAL_COMPANY,
    ).to_dict())
    _entity(store, "organization", Organization(
        id="org_cro", name="Sample CRO", type=OrganizationType.CRO,
    ).to_dict())
    _entity(store, "study_role", StudyRole(
        id="role_sponsor", name="Sponsor", code=StudyRoleCode.SPONSOR,
        organization_ids=["org_sponsor"],
    ).to_dict())
    _entity(store, "study_role", StudyRole(
        id="role_investigator", name="Investigator",
        code=StudyRoleCode.INVESTIGATOR, organization_ids=["org_cro"],
    ).to_dict())

    # -- Metadata / identity ---------------------------------------------------
    _entity(store, "metadata", {
        "id": "metadata_1", "name": "Sample Study", "description": "",
        "label": "", "versionIdentifier": "1",
    })
    _entity(store, "study_identifier", StudyIdentifier(
        id="sid_1", text="SAMPLE-001", scope_id="org_sponsor",
        identifier_type=IdentifierType.SPONSOR_PROTOCOL,
    ).to_dict())
    _entity(store, "study_phase", StudyPhase(phase="Phase 2").to_dict())
    _entity(store, "study_title", StudyTitle(
        id="title_1", text="Sample Study Title", type=TitleType.OFFICIAL,
    ).to_dict())
    _entity(store, "indication", Indication(id="ind_1", name="Sample Indication").to_dict())
    _entity(store, "governance_date", GovernanceDate(
        id="gd_1", name="Protocol Version Date", date="2026-01-15",
        type_code="C99906", type_decode="Protocol Version Date",
    ).to_dict())

    # -- Study design -----------------------------------------------------------
    _entity(store, "study_design", InterventionalStudyDesign(
        id="design_1", name="", blinding_schema=BlindingSchema.DOUBLE_BLIND,
        masked_roles=["Investigator"], trial_intent_types=["Treatment"],
        therapeutic_areas=["Oncology"],
    ).to_dict())
    _entity(store, "study_arm", StudyArm(
        id="arm_exp", name="Experimental Arm", arm_type=ArmType.EXPERIMENTAL,
    ).to_dict())
    _entity(store, "study_arm", StudyArm(
        id="arm_pbo", name="Placebo Arm", arm_type=ArmType.PLACEBO_COMPARATOR,
    ).to_dict())
    _entity(store, "epoch", {"id": "epoch_screen", "name": "Screening", "instanceType": "Epoch"})
    _entity(store, "epoch", {"id": "epoch_tx", "name": "Treatment", "instanceType": "Epoch"})
    _entity(store, "epoch", {"id": "epoch_fu", "name": "Follow-up", "instanceType": "Epoch"})
    _entity(store, "study_element", StudyElement(id="elem_1", name="Treatment Element").to_dict())
    _entity(store, "study_cell", StudyCell(
        id="cell_exp", arm_id="arm_exp", epoch_id="epoch_tx", element_ids=["elem_1"],
    ).to_dict())
    _entity(store, "study_cell", StudyCell(
        id="cell_pbo", arm_id="arm_pbo", epoch_id="epoch_tx", element_ids=["elem_1"],
    ).to_dict())

    # -- Eligibility --------------------------------------------------------------
    _entity(store, "criterion_item", EligibilityCriterionItem(
        id="eci_inc", name="Inclusion Item 1", text="Sample inclusion criterion text.",
    ).to_dict())
    _entity(store, "criterion_item", EligibilityCriterionItem(
        id="eci_exc", name="Exclusion Item 1", text="Sample exclusion criterion text.",
    ).to_dict())
    _entity(store, "eligibility_criterion", EligibilityCriterion(
        id="crit_inc", identifier="I1", category=CriterionCategory.INCLUSION,
        criterion_item_id="eci_inc",
    ).to_dict())
    _entity(store, "eligibility_criterion", EligibilityCriterion(
        id="crit_exc", identifier="E1", category=CriterionCategory.EXCLUSION,
        criterion_item_id="eci_exc",
    ).to_dict())
    _entity(store, "study_population", StudyDesignPopulation(
        id="pop_1", name="Study Population",
        planned_minimum_age="P18Y", planned_maximum_age="P65Y",
        planned_age_is_approximate=False,
        criterion_ids=["crit_inc", "crit_exc"],
    ).to_dict())

    # -- Activities / encounters / SoA tick data ---------------------------------
    _entity(store, "activity", {"id": "act_1", "name": "Vital Signs", "instanceType": "Activity"})
    _entity(store, "encounter", {
        "id": "enc_screen", "name": "Screening Visit", "epochId": "epoch_screen",
        "instanceType": "Encounter",
    })
    _entity(store, "encounter", {
        "id": "enc_tx", "name": "Treatment Visit", "epochId": "epoch_tx",
        "instanceType": "Encounter",
    })
    _entity(store, "scheduled_instance", {"id": "si_1", "encounterId": "enc_screen", "activityId": "act_1"})
    _entity(store, "scheduled_instance", {"id": "si_2", "encounterId": "enc_tx", "activityId": "act_1"})
    _entity(store, "schedule_exit", ScheduleTimelineExit(id="exit_1", name="Early Termination").to_dict())

    # -- Interventions & products -------------------------------------------------
    _entity(store, "substance", Substance(id="sub_1", name="Sample Active Ingredient").to_dict())
    _entity(store, "administrable_product", AdministrableProduct(
        id="prod_1", name="Study Drug A Tablet", dose_form=DoseForm.TABLET,
        strength_value=100.0, strength_unit="mg", substance_ids=["sub_1"],
    ).to_dict())
    _entity(store, "medical_device", MedicalDevice(id="dev_1", name="Sample Injector Device").to_dict())
    _entity(store, "study_intervention", StudyIntervention(
        id="interv_1", name="Study Drug A", role=InterventionRole.INVESTIGATIONAL,
    ).to_dict())
    _entity(store, "study_intervention", StudyIntervention(
        id="interv_2", name="Placebo", role=InterventionRole.PLACEBO,
    ).to_dict())

    # -- Objectives / endpoints / estimands / analysis populations ---------------
    _entity(store, "analysis_population", AnalysisPopulation(
        id="ap_1", name="Intent-to-Treat Population", level="ITT",
    ).to_dict())
    _entity(store, "objective", Objective(
        id="obj_1", name="", text="Sample primary objective.", level=ObjectiveLevel.PRIMARY,
    ).to_dict())
    _entity(store, "objective", Objective(
        id="obj_2", name="", text="Sample secondary objective.", level=ObjectiveLevel.SECONDARY,
    ).to_dict())
    _entity(store, "endpoint", Endpoint(
        id="ep_1", name="Primary Endpoint", text="Sample primary endpoint.",
        level=EndpointLevel.PRIMARY, objective_id="obj_1",
    ).to_dict())
    _entity(store, "endpoint", Endpoint(
        id="ep_2", name="Secondary Endpoint", text="Sample secondary endpoint.",
        level=EndpointLevel.SECONDARY, objective_id="obj_2",
    ).to_dict())
    _entity(store, "estimand", Estimand(
        id="est_1", name="Sample Estimand", analysis_population_id="ap_1",
        variable_of_interest_id="ep_1", intervention_ids=["interv_1"],
    ).to_dict())

    # -- Biomedical concepts -------------------------------------------------------
    _entity(store, "biomedical_concept_category", BiomedicalConceptCategory(
        id="bcc_1", name="Vital Signs", label="Vital Signs", bc_ids=["bc_1"],
    ).to_dict())
    _entity(store, "biomedical_concept", BiomedicalConcept(
        id="bc_1", name="Vital Signs", label="Vital Signs", category_ids=["bcc_1"],
        properties=[BiomedicalConceptProperty(
            id="bcp_1", name="Systolic Blood Pressure", label="Systolic Blood Pressure",
        )],
    ).to_dict())

    # -- Narrative / document structure --------------------------------------------
    _entity(store, "narrative_content_item", NarrativeContentItem(
        id="nci_1", name="Section 1", text="Sample narrative text.", order=1,
    ).to_dict())
    _entity(store, "abbreviation", Abbreviation(
        id="abbr_1", abbreviated_text="AE", expanded_text="Adverse Event",
    ).to_dict())
    _entity(store, "comment_annotation", CommentAnnotation(
        id="ca_1", text="Sample footnote text.",
    ).to_dict())
    _entity(store, "study_definition_document", StudyDefinitionDocument(
        id="doc_1", name="Protocol", document_type="Protocol", language="en",
        template_name="SPONSOR",
    ).to_dict())
    _entity(store, "document_version", StudyDefinitionDocumentVersion(
        id="docver_1", version_number="1.0", status="Final",
    ).to_dict())

    # -- Amendments / geographic scope ----------------------------------------------
    _entity(store, "study_amendment", StudyAmendment(id="amend_1", number="1").to_dict())
    _entity(store, "geographic_scope", GeographicScope(
        id="geo_1", name="Global Scope", scope_type="Global",
    ).to_dict())

    return store


def main() -> int:
    repo_root = Path(__file__).resolve().parent
    output_path = repo_root / "docs" / "usdm_full_coverage_example.json"

    store = build_store()
    agent = USDMGeneratorAgent()
    agent.initialize()
    agent.set_context_store(store)

    task = AgentTask(
        task_id="build-full-coverage-example",
        agent_id="usdm-generator",
        task_type="usdm_generate",
        input_data={"output_path": str(output_path)},
    )
    result = agent.execute(task)

    print(f"success: {result.success}")
    print(f"entity_count: {result.data.get('entity_count')}")
    print(f"entity_types_included: {result.data.get('entity_types_included')}")
    print(f"schema_valid: {result.data.get('schema_valid')}")
    issues = result.data.get("semantic_issues") or []
    print(f"semantic_issues ({len(issues)}):")
    for issue in issues:
        print(f"  - {issue}")
    if result.error:
        print(f"error: {result.error}")
    print(f"output written to: {output_path}")

    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
