"""
Interventions Extraction Schema - Internal types for extraction pipeline.

These types are used during extraction and convert to official USDM types
(from core.usdm_types) when generating final output.

For official USDM types, see: core/usdm_types.py
Schema source: https://github.com/cdisc-org/DDF-RA/blob/main/Deliverables/UML/dataStructure.yml
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum

from core.usdm_types import generate_uuid, Code
from core.cdisc_codelists import (
    DOSE_FORM, FREQUENCY, INTERVENTION_TYPE, PRODUCT_DESIGNATION, ROUTE, STUDY_INTERVENTION_ROLE, UNIT,
    lookup as cdisc_lookup, to_code,
)


class RouteOfAdministration(Enum):
    """USDM route of administration codes."""
    ORAL = "Oral"
    INTRAVENOUS = "Intravenous"
    SUBCUTANEOUS = "Subcutaneous"
    INTRAMUSCULAR = "Intramuscular"
    TOPICAL = "Topical"
    INHALATION = "Inhalation"
    INTRANASAL = "Intranasal"
    OPHTHALMIC = "Ophthalmic"
    TRANSDERMAL = "Transdermal"
    RECTAL = "Rectal"
    SUBLINGUAL = "Sublingual"
    OTHER = "Other"


class DoseForm(Enum):
    """USDM dose form codes."""
    TABLET = "Tablet"
    CAPSULE = "Capsule"
    SOLUTION = "Solution"
    SUSPENSION = "Suspension"
    INJECTION = "Injection"
    CREAM = "Cream"
    OINTMENT = "Ointment"
    GEL = "Gel"
    PATCH = "Patch"
    POWDER = "Powder"
    SPRAY = "Spray"
    INHALER = "Inhaler"
    OTHER = "Other"


class InterventionRole(Enum):
    """Study intervention roles; values are CDISC C207417 submission values.

    CONCOMITANT has no C207417 term: permitted/prohibited concomitant
    medications are not study interventions and are not emitted as such.
    """
    UNKNOWN = ""  # Not extracted from source
    INVESTIGATIONAL = "Experimental Intervention"
    COMPARATOR = "Active Comparator"
    PLACEBO = "Placebo"
    RESCUE = "Rescue Medicine"
    BACKGROUND = "Background Treatment"
    CHALLENGE = "Challenge Agent"
    ADDITIONAL_REQUIRED = "Additional Required Treatment"
    DIAGNOSTIC = "Diagnostic"
    CONCOMITANT = "Concomitant Medication"


@dataclass
class Substance:
    """
    USDM Substance entity.
    
    Active pharmaceutical ingredient.
    """
    id: str
    name: str
    description: Optional[str] = None
    codes: List[Dict[str, str]] = field(default_factory=list)  # UNII, CAS, etc.
    instance_type: str = "Substance"
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "id": self.id,
            "name": self.name,
            "instanceType": self.instance_type,
        }
        if self.description:
            result["description"] = self.description
        if self.codes:
            result["codes"] = self.codes
        return result


@dataclass
class Administration:
    """
    USDM Administration entity.

    Describes how a product is administered (dose, route, frequency,
    duration) within a StudyIntervention.
    """
    id: str
    name: str
    dose: Optional[str] = None  # e.g., "15 mg", "100 mg/m2"
    dose_frequency: Optional[str] = None  # e.g., "once daily", "twice daily"
    route: Optional[RouteOfAdministration] = None
    route_text: Optional[str] = None  # protocol wording, resolved against CDISC C66729
    duration: Optional[str] = None  # e.g., "24 weeks", "Until disease progression"
    description: Optional[str] = None
    product_id: Optional[str] = None  # AdministrableProduct administered
    instance_type: str = "Administration"

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "id": self.id,
            "name": self.name,
            "duration": _duration(self.duration),  # required in USDM 4.0
            "instanceType": self.instance_type,
        }
        dose = _quantity(self.dose)
        if dose:
            result["dose"] = dose
        # CDISC lists e.g. "Intranasal Route of Administration" as a NASAL synonym
        route = (cdisc_lookup(ROUTE, self.route_text)
                 or (cdisc_lookup(ROUTE, f"{self.route_text} Route of Administration") if self.route_text else None)
                 or (cdisc_lookup(ROUTE, self.route.value) if self.route else None))
        if route:
            result["route"] = _alias_code(route, ROUTE)
        frequency = cdisc_lookup(FREQUENCY, self.dose_frequency)
        if frequency:
            result["frequency"] = _alias_code(frequency, FREQUENCY)
        if self.product_id:
            result["administrableProductId"] = self.product_id
        # Keep the protocol's own wording for anything not structured above
        # (titration rules, "1 mg reconstituted in 1.1 mL", "once daily", ...)
        details = [self.description]
        match = _QUANTITY_RE.match(self.dose or "")
        if self.dose and (not dose or self.dose[match.end():].strip()):
            details.append(f"Dose: {self.dose}")
        if self.dose_frequency and not frequency:
            details.append(f"Frequency: {self.dose_frequency}")
        text = "; ".join(d for d in details if d)
        if text:
            result["description"] = text
        return result


_QUANTITY_RE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*([A-Za-zµμ%/][^\s,;()]*)?")


def _alias_code(term: Dict[str, Any], codelist_id: str) -> Dict[str, Any]:
    return {
        "id": generate_uuid(),
        "standardCode": {"id": generate_uuid(), **to_code(term, codelist_id), "instanceType": "Code"},
        "standardCodeAliases": [],
        "instanceType": "AliasCode",
    }


def _quantity(text: Optional[str]) -> Optional[Dict[str, Any]]:
    """Quantity from a leading "<number> <CDISC unit>" ("1 mg (reconstituted...)");
    None when the text doesn't start with a number or the unit isn't a CDISC unit."""
    match = _QUANTITY_RE.match(text or "")
    if not match:
        return None
    quantity: Dict[str, Any] = {"id": generate_uuid(), "value": float(match.group(1)), "instanceType": "Quantity"}
    if match.group(2):
        unit = cdisc_lookup(UNIT, match.group(2))
        if not unit:
            return None
        quantity["unit"] = _alias_code(unit, UNIT)
    return quantity


def _duration(text: Optional[str]) -> Dict[str, Any]:
    """USDM Duration: structured quantity when the text is "<number> <time unit>",
    otherwise the protocol text with durationWillVary set."""
    quantity = _quantity(text)
    duration: Dict[str, Any] = {
        "id": generate_uuid(),
        "text": text or "Not specified in protocol",
        "durationWillVary": quantity is None,
        "instanceType": "Duration",
    }
    if quantity:
        duration["quantity"] = quantity
    else:
        duration["reasonDurationWillVary"] = text or "Not specified in protocol"
    return duration


@dataclass
class AdministrableProduct:
    """
    USDM AdministrableProduct entity.
    
    A product that can be administered to subjects.
    """
    id: str
    name: str
    description: Optional[str] = None
    dose_form: Optional[DoseForm] = None
    strength_value: Optional[float] = None  # numerator value, e.g. 15.0 for "15 mg"
    strength_unit: Optional[str] = None  # numerator unit, e.g. "mg"
    strength_denominator_value: Optional[float] = None  # e.g. 1.0 for "1 mg/mL"
    strength_denominator_unit: Optional[str] = None  # e.g. "mL"
    strength_name: Optional[str] = None  # distinct strength label if the protocol names one, e.g. "High Dose"
    dose_form_text: Optional[str] = None  # protocol wording, resolved against CDISC C66726
    designation: Optional[str] = None  # "IMP" or "NIMP" (CDISC C207418)
    active_ingredients: List[str] = field(default_factory=list)  # LLM-listed ingredient names (linking only)
    substance_ids: List[str] = field(default_factory=list)
    manufacturer: Optional[str] = None
    instance_type: str = "AdministrableProduct"
    
    def _dose_form_code(self) -> Dict[str, Any]:
        """Resolve the dose form against CDISC codelist C66726.

        The protocol's own wording is tried first (most specific, e.g.
        "Lyophilized powder for solution for injection"), falling back to a
        broader term of the same wording ("nasal powder" -> POWDER), then the
        coarse enum value; a product whose form isn't stated is UNKNOWN.
        """
        term = (
            cdisc_lookup(DOSE_FORM, self.dose_form_text)
            or cdisc_lookup(DOSE_FORM, self.dose_form_text, allow_broader=True)
            or (cdisc_lookup(DOSE_FORM, self.dose_form.value) if self.dose_form and self.dose_form != DoseForm.OTHER else None)
            or cdisc_lookup(DOSE_FORM, "UNKNOWN")
        )
        return {"id": generate_uuid(), **to_code(term, DOSE_FORM), "instanceType": "Code"}

    def to_dict(self) -> Dict[str, Any]:
        dose_form = self._dose_form_code()
        designation = cdisc_lookup(PRODUCT_DESIGNATION, self.designation) or cdisc_lookup(PRODUCT_DESIGNATION, "IMP")

        result = {
            "id": self.id,
            "name": self.name,
            "administrableDoseForm": {  # Required field (AliasCode)
                "id": generate_uuid(),
                "standardCode": dose_form,
                "standardCodeAliases": [],
                "instanceType": "AliasCode",
            },
            # Required field — IMP (investigational or reference/comparator)
            # vs NIMP/AxMP (auxiliary: challenge agent, rescue, background)
            "productDesignation": {
                "id": generate_uuid(),
                **to_code(designation, PRODUCT_DESIGNATION),
                "instanceType": "Code",
            },
            "instanceType": self.instance_type,
        }
        if self.description:
            result["description"] = self.description
        # strengthValue/strengthUnit/strengthName and substanceIds aren't real
        # AdministrableProduct fields in USDM 4.0 (strength lives on
        # Substance.strengths[].numerator/name, reached via ingredients[]) —
        # the generator reads these staging keys to build ingredients[]
        # and strips them afterward.
        if self.strength_value is not None:
            result["strengthValue"] = self.strength_value
            if self.strength_unit:
                result["strengthUnit"] = self.strength_unit
            if self.strength_denominator_value is not None:
                result["strengthDenominatorValue"] = self.strength_denominator_value
                if self.strength_denominator_unit:
                    result["strengthDenominatorUnit"] = self.strength_denominator_unit
            if self.strength_name:
                result["strengthName"] = self.strength_name
        if self.substance_ids:
            result["substanceIds"] = self.substance_ids
        if self.manufacturer:
            result["manufacturer"] = self.manufacturer
        return result


@dataclass
class MedicalDevice:
    """
    USDM MedicalDevice entity.
    
    A medical device used in the study.
    """
    id: str
    name: str
    description: Optional[str] = None
    device_identifier: Optional[str] = None
    manufacturer: Optional[str] = None
    instance_type: str = "MedicalDevice"
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "id": self.id,
            "name": self.name,
            "instanceType": self.instance_type,
        }
        if self.description:
            result["description"] = self.description
        if self.device_identifier:
            result["deviceIdentifier"] = self.device_identifier
        if self.manufacturer:
            result["manufacturer"] = self.manufacturer
        return result


@dataclass
class StudyIntervention:
    """
    USDM StudyIntervention entity.
    
    High-level description of an intervention in the study.
    """
    id: str
    name: str
    description: Optional[str] = None
    role: InterventionRole = InterventionRole.INVESTIGATIONAL
    intervention_type: Optional[str] = None  # e.g. "Drug", "Biologic", "Device" (CDISC C99078)
    label: Optional[str] = None
    product_ids: List[str] = field(default_factory=list)  # Links to AdministrableProduct
    administration_ids: List[str] = field(default_factory=list)  # Links to Administration
    codes: List[Dict[str, str]] = field(default_factory=list)  # ATC codes, etc.
    instance_type: str = "StudyIntervention"
    
    def to_dict(self) -> Dict[str, Any]:
        role = (
            (cdisc_lookup(STUDY_INTERVENTION_ROLE, self.role.value) if self.role else None)
            or cdisc_lookup(STUDY_INTERVENTION_ROLE, InterventionRole.INVESTIGATIONAL.value)
        )
        # Intervention type (C99078) is what the intervention is, not its role;
        # most protocol interventions are drugs
        itype = cdisc_lookup(INTERVENTION_TYPE, self.intervention_type) or cdisc_lookup(INTERVENTION_TYPE, "DRUG")

        result = {
            "id": self.id,
            "name": self.name,
            "type": {"id": generate_uuid(), **to_code(itype, INTERVENTION_TYPE), "instanceType": "Code"},
            "role": {"id": generate_uuid(), **to_code(role, STUDY_INTERVENTION_ROLE), "instanceType": "Code"},
            "instanceType": self.instance_type,
        }
        if self.description:
            result["description"] = self.description
        if self.label:
            result["label"] = self.label
        if self.product_ids:
            result["productIds"] = self.product_ids
        if self.administration_ids:
            result["administrationIds"] = self.administration_ids
        if self.codes:
            result["codes"] = self.codes
        return result


@dataclass
class InterventionsData:
    """
    Aggregated interventions extraction result.
    
    Contains all Phase 5 entities for a protocol.
    """
    interventions: List[StudyIntervention] = field(default_factory=list)
    products: List[AdministrableProduct] = field(default_factory=list)
    administrations: List[Administration] = field(default_factory=list)
    substances: List[Substance] = field(default_factory=list)
    devices: List[MedicalDevice] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to USDM-compatible dictionary structure."""
        return {
            "studyInterventions": [i.to_dict() for i in self.interventions],
            "administrableProducts": [p.to_dict() for p in self.products],
            "administrations": [a.to_dict() for a in self.administrations],
            "substances": [s.to_dict() for s in self.substances],
            "medicalDevices": [d.to_dict() for d in self.devices],
            "summary": {
                "interventionCount": len(self.interventions),
                "productCount": len(self.products),
                "deviceCount": len(self.devices),
            }
        }
