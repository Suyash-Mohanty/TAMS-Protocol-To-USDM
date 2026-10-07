"""
Advanced Extraction Schema - Internal types for extraction pipeline.

These types are used during extraction and convert to official USDM types
(from core.usdm_types) when generating final output.

For official USDM types, see: core/usdm_types.py
Schema source: https://github.com/cdisc-org/DDF-RA/blob/main/Deliverables/UML/dataStructure.yml
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum

from core.usdm_types import generate_uuid, Code


CDISC_CODE_SYSTEM = "http://www.cdisc.org"
CDISC_CODE_SYSTEM_VERSION = "2024-09-27"

# CDISC DDF Study Amendment Reason codelist (C207415): preferred term -> code
AMENDMENT_REASON_CODES: Dict[str, str] = {
    "Change In Standard Of Care": "C207600",
    "Change In Strategy": "C207601",
    "IMP Addition": "C207602",
    "Inconsistency and/or Error In The Protocol": "C207603",
    "Investigator/Site Feedback": "C207604",
    "IRB/IEC Feedback": "C207605",
    "Manufacturing Change": "C207606",
    "New Data Available (Other Than Safety Data)": "C207607",
    "New Regulatory Guidance": "C207608",
    "New Safety Information Available": "C207609",
    "Not Applicable": "C48660",
    "Other": "C17649",
    "Protocol Design Error": "C207610",
    "Recruitment Difficulty": "C207611",
    "Regulatory Agency Request To Amend": "C207612",
}

# Keyword fallback for free-text reasons (e.g. legacy "Safety", "Regulatory").
# Order matters: more specific phrases first.
_REASON_KEYWORDS = [
    (("agency request", "health authority", "fda request", "ema request"), "Regulatory Agency Request To Amend"),
    (("irb", "iec", "ethics"), "IRB/IEC Feedback"),
    (("investigator", "site feedback"), "Investigator/Site Feedback"),
    (("safety",), "New Safety Information Available"),
    (("regulat", "guidance"), "New Regulatory Guidance"),
    (("efficacy", "scientific", "new data", "pharmacokinetic"), "New Data Available (Other Than Safety Data)"),
    (("design error",), "Protocol Design Error"),
    (("error", "inconsisten", "clarif", "administrative", "typo", "correction"), "Inconsistency and/or Error In The Protocol"),
    (("strategy", "operational", "business"), "Change In Strategy"),
    (("standard of care",), "Change In Standard Of Care"),
    (("recruit", "enrol"), "Recruitment Difficulty"),
    (("manufactur", "formulation"), "Manufacturing Change"),
    (("imp addition", "new investigational", "add investigational"), "IMP Addition"),
    (("not applicable",), "Not Applicable"),
]

_TERMS_BY_LOWER = {term.lower(): term for term in AMENDMENT_REASON_CODES}


def resolve_amendment_reason(text: Optional[str]) -> Optional[str]:
    """Map a reason string to a C207415 preferred term (None if blank).

    Exact terms (case-insensitive) win; otherwise keywords are matched;
    anything unmatched becomes "Other" so the caller keeps the text as
    otherReason.
    """
    if not text or not str(text).strip():
        return None
    lower = str(text).strip().lower()
    if lower in _TERMS_BY_LOWER:
        return _TERMS_BY_LOWER[lower]
    for keywords, term in _REASON_KEYWORDS:
        if any(k in lower for k in keywords):
            return term
    return "Other"


def build_amendment_reason(term: str, other_text: Optional[str] = None) -> Dict[str, Any]:
    """Build a USDM StudyAmendmentReason dict for a C207415 term."""
    reason: Dict[str, Any] = {
        "id": generate_uuid(),
        "code": {
            "id": generate_uuid(),
            "code": AMENDMENT_REASON_CODES[term],
            "codeSystem": CDISC_CODE_SYSTEM,
            "codeSystemVersion": CDISC_CODE_SYSTEM_VERSION,
            "decode": term,
            "instanceType": "Code",
        },
        "instanceType": "StudyAmendmentReason",
    }
    # DDF00020: otherReason only (and always) when the code is "Other"
    if term == "Other":
        reason["otherReason"] = other_text or "Other"
    return reason


class AmendmentScope(Enum):
    """Scope of a protocol amendment."""
    GLOBAL = "Global"
    COUNTRY_SPECIFIC = "Country Specific"
    SITE_SPECIFIC = "Site Specific"


@dataclass
class AmendmentReason:
    """
    USDM AmendmentReason entity.
    
    Describes why an amendment was made.
    """
    id: str
    code: str  # e.g., "SAFETY", "EFFICACY", "REGULATORY"
    description: str
    instance_type: str = "AmendmentReason"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "code": self.code,
            "description": self.description,
            "instanceType": self.instance_type,
        }


@dataclass
class StudyAmendment:
    """
    USDM StudyAmendment entity.

    Represents a protocol amendment.
    date_values holds pre-serialised GovernanceDate dicts for USDM dateValues[].
    """
    id: str
    number: str  # Amendment number (e.g., "1", "2")
    summary: Optional[str] = None
    effective_date: Optional[str] = None
    scope: AmendmentScope = AmendmentScope.GLOBAL
    reason_ids: List[str] = field(default_factory=list)
    previous_version: Optional[str] = None
    new_version: Optional[str] = None
    date_values: List[Dict[str, Any]] = field(default_factory=list)  # GovernanceDate dicts
    # C207415 preferred terms (see AMENDMENT_REASON_CODES); other_reason is the
    # protocol's wording, used only when primary_reason is "Other"
    primary_reason: Optional[str] = None
    secondary_reasons: List[str] = field(default_factory=list)
    other_reason: Optional[str] = None
    # One dict per Summary of Changes row: sectionNumber, sectionTitle,
    # description, rationale
    changes: List[Dict[str, Any]] = field(default_factory=list)
    instance_type: str = "StudyAmendment"

    def _changes_to_dict(self) -> List[Dict[str, Any]]:
        """Build USDM StudyChange objects from the extracted table rows.

        changedSections[].appliesToId must reference the StudyDefinitionDocument,
        which isn't known at extraction time — the generator rewires it.
        """
        result = []
        for change in self.changes:
            number = (change.get("sectionNumber") or "").strip()
            title = (change.get("sectionTitle") or "").strip()
            description = (change.get("description") or "").strip()
            if not description:
                continue
            name = " ".join(p for p in (f"Section {number}" if number else "", title) if p)
            result.append({
                "id": generate_uuid(),
                "name": name or f"Amendment {self.number} Change",
                "summary": description,
                "rationale": (change.get("rationale") or "").strip() or self.summary or description,
                "changedSections": [{
                    "id": generate_uuid(),
                    "sectionNumber": number or "NA",
                    "sectionTitle": title or "NA",
                    "appliesToId": "",
                    "instanceType": "DocumentContentReference",
                }],
                "instanceType": "StudyChange",
            })
        return result

    def to_dict(self) -> Dict[str, Any]:
        # USDM requires: name, primaryReason, geographicScopes
        primary_term = self.primary_reason or "Other"
        result = {
            "id": self.id,
            "number": self.number,
            "name": f"Amendment {self.number}",  # Required field
            "scope": {
                "id": generate_uuid(),
                "code": self.scope.value,
                "codeSystem": "USDM",
                "codeSystemVersion": "2024-09-27",
                "decode": self.scope.value,
                "instanceType": "Code",
            },
            # Required field — StudyAmendmentReason coded from C207415
            "primaryReason": build_amendment_reason(
                primary_term, self.other_reason or self.summary
            ),
            "geographicScopes": [{  # Required field - at least one
                "id": generate_uuid(),
                "type": {
                    "id": generate_uuid(),
                    "code": self.scope.value,
                    "codeSystem": "USDM",
                    "codeSystemVersion": "2024-09-27",
                    "decode": self.scope.value,
                    "instanceType": "Code",
                },
                "instanceType": "GeographicScope",
            }],
            "instanceType": self.instance_type,
        }
        # summary is required in USDM 4.0
        result["summary"] = self.summary if self.summary else f"Amendment {self.number} to the protocol"
        if self.effective_date:
            result["effectiveDate"] = self.effective_date
        # USDM 4.0 dateValues — structured governance dates for this amendment
        if self.date_values:
            result["dateValues"] = self.date_values
        secondary = [t for t in self.secondary_reasons if t and t != primary_term]
        if secondary:
            result["secondaryReasons"] = [
                build_amendment_reason(t, self.other_reason) for t in dict.fromkeys(secondary)
            ]
        changes = self._changes_to_dict()
        if changes:
            result["changes"] = changes
        if self.reason_ids:
            result["reasonIds"] = self.reason_ids
        if self.previous_version:
            result["previousVersion"] = self.previous_version
        if self.new_version:
            result["newVersion"] = self.new_version
        return result


@dataclass
class Country:
    """
    USDM Country entity.
    
    Represents a country where the study is conducted.
    """
    id: str
    name: str
    code: Optional[str] = None  # ISO 3166-1 alpha-2 or alpha-3
    region: Optional[str] = None  # e.g., "Europe", "North America"
    instance_type: str = "Country"
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "id": self.id,
            "name": self.name,
            "instanceType": self.instance_type,
        }
        if self.code:
            result["code"] = self.code
        if self.region:
            result["region"] = self.region
        return result


@dataclass
class StudySite:
    """
    USDM StudySite entity.
    
    Represents a clinical study site.
    """
    id: str
    name: str
    site_number: Optional[str] = None
    country_id: Optional[str] = None
    city: Optional[str] = None
    instance_type: str = "StudySite"
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "id": self.id,
            "name": self.name,
            "instanceType": self.instance_type,
        }
        if self.site_number:
            result["siteNumber"] = self.site_number
        if self.country_id:
            result["countryId"] = self.country_id
        if self.city:
            result["city"] = self.city
        return result


@dataclass
class GeographicScope:
    """
    USDM GeographicScope entity.
    
    Defines the geographic scope of the study.
    """
    id: str
    name: str
    scope_type: str = "Global"  # Global, Regional, Country
    country_ids: List[str] = field(default_factory=list)
    site_ids: List[str] = field(default_factory=list)
    regions: List[str] = field(default_factory=list)
    instance_type: str = "GeographicScope"
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "id": self.id,
            "name": self.name,
            "scopeType": self.scope_type,
            "instanceType": self.instance_type,
        }
        if self.country_ids:
            result["countryIds"] = self.country_ids
        if self.site_ids:
            result["siteIds"] = self.site_ids
        if self.regions:
            result["regions"] = self.regions
        return result


@dataclass
class AdvancedData:
    """
    Aggregated advanced entities extraction result.
    
    Contains all Phase 8 entities for a protocol.
    """
    amendments: List[StudyAmendment] = field(default_factory=list)
    amendment_reasons: List[AmendmentReason] = field(default_factory=list)
    geographic_scope: Optional[GeographicScope] = None
    countries: List[Country] = field(default_factory=list)
    sites: List[StudySite] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to USDM-compatible dictionary structure."""
        result = {
            "studyAmendments": [a.to_dict() for a in self.amendments],
            "amendmentReasons": [r.to_dict() for r in self.amendment_reasons],
            "countries": [c.to_dict() for c in self.countries],
            "studySites": [s.to_dict() for s in self.sites],
            "summary": {
                "amendmentCount": len(self.amendments),
                "countryCount": len(self.countries),
                "siteCount": len(self.sites),
            }
        }
        if self.geographic_scope:
            result["geographicScope"] = self.geographic_scope.to_dict()
        return result
