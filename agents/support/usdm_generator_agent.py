"""
USDM Generator Agent - Builds USDM v4.0 JSON from Context Store entities.

Queries the Context Store for all extracted entities and assembles them
into the USDM v4.0 hierarchy:
  Study → StudyVersion → StudyDesign → (arms, epochs, activities, etc.)
"""

import json
import logging
import os
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple

from agents.base import AgentCapabilities, AgentResult, AgentState, AgentTask, BaseAgent
from core.evs_client import find_ct_entry
from core.cdisc_codelists import UNIT as UNIT_CODELIST, codelist_for, conform_code, lookup as cdisc_lookup, to_code

logger = logging.getLogger(__name__)


# Internal properties that should NOT appear in the final USDM JSON.
# These are added by extraction, reconciliation, enrichment, and validation agents.
_INTERNAL_PROPERTIES = {
    "raw",                      # raw extracted text (provenance)
    "source",                   # source agent/page info
    "_reconciled",              # reconciliation flag
    "_sources",                 # reconciliation source list
    "_enrichment_confidence",   # enrichment metadata
    "_enrichment_source",       # enrichment metadata
    "_validation_fixes",        # validation auto-fix records
    "order",                    # internal ordering (not in USDM schema)
    "entity_type",              # internal type tag (already encoded in placement)
}

# Estimand extension properties that are NOT in the USDM v4.0 schema.
# These are informational duplicates — the real data is already in the
# proper USDM fields (interventionIds, analysisPopulationId,
# variableOfInterestId, populationSummary).
_ESTIMAND_EXTRA_PROPERTIES = {
    "treatment",                # text description → already in interventionIds
    "analysisPopulation",       # text description → already in analysisPopulationId
    "variableOfInterest",       # text description → already in variableOfInterestId
    "summaryMeasure",           # text description → already folded into populationSummary
}

# Per-entity-type properties to strip from the USDM output.
# These are either internal extensions or properties not in the v4.0 schema.
_ENTITY_EXTRA_PROPERTIES: Dict[str, set] = {
    "estimand": _ESTIMAND_EXTRA_PROPERTIES,
    "narrative_content": {"childIds", "sectionNumber", "sectionTitle", "sectionType"},
    "narrative_content_item": {"childIds", "sectionNumber", "sectionTitle", "sectionType"},
    "study_population": {"criteria"},
    # StudyIdentifier: "identifierType" and "type" not in USDM 4.0 schema (DDF00125)
    "study_identifier": {"identifierType", "type"},
    "objective": {"endpointIds"},  # endpoints live at StudyDesign level, not nested
    "study_intervention": {"administrationIds", "productIds", "codes"},
    "comment_annotation": {"annotationType", "pageNumber", "sourceSection"},
    "schedule_exit": {"description", "exitType", "name"},
    "study_amendment": {
        "effectiveDate", "newVersion", "previousVersion", "reasonIds", "scope",
    },
    "amendment": {
        "effectiveDate", "newVersion", "previousVersion", "reasonIds", "scope",
    },
    # Encounter: "epochId" not in USDM 4.0 Encounter schema (DDF00125)
    "encounter": {"epochId"},
    # BiomedicalConcept: "categories" not in USDM 4.0 (use bcCategories at version level)
    "biomedical_concept": {"categories", "sourceActivity"},
    # BiomedicalConceptCategory: "bcIds" not in USDM 4.0 schema (DDF00125)
    "biomedical_concept_category": {"bcIds"},
    # AnalysisPopulation: "level" not in USDM 4.0 schema (DDF00125)
    "analysis_population": {"level"},
    # MedicalDevice: extra properties not in USDM 4.0 schema (DDF00125)
    "medical_device": {"codes", "deviceType", "manufacturer", "modelNumber"},
    # AdministrableProduct: extra properties not in USDM 4.0 schema (DDF00125).
    # strengthValue/strengthUnit/substanceIds are staging keys popped by the
    # custom administrable_product handling below (used to build
    # ingredients[] via _link_substances_to_products), not stripped here.
    "administrable_product": {"manufacturer", "strength"},
}


def _is_code_object(d: Dict[str, Any]) -> bool:
    """Check if a dict looks like a USDM Code object."""
    return "code" in d and ("codeSystem" in d or "decode" in d)


def _normalize_epoch_name(name: str) -> str:
    """Normalize an epoch name for comparison.

    Strips Unicode superscript/subscript digits and common footnote markers
    (e.g. ``UNS¹ EOS or ET²`` → ``uns eos or et``), collapses whitespace,
    and normalises hyphens/underscores so header-structure names match the
    cleaned USDM epoch names.
    """
    # Strip Unicode superscript digits (U+00B9, U+00B2, U+00B3, U+2070-U+2079)
    # and subscript digits (U+2080-U+2089), plus common footnote chars like * † ‡ §
    cleaned = re.sub(r'[\u00B9\u00B2\u00B3\u2070-\u2079\u2080-\u2089*†‡§¶]', '', name)
    # Also strip letter superscripts (ᵃ-ᵛ range U+1D43-U+1D5B)
    cleaned = re.sub(r'[\u1D43-\u1D5B]', '', cleaned)
    # Normalise hyphens and underscores to a single space
    cleaned = re.sub(r'[-_]', ' ', cleaned)
    # Collapse whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip().lower()
    return cleaned


def _ensure_code_id(d: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure a USDM Code object has all required fields.

    Required by CORE engine: id, code, codeSystem, codeSystemVersion,
    decode, instanceType.
    """
    if not d.get("id"):
        d["id"] = str(uuid.uuid4()).replace("-", "_")
    if "instanceType" not in d:
        d["instanceType"] = "Code"
    if "codeSystem" not in d:
        d["codeSystem"] = "http://www.cdisc.org"
    if "codeSystemVersion" not in d:
        d["codeSystemVersion"] = "2024-09-27"
    if "decode" not in d:
        d["decode"] = d.get("code", "")
    return d


# ISO 639-1 language codes/names accepted for StudyDefinitionDocument.language.
# This is a small, fixed vocabulary — not a CDISC/NCI codelist — so it is
# resolved locally rather than via the NCI EVS lookup used for `type`/`status`.
_ISO_LANGUAGE_CODES = {
    "en": "English", "fr": "French", "de": "German", "es": "Spanish",
    "it": "Italian", "pt": "Portuguese", "nl": "Dutch", "ja": "Japanese",
    "zh": "Chinese", "ko": "Korean", "ru": "Russian", "pl": "Polish",
}
_ISO_LANGUAGE_NAME_TO_CODE = {name.lower(): code for code, name in _ISO_LANGUAGE_CODES.items()}


# ISO 3166-1 alpha-2 -> (alpha-3, English short name) for common clinical-trial
# countries. Like _ISO_LANGUAGE_CODES, this is a small, fixed vocabulary
# resolved locally rather than via a live lookup — countries not in this map
# are skipped (logged) rather than fabricated.
_ISO_COUNTRY_CODES = {
    "US": ("USA", "United States of America"),
    "CA": ("CAN", "Canada"),
    "MX": ("MEX", "Mexico"),
    "GB": ("GBR", "United Kingdom of Great Britain and Northern Ireland"),
    "IE": ("IRL", "Ireland"),
    "FR": ("FRA", "France"),
    "DE": ("DEU", "Germany"),
    "ES": ("ESP", "Spain"),
    "IT": ("ITA", "Italy"),
    "PT": ("PRT", "Portugal"),
    "NL": ("NLD", "Netherlands"),
    "BE": ("BEL", "Belgium"),
    "CH": ("CHE", "Switzerland"),
    "AT": ("AUT", "Austria"),
    "SE": ("SWE", "Sweden"),
    "NO": ("NOR", "Norway"),
    "DK": ("DNK", "Denmark"),
    "FI": ("FIN", "Finland"),
    "PL": ("POL", "Poland"),
    "CZ": ("CZE", "Czechia"),
    "HU": ("HUN", "Hungary"),
    "RO": ("ROU", "Romania"),
    "GR": ("GRC", "Greece"),
    "RU": ("RUS", "Russian Federation"),
    "UA": ("UKR", "Ukraine"),
    "TR": ("TUR", "Turkiye"),
    "JP": ("JPN", "Japan"),
    "CN": ("CHN", "China"),
    "KR": ("KOR", "Korea, Republic of"),
    "IN": ("IND", "India"),
    "AU": ("AUS", "Australia"),
    "NZ": ("NZL", "New Zealand"),
    "BR": ("BRA", "Brazil"),
    "AR": ("ARG", "Argentina"),
    "CL": ("CHL", "Chile"),
    "CO": ("COL", "Colombia"),
    "ZA": ("ZAF", "South Africa"),
    "IL": ("ISR", "Israel"),
    "SG": ("SGP", "Singapore"),
    "TW": ("TWN", "Taiwan, Province of China"),
}
_ISO_COUNTRY_NAME_TO_ENTRY = {
    name.lower(): entry for code, entry in _ISO_COUNTRY_CODES.items() for name in (entry[1], code)
}


def _build_country_alias_code(country: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Build a USDM AliasCode for GeographicScope.code from a Country entity.

    Resolves via the alpha-2 `code` field first, falling back to matching by
    `name`. Returns None (caller logs and skips) if the country isn't in the
    fixed vocabulary above — never fabricates an ISO code.
    """
    code2 = str(country.get("code") or "").upper()
    entry = _ISO_COUNTRY_CODES.get(code2)
    if entry is None:
        name = str(country.get("name") or "").lower()
        entry = _ISO_COUNTRY_NAME_TO_ENTRY.get(name)
    if entry is None:
        return None
    alpha3, full_name = entry
    return {
        "id": str(uuid.uuid4()),
        "standardCode": {
            "id": str(uuid.uuid4()),
            "code": alpha3,
            "codeSystem": "ISO 3166 1 alpha3",
            "codeSystemVersion": "2020-08",
            "decode": full_name,
            "instanceType": "Code",
        },
        "standardCodeAliases": [],
        "instanceType": "AliasCode",
    }


_GEO_SCOPE_TYPE_CODES = {
    "global": ("C68846", "Global"),
    "country": ("C25464", "Country"),
    "region": ("C41129", "Region"),
}


def _resolve_geographic_scope(raw: Dict[str, Any],
                               countries_by_id: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Build real USDM GeographicScope object(s) from a staged geographic_scope entity.

    Global -> one object with no code. Country (or any scope naming specific
    countries, e.g. "Multi-national") -> one object per resolvable country
    (unresolvable countries are skipped and logged). Region with no countries
    -> no authoritative region-code source exists today, so it's skipped and
    logged rather than fabricated, matching the masking-link "don't invent
    codes" rule.
    """
    scope_type = str(raw.get("scopeType") or "Global").strip().lower()
    country_ids = raw.get("countryIds") or []

    if country_ids:
        # The LLM's scope-type label varies ("Country", "Multi-national",
        # "Multinational", etc.) but a non-empty countryIds list is the real
        # signal — that's the only way to carry the actual extracted country
        # data into valid USDM, so it takes priority over the label.
        code, decode = _GEO_SCOPE_TYPE_CODES["country"]
        type_obj = {
            "id": str(uuid.uuid4()),
            "code": code,
            "codeSystem": "http://www.cdisc.org",
            "codeSystemVersion": "2024-09-27",
            "decode": decode,
            "instanceType": "Code",
        }
        resolved = []
        for country_id in country_ids:
            country = countries_by_id.get(country_id)
            if country is None:
                logger.warning(
                    "geographic_scope references countryId %r with no matching "
                    "country entity; skipping", country_id,
                )
                continue
            alias = _build_country_alias_code(country)
            if alias is None:
                logger.warning(
                    "Country %r has no resolvable ISO 3166-1 alpha-3 code; "
                    "skipping rather than fabricating one", country.get("name"),
                )
                continue
            resolved.append({
                "id": str(uuid.uuid4()),
                "type": type_obj,
                "code": alias,
                "instanceType": "GeographicScope",
            })
        return resolved

    if scope_type == "region":
        logger.warning(
            "geographic_scope type 'Region' has no authoritative region-code "
            "source; skipping rather than fabricating one",
        )
        return []

    code, decode = _GEO_SCOPE_TYPE_CODES.get(scope_type, _GEO_SCOPE_TYPE_CODES["global"])
    type_obj = {
        "id": str(uuid.uuid4()),
        "code": code,
        "codeSystem": "http://www.cdisc.org",
        "codeSystemVersion": "2024-09-27",
        "decode": decode,
        "instanceType": "Code",
    }
    return [{
        "id": str(uuid.uuid4()),
        "type": type_obj,
        "code": None,
        "instanceType": "GeographicScope",
    }]


def _link_geographic_scopes(usdm: Dict[str, Any]) -> None:
    """Attach staged geographic_scope/country entities to the real v4.0
    GeographicScope locations: StudyAmendment.geographicScopes[] (including
    each amendment's own embedded dateValues[]) and study.versions[0].dateValues[].

    geographic_scope is extracted once per protocol, not per-amendment/date,
    so the same resolved list is attached uniformly to every amendment and
    governance date. If nothing resolves (e.g. Country scope with no matching
    Country entity), the existing synthesized/defaulted placeholder behavior
    in _fix_required_fields()/_fix_governance_dates() is left untouched.
    """
    study = usdm.get("study", {})
    pending_scopes = study.pop("_pendingGeographicScopes", [])
    countries_by_id = study.pop("_pendingCountries", {})
    if not pending_scopes:
        return

    resolved: List[Dict[str, Any]] = []
    for raw in pending_scopes:
        resolved.extend(_resolve_geographic_scope(raw, countries_by_id))
    if not resolved:
        return

    try:
        version = study["versions"][0]
    except (KeyError, IndexError):
        return

    # Each location gets its own copy with fresh ids — USDM objects are
    # nested by value, so sharing one list would duplicate ids
    for amend in version.get("amendments", []):
        amend["geographicScopes"] = _copy_with_new_ids(resolved)
        for dv in amend.get("dateValues", []):
            dv["geographicScopes"] = _copy_with_new_ids(resolved)
    for gd in version.get("dateValues", []):
        gd["geographicScopes"] = _copy_with_new_ids(resolved)
    for document in study.get("documentedBy", []):
        for doc_version in document.get("versions", []):
            for gd in doc_version.get("dateValues", []):
                gd["geographicScopes"] = _copy_with_new_ids(resolved)


def _copy_with_new_ids(value: Any) -> Any:
    """Deep copy of a nested USDM structure with every "id" regenerated."""
    if isinstance(value, list):
        return [_copy_with_new_ids(v) for v in value]
    if isinstance(value, dict):
        return {k: (str(uuid.uuid4()) if k == "id" else _copy_with_new_ids(v)) for k, v in value.items()}
    return value


def _build_language_code(lang: Optional[str]) -> Dict[str, Any]:
    """Build a USDM Code object for StudyDefinitionDocument.language.

    Accepts either an ISO 639-1 code ("en") or an English language name
    ("English") — the LLM extraction prompt may return either.
    """
    raw = (lang or "en").strip()
    code = raw.lower() if raw.lower() in _ISO_LANGUAGE_CODES else _ISO_LANGUAGE_NAME_TO_CODE.get(raw.lower(), "en")
    return {
        "id": str(uuid.uuid4()),
        "code": code,
        "codeSystem": "ISO",
        "codeSystemVersion": "639-1",
        "decode": _ISO_LANGUAGE_CODES.get(code, "English"),
        "instanceType": "Code",
    }


def _resolve_ct_code(term: str, codelist_id: Optional[str] = None) -> Dict[str, Any]:
    """Resolve a CDISC Controlled Terminology term to a USDM Code object.

    When the governing codelist is known, the term is matched against the
    local copy of that CDISC codelist first (``core.cdisc_codelists``), so
    "g" resolves to Gram in the Unit codelist rather than whatever a
    free-text search ranks first. Otherwise (or with no local match) a live
    NCI EVS lookup (``core.evs_client.find_ct_entry``) is used, cached to
    disk. If the term can't be resolved, a degraded placeholder Code is
    returned with the raw term as the decode and code "UNK" — the value is
    never fabricated, since these are CDISC-controlled codes.
    """
    if codelist_id:
        term_entry = cdisc_lookup(codelist_id, term)
        if term_entry:
            return {"id": str(uuid.uuid4()), **to_code(term_entry, codelist_id), "instanceType": "Code"}

    entry = None
    try:
        entry = find_ct_entry(term)
    except Exception as e:
        logger.warning(f"NCI EVS lookup failed for CT term '{term}': {e}")

    if entry:
        return {
            "id": str(uuid.uuid4()),
            "code": entry.get("code", "UNK"),
            "codeSystem": "http://www.cdisc.org",
            "codeSystemVersion": entry.get("codeSystemVersion", "2024-09-27"),
            "decode": entry.get("preferredName") or entry.get("decode") or term,
            "instanceType": "Code",
        }

    logger.warning(f"NCI EVS lookup returned no result for CT term '{term}'; using placeholder code")
    return {
        "id": str(uuid.uuid4()),
        "code": "UNK",
        "codeSystem": "http://www.cdisc.org",
        "codeSystemVersion": "2024-09-27",
        "decode": term,
        "instanceType": "Code",
    }


def _build_unit_alias_code(unit: str) -> Dict[str, Any]:
    """Wrap a resolved CT code for a unit (e.g. "mg") in an AliasCode.

    Quantity.unit is typed AliasCode, not a bare Code — reuses the same
    non-fabricating NCI EVS lookup as other CT-controlled fields.
    """
    return {
        "id": str(uuid.uuid4()),
        "instanceType": "AliasCode",
        "standardCode": _resolve_ct_code(unit, UNIT_CODELIST),
        "standardCodeAliases": [],
    }


_ISO_DURATION_UNITS = {"Y": "Year", "M": "Month", "W": "Week", "D": "Day"}


def _parse_age_duration(raw: Optional[str]) -> Optional[Tuple[float, str]]:
    """Parse an age bound into (numeric value, unit string).

    Accepts ISO 8601 durations (e.g. "P18Y", "P6M") per the eligibility
    extraction prompt, with a regex fallback for descriptive strings (e.g.
    "18 years") in case the LLM doesn't follow the ISO format.
    """
    if not raw or not isinstance(raw, str):
        return None
    raw = raw.strip()

    iso_match = re.match(r'^P(\d+(?:\.\d+)?)([YMWD])$', raw, re.IGNORECASE)
    if iso_match:
        return float(iso_match.group(1)), _ISO_DURATION_UNITS[iso_match.group(2).upper()]

    desc_match = re.match(r'^([\d.]+)\s*(year|month|week|day)s?', raw, re.IGNORECASE)
    if desc_match:
        return float(desc_match.group(1)), desc_match.group(2).capitalize()

    return None


def _count_value(raw: Any) -> Optional[float]:
    """A number from an int/float, a numeric string ("1,035", "approximately 200"), or a
    {"value": n} object; None when no number is stated."""
    if isinstance(raw, bool):
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    if isinstance(raw, dict):
        return _count_value(raw.get("value"))
    if isinstance(raw, str):
        match = re.search(r"\d[\d,]*(?:\.\d+)?", raw)
        if match:
            return float(match.group(0).replace(",", ""))
    return None


def _build_quantity_range(raw: Any) -> Optional[Dict[str, Any]]:
    """USDM QuantityRange (Quantity or Range) for a planned count such as enrollment.

    A single number becomes a Quantity. A stated range ({"minValue": a, "maxValue": b},
    both numbers) becomes a Range of Quantities. A malformed value (e.g. only a nested
    placeholder object, or a Range with one bound) yields None rather than an
    invalid object; a lone maxValue is read as the planned number.
    """
    if isinstance(raw, dict) and ("minValue" in raw or "maxValue" in raw):
        low, high = _count_value(raw.get("minValue")), _count_value(raw.get("maxValue"))
        if low is not None and high is not None and low != high:
            return {
                "id": str(uuid.uuid4()).replace("-", "_"),
                "minValue": {"id": str(uuid.uuid4()).replace("-", "_"), "value": min(low, high), "instanceType": "Quantity"},
                "maxValue": {"id": str(uuid.uuid4()).replace("-", "_"), "value": max(low, high), "instanceType": "Quantity"},
                "isApproximate": bool(raw.get("isApproximate", False)),
                "instanceType": "Range",
            }
        raw = high if high is not None else low
    value = _count_value(raw)
    if value is None:
        return None
    return {"id": str(uuid.uuid4()).replace("-", "_"), "value": value, "instanceType": "Quantity"}


def _build_planned_age_range(min_raw: Optional[str], max_raw: Optional[str],
                              is_approximate: Optional[bool]) -> Optional[Dict[str, Any]]:
    """Build a USDM Range for StudyDesignPopulation.plannedAge.

    Range.minValue/maxValue are both required (cardinality '1') — if either
    bound can't be parsed, the whole Range is skipped and logged rather
    than fabricating the missing bound.
    """
    min_parsed = _parse_age_duration(min_raw)
    max_parsed = _parse_age_duration(max_raw)
    if not min_parsed or not max_parsed:
        if min_raw or max_raw:
            logger.warning(
                "Could not build plannedAge Range from minAge=%r maxAge=%r "
                "(Range requires both minValue and maxValue); skipping rather "
                "than fabricating the missing bound", min_raw, max_raw,
            )
        return None

    min_value, min_unit = min_parsed
    max_value, max_unit = max_parsed
    return {
        "id": str(uuid.uuid4()).replace("-", "_"),
        "minValue": {
            "id": str(uuid.uuid4()).replace("-", "_"),
            "value": min_value,
            "unit": _build_unit_alias_code(min_unit),
            "instanceType": "Quantity",
        },
        "maxValue": {
            "id": str(uuid.uuid4()).replace("-", "_"),
            "value": max_value,
            "unit": _build_unit_alias_code(max_unit),
            "instanceType": "Quantity",
        },
        "isApproximate": bool(is_approximate) if is_approximate is not None else False,
        "instanceType": "Range",
    }


def _sanitize_entity_data(entity_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove internal/debug properties that are not part of the USDM v4.0 schema.

    Also recursively sanitizes nested dicts and lists, ensures all
    USDM Code objects have required fields, and normalizes
    codeSystemVersion to ISO 8601 format.
    """
    cleaned = {}
    for key, value in entity_data.items():
        # Skip known internal properties
        if key in _INTERNAL_PROPERTIES:
            continue
        # Skip any property starting with underscore (internal convention)
        if key.startswith("_"):
            continue
        # Recursively clean nested dicts
        if isinstance(value, dict):
            sanitized = _sanitize_entity_data(value)
            # Ensure Code objects have all required fields
            if _is_code_object(sanitized):
                sanitized = _ensure_code_id(sanitized)
            cleaned[key] = sanitized
        # Recursively clean lists of dicts
        elif isinstance(value, list):
            items = []
            for item in value:
                if isinstance(item, dict):
                    sanitized = _sanitize_entity_data(item)
                    if _is_code_object(sanitized):
                        sanitized = _ensure_code_id(sanitized)
                    items.append(sanitized)
                else:
                    items.append(item)
            cleaned[key] = items
        else:
            # Fix codeSystemVersion underscores → ISO 8601 dashes
            if key == "codeSystemVersion" and isinstance(value, str):
                if re.match(r"^\d{4}_\d{2}_\d{2}$", value):
                    value = value.replace("_", "-")
            cleaned[key] = value
    return cleaned


# USDM entity type → placement path in the hierarchy
ENTITY_TYPE_PLACEMENT = {
    "metadata": "study",
    "study_identifier": "study.versions[0].studyIdentifiers",
    "study_phase": "study.versions[0].studyPhase",
    "study_title": "study.versions[0].titles",
    "indication": "study.versions[0].studyDesigns[0].indications",
    "objective": "study.versions[0].studyDesigns[0].objectives",
    "endpoint": "study.versions[0].studyDesigns[0].endpoints",
    "estimand": "study.versions[0].studyDesigns[0].estimands",
    "study_arm": "study.versions[0].studyDesigns[0].arms",
    "study_epoch": "study.versions[0].studyDesigns[0].epochs",
    "epoch": "study.versions[0].studyDesigns[0].epochs",  # alias
    "study_cell": "study.versions[0].studyDesigns[0].studyCells",
    "eligibility_criterion": "study.versions[0].studyDesigns[0].eligibilityCriteria",
    "criterion_item": "study.versions[0].eligibilityCriterionItems",
    "study_population": "study.versions[0].studyDesigns[0].population",
    "activity": "study.versions[0].studyDesigns[0].activities",
    "encounter": "study.versions[0].studyDesigns[0].encounters",
    "intervention": "study.versions[0].studyDesigns[0].studyInterventions",
    "study_intervention": "study.versions[0].studyDesigns[0].studyInterventions",  # alias
    "substance": "study._pendingSubstances",  # staged, linked into administrableProducts[].ingredients[] post-placement
    "administrable_product": "study.versions[0].administrableProducts",
    "medical_device": "study.versions[0].medicalDevices",
    "study_element": "study.versions[0].studyDesigns[0].elements",
    "analysis_population": "study.versions[0].studyDesigns[0].analysisPopulations",
    "governance_date": "study.versions[0].dateValues",
    "biomedical_concept": "study.versions[0].biomedicalConcepts",
    "biomedical_concept_category": "study.versions[0].bcCategories",
    "timing": "study.versions[0].studyDesigns[0].scheduleTimelines[].timings",
    "schedule_timeline": "study.versions[0].studyDesigns[0].scheduleTimelines",
    "scheduled_instance": "study.versions[0].studyDesigns[0].scheduleTimelines[].instances",
    "narrative_content": "study.versions[0].narrativeContentItems",
    "narrative_content_item": "study.versions[0].narrativeContentItems",  # alias
    "abbreviation": "study.versions[0].abbreviations",
    "amendment": "study.versions[0].amendments",
    "study_amendment": "study.versions[0].amendments",  # alias
    "geographic_scope": "study._pendingGeographicScopes",  # staged, linked into amendments[]/dateValues[] post-placement
    "country": "study._pendingCountries",  # staged dict keyed by id, resolved alongside geographic_scope
    "document_section": "study.documentVersions[0].sections",
    "organization": "study.versions[0].organizations",
    "study_role": "study.versions[0].roles",
    "schedule_exit": "study.versions[0].studyDesigns[0]._pendingExits",
    "comment_annotation": "study.versions[0].studyDesigns[0].notes",
    "study_definition_document": "study.documentedBy",
    "document_version": "study._pendingDocumentVersions",  # staged, linked into documentedBy[0].versions post-placement
    "biospecimen_retention": "study.versions[0].studyDesigns[0].biospecimenRetentions",
}

# Entity types that go into list containers
LIST_ENTITY_TYPES = {
    "study_identifier", "study_title", "indication", "objective",
    "endpoint", "estimand", "study_arm", "study_epoch", "epoch", "study_cell",
    "eligibility_criterion", "criterion_item", "activity", "encounter",
    "intervention", "study_intervention", "timing",
    "schedule_timeline", "narrative_content", "narrative_content_item",
    "abbreviation", "amendment", "study_amendment",
    "geographic_scope", "document_section",
    "organization", "study_role", "schedule_exit", "comment_annotation",
    # Phase 1 additions — wired entities
    "administrable_product", "medical_device", "study_element",
    "analysis_population", "governance_date",
    # Phase 3 additions — BiomedicalConcept agent
    "biomedical_concept", "biomedical_concept_category",
    # SoA tick data
    "scheduled_instance",
    # Protocol document versions (staged; linked into documentedBy post-placement)
    "document_version",
    "biospecimen_retention",
}


@dataclass
class USDMValidationIssue:
    """An issue found during USDM structure validation."""
    severity: str  # "error", "warning", "info"
    path: str
    message: str

    def to_dict(self) -> Dict[str, Any]:
        return {"severity": self.severity, "path": self.path, "message": self.message}


@dataclass
class USDMGenerationResult:
    """Result of USDM generation."""
    usdm_json: Dict[str, Any] = field(default_factory=dict)
    entity_count: int = 0
    entity_types_included: List[str] = field(default_factory=list)
    validation_issues: List[USDMValidationIssue] = field(default_factory=list)
    output_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_count": self.entity_count,
            "entity_types_included": self.entity_types_included,
            "validation_issues": [v.to_dict() for v in self.validation_issues],
            "output_path": self.output_path,
        }


def _build_empty_usdm_skeleton() -> Dict[str, Any]:
    """Build the minimal USDM v4.0 skeleton structure."""
    return {
        "usdmVersion": "4.0.0",
        "study": {
            "id": str(uuid.uuid4()),
            "instanceType": "Study",
            "name": "",
            "description": "",
            "label": "",
            "versions": [
                {
                    "id": str(uuid.uuid4()),
                    "versionIdentifier": "1",
                    "rationale": "",
                    "titles": [],
                    "studyIdentifiers": [],
                    "studyPhase": None,
                    "organizations": [],
                    "roles": [],
                    "narrativeContentItems": [],
                    "abbreviations": [],
                    "amendments": [],
                    "eligibilityCriterionItems": [],
                    "dateValues": [],
                    "businessTherapeuticAreas": [],
                    "administrableProducts": [],
                    "medicalDevices": [],
                    "biomedicalConcepts": [],
                    "bcCategories": [],
                    "studyDesigns": [
                        {
                            "id": str(uuid.uuid4()),
                            "name": "",
                            "description": "",
                            "arms": [],
                            "epochs": [],
                            "studyCells": [],
                            "objectives": [],
                            "endpoints": [],
                            "estimands": [],
                            "indications": [],
                            "activities": [],
                            "encounters": [],
                            "procedures": [],
                            "studyInterventions": [],
                            "soaFootnotes": [],
                            "scheduleTimelines": [],
                            "eligibilityCriteria": [],
                            "elements": [],
                            "analysisPopulations": [],
                            "studyInterventionIds": [],
                            "population": {
                                "id": str(uuid.uuid4()),
                                "name": "Study Population",
                                "criteria": [],
                                "instanceType": "StudyDesignPopulation",
                            },
                            "geographicScopes": [],
                            "biospecimenRetentions": [],
                        }
                    ],
                }
            ],
            "documentVersions": [
                {
                    "id": str(uuid.uuid4()),
                    "sections": [],
                }
            ],
            "documentedBy": [],
        }
    }


def _place_entity(usdm: Dict[str, Any], entity_type: str,
                   entity_data: Dict[str, Any]) -> bool:
    """
    Place an entity into the correct location in the USDM hierarchy.

    Returns True if placed successfully.
    """
    placement = ENTITY_TYPE_PLACEMENT.get(entity_type)
    if not placement:
        return False

    try:
        if entity_type == "metadata":
            _place_metadata(usdm, entity_data)
            return True
        elif entity_type == "study_phase":
            usdm["study"]["versions"][0]["studyPhase"] = entity_data
            return True
        elif entity_type == "study_population":
            pop = usdm["study"]["versions"][0]["studyDesigns"][0]["population"]
            # plannedMinimumAge/plannedMaximumAge/plannedAgeIsApproximate are
            # staging keys (see extraction/eligibility/schema.py) — build the
            # real plannedAge Range from them instead of passing them through.
            planned_age = _build_planned_age_range(
                entity_data.get("plannedMinimumAge"),
                entity_data.get("plannedMaximumAge"),
                entity_data.get("plannedAgeIsApproximate"),
            )
            skip_keys = {"criteria", "plannedMinimumAge", "plannedMaximumAge", "plannedAgeIsApproximate",
                         "plannedEnrollmentNumber", "plannedCompletionNumber"}
            pop.update({k: v for k, v in entity_data.items() if k not in skip_keys})
            if planned_age:
                pop["plannedAge"] = planned_age
            for key in ("plannedEnrollmentNumber", "plannedCompletionNumber"):
                planned_count = _build_quantity_range(entity_data.get(key))
                if planned_count:
                    pop[key] = planned_count
                elif entity_data.get(key):
                    logger.warning("Could not build %s from %r; left unset", key, entity_data.get(key))
            return True
        elif entity_type == "study_definition_document":
            _place_study_definition_document(usdm, entity_data)
            return True
        elif entity_type == "substance":
            # Substance has no top-level container in USDM 4.0 — it's only
            # reachable via AdministrableProduct.ingredients[].substance.
            # Stage it here and resolve it in _link_substances_to_products()
            # once administrable_product entities (same wave) are placed.
            sub_id = entity_data.get("id")
            if sub_id:
                usdm["study"].setdefault("_pendingSubstances", {})[sub_id] = entity_data
            return True
        elif entity_type == "country":
            # Country has no top-level container in USDM 4.0 — it's only
            # reachable via GeographicScope.code (per-country AliasCode).
            # Stage it here and resolve it in _link_geographic_scopes()
            # once geographic_scope entities (same wave) are placed.
            country_id = entity_data.get("id")
            if country_id:
                usdm["study"].setdefault("_pendingCountries", {})[country_id] = entity_data
            return True
        elif entity_type in LIST_ENTITY_TYPES:
            container = _resolve_list_container(usdm, entity_type)
            if container is not None:
                container.append(entity_data)
                return True
        return False
    except (KeyError, IndexError, TypeError):
        return False


def _place_metadata(usdm: Dict[str, Any], data: Dict[str, Any]) -> None:
    """Place metadata fields at the study level and version level."""
    study = usdm["study"]
    if "name" in data:
        study["name"] = data["name"]
    if "description" in data:
        study["description"] = data["description"]
    if "label" in data:
        study["label"] = data["label"]
    # Propagate versionIdentifier to StudyVersion
    if data.get("versionIdentifier") and study.get("versions"):
        study["versions"][0]["versionIdentifier"] = str(data["versionIdentifier"])


def _place_study_definition_document(usdm: Dict[str, Any], data: Dict[str, Any]) -> None:
    """Place a StudyDefinitionDocument entity into study.documentedBy[].

    Builds the required `language` and `type` Code objects and defaults
    `templateName` to "SPONSOR" when the protocol doesn't state one.
    """
    doc = {
        "id": data.get("id") or str(uuid.uuid4()),
        "name": data.get("name") or "Protocol",
        "language": _build_language_code(data.get("language")),
        "type": _resolve_ct_code(data.get("documentType") or "Protocol", "C215477"),
        "templateName": data.get("templateName") or "SPONSOR",
        "versions": [],
        "instanceType": "StudyDefinitionDocument",
    }
    if data.get("label"):
        doc["label"] = data["label"]
    if data.get("description"):
        doc["description"] = data["description"]
    usdm["study"].setdefault("documentedBy", []).append(doc)


def _resolve_list_container(usdm: Dict[str, Any],
                             entity_type: str) -> Optional[List]:
    """Resolve the list container for a given entity type."""
    study = usdm["study"]
    version = study["versions"][0]
    design = version["studyDesigns"][0]

    mapping = {
        "study_identifier": version["studyIdentifiers"],
        "study_title": version["titles"],
        "indication": design["indications"],
        "objective": design["objectives"],
        "endpoint": design["endpoints"],
        "estimand": design["estimands"],
        "study_arm": design["arms"],
        "study_epoch": design["epochs"],
        "epoch": design["epochs"],
        "study_cell": design["studyCells"],
        "eligibility_criterion": design["eligibilityCriteria"],
        "criterion_item": version["eligibilityCriterionItems"],
        "activity": design["activities"],
        "encounter": design["encounters"],
        "procedure": design["procedures"],
        "intervention": design["studyInterventions"],
        "study_intervention": design["studyInterventions"],
        "schedule_timeline": design["scheduleTimelines"],
        "narrative_content": version["narrativeContentItems"],
        "narrative_content_item": version["narrativeContentItems"],
        "abbreviation": version["abbreviations"],
        "amendment": version["amendments"],
        "study_amendment": version["amendments"],
        # Staged geographic scope — linked into amendments[]/dateValues[]
        # by _link_geographic_scopes() after all entities are placed.
        "geographic_scope": study.setdefault("_pendingGeographicScopes", []),
        "document_section": study["documentVersions"][0]["sections"],
        "organization": version["organizations"],
        "study_role": version["roles"],
        "schedule_exit": design.setdefault("_pendingExits", []),
        "scheduled_instance": design.setdefault("_scheduledInstances", []),
        "comment_annotation": design.setdefault("notes", []),
        # Phase 1 additions
        "administrable_product": version.setdefault("administrableProducts", []),
        "medical_device": version.setdefault("medicalDevices", []),
        "study_element": design.setdefault("elements", []),
        "analysis_population": design.setdefault("analysisPopulations", []),
        "governance_date": version.setdefault("dateValues", []),
        # Phase 3 additions
        "biomedical_concept": version.setdefault("biomedicalConcepts", []),
        "biomedical_concept_category": version.setdefault("bcCategories", []),
        # Staged document versions — linked into documentedBy[0].versions
        # by _link_document_versions() after all entities are placed.
        "document_version": study.setdefault("_pendingDocumentVersions", []),
        "biospecimen_retention": design.setdefault("biospecimenRetentions", []),
    }
    return mapping.get(entity_type)


def _resolve_objective_endpoints(usdm: Dict[str, Any],
                                 endpoint_map: Optional[Dict[str, Dict[str, Any]]] = None) -> None:
    """
    Resolve endpointIds on Objective entities into nested objectiveEndpoints.

    USDM v4.0 expects endpoints as nested objects within objectives
    (property: objectiveEndpoints), not as ID references (endpointIds).
    """
    try:
        sd = usdm["study"]["versions"][0]["studyDesigns"][0]
    except (KeyError, IndexError):
        return

    objectives = sd.get("objectives", [])
    if not objectives:
        return

    ep_map = dict(endpoint_map or {})

    # Also scan the USDM tree for any endpoint objects already placed
    def _collect_endpoints(obj: Any) -> None:
        if isinstance(obj, dict):
            eid = obj.get("id", "")
            if isinstance(eid, str) and eid.startswith("ep_") and eid not in ep_map:
                ep_map[eid] = obj
            for v in obj.values():
                _collect_endpoints(v)
        elif isinstance(obj, list):
            for item in obj:
                _collect_endpoints(item)

    _collect_endpoints(usdm)

    # Resolve endpointIds → objectiveEndpoints on each objective
    for obj in objectives:
        endpoint_ids = obj.pop("endpointIds", [])
        if not endpoint_ids:
            continue

        nested_endpoints = []
        for ep_id in endpoint_ids:
            ep = ep_map.get(ep_id)
            if ep:
                nested_endpoints.append(dict(ep))
            else:
                nested_endpoints.append({
                    "id": ep_id,
                    "instanceType": "Endpoint",
                })
        obj["objectiveEndpoints"] = nested_endpoints


# ── Codelist normalization maps ──────────────────────────────────────────────
# These map extraction-side values to the correct CDISC codelist codes that
# the CORE engine validates against.

# EligibilityCriterion.category → codelist C66797
_ELIGIBILITY_CATEGORY_MAP = {
    "Inclusion": ("C25532", "Inclusion Criteria"),
    "inclusion": ("C25532", "Inclusion Criteria"),
    "Exclusion": ("C25370", "Exclusion Criteria"),
    "exclusion": ("C25370", "Exclusion Criteria"),
}

# Endpoint.level → codelist C188726 (NOT extensible)
_ENDPOINT_LEVEL_MAP = {
    "C98772": ("C94496", "Primary Endpoint"),        # Primary Outcome Measure → Primary Endpoint
    "C98781": ("C139173", "Secondary Endpoint"),      # Secondary Outcome Measure → Secondary Endpoint
    "C98724": ("C170559", "Exploratory Endpoint"),    # Exploratory Outcome Measure → Exploratory Endpoint
}

# Encounter.type → codelist C188728
_ENCOUNTER_TYPE_MAP = {
    "C25426": ("C25716", "Visit"),                   # Visit → Scheduled Visit
    "C98779": ("C98779", "Screening Visit"),
    "C142615": ("C142615", "Baseline Visit"),
    "C98780": ("C98780", "Treatment Visit"),
    "C71738": ("C71738", "Randomization Visit"),
    "C98777": ("C98777", "Follow-up Visit"),
}

# StudyTitle.type → codelist C207419
_TITLE_TYPE_MAP = {
    "Official Study Title": ("C207616", "Official Study Title"),
    "Study Acronym": ("C207646", "Study Acronym"),
    "Brief Study Title": ("C207617", "Brief Study Title"),
}

# CDISC DDF Study Role codelist (C215480): code → preferred term
_STUDY_ROLE_CODES = {
    "C78726": "Adjudication Committee",
    "C17445": "Caregiver",
    "C215672": "Clinical Trial Physician",
    "C215669": "Study Co-Sponsor",
    "C215662": "Contract Research",
    "C142489": "Data Monitoring Committee",
    "C215671": "Dose Escalation Committee",
    "C142578": "Independent Data Monitoring Committee",
    "C25936": "Investigator",
    "C37984": "Laboratory",
    "C215670": "Local Legal Sponsor",
    "C25392": "Manufacturer",
    "C51876": "Sponsor Medical Expert",
    "C207599": "Outcomes Assessor",
    "C215673": "Pharmacovigilance Group",
    "C19924": "Principal Investigator",
    "C51851": "Project Coordinator",
    "C188863": "Regulatory Agency",
    "C70793": "Clinical Study Sponsor",
    "C51877": "Statistician",
    "C80403": "Study Site",
    "C41189": "Study Subject",
}

# Role name keywords → C215480 code. Order matters: specific before generic
# (e.g. "co-sponsor" before "sponsor", "principal investigator" before
# "investigator"). Registry is an Organization type, not a study role, so it
# has no entry and such roles are dropped.
_STUDY_ROLE_KEYWORDS = [
    (r"independent data monitoring|\bidmc\b", "C142578"),
    (r"data (safety )?monitoring (committee|board)|\bdmc\b|\bdsmb\b", "C142489"),
    (r"adjudicat|endpoint committee|events? committee|\bcec\b", "C78726"),
    (r"dose[\s-]escalation committee", "C215671"),
    (r"co-?\s?sponsor", "C215669"),
    (r"local (legal )?sponsor|legal representative", "C215670"),
    (r"medical monitor|sponsor medical|medical expert", "C51876"),
    (r"sponsor", "C70793"),
    (r"contract research|\bcro\b", "C215662"),
    (r"principal investigator|\bpi\b", "C19924"),
    (r"investigator", "C25936"),
    (r"pharmacovigilance", "C215673"),
    (r"laborator", "C37984"),
    (r"statistic", "C51877"),
    (r"regulatory", "C188863"),
    (r"manufactur", "C25392"),
    (r"project (coordinat|manag)", "C51851"),
    (r"clinical trial physician", "C215672"),
    (r"outcomes? assessor", "C207599"),
    (r"study site|^site$", "C80403"),
    (r"caregiver", "C17445"),
]


def _map_study_role(name: str, code_val: str = "") -> Optional[Tuple[str, str]]:
    """Map a StudyRole to its C215480 (code, decode), or None if not a study role.

    The role name is the primary signal (extraction may set a wrong code);
    a code already in C215480 is the fallback.
    """
    name_lower = (name or "").strip().lower()
    for pattern, code in _STUDY_ROLE_KEYWORDS:
        if name_lower and re.search(pattern, name_lower):
            return code, _STUDY_ROLE_CODES[code]
    if code_val in _STUDY_ROLE_CODES:
        return code_val, _STUDY_ROLE_CODES[code_val]
    return None

# Organization type → CDISC codelist C188724
_ORG_TYPE_MAP = {
    "Pharmaceutical Company": ("C54086", "Pharmaceutical Company"),
    "Clinical Research Organization": ("C54086", "Pharmaceutical Company"),
    "Healthcare Facility": ("C19326", "Healthcare Facility"),
    "Registry": ("C19326", "Healthcare Facility"),
}

# StudyIntervention type → CDISC codelist C99078
# These codes are already correct NCI codes; just need codeSystem fixed
_INTERVENTION_TYPE_CODES = {
    "C54121", "C54129", "C1909", "C54130", "C54131",
    "C82637", "C82638", "C96631",
}

# StudyIntervention role → CDISC codelist C207417
_INTERVENTION_ROLE_CODES = {
    "C54121", "C54129", "C54130", "C54131", "C82637",
    "C82638", "C96631", "C1909",
}


def _normalize_codelists(usdm: Dict[str, Any]) -> None:
    """
    Normalize Code objects to use correct CDISC codelist codes.

    The extraction agents sometimes use internal code values or wrong
    codelists. This function remaps them to the codes expected by the
    CORE engine.
    """
    try:
        version = usdm["study"]["versions"][0]
        design = version["studyDesigns"][0]
    except (KeyError, IndexError):
        return

    cdisc_sys = "http://www.cdisc.org"
    cdisc_ver = "2024-09-27"

    # Fix EligibilityCriterion.category
    for ec in design.get("eligibilityCriteria", []):
        cat = ec.get("category")
        if isinstance(cat, dict):
            code_val = cat.get("code", "")
            mapped = _ELIGIBILITY_CATEGORY_MAP.get(code_val)
            if mapped:
                cat["code"] = mapped[0]
                cat["decode"] = mapped[1]
                cat["codeSystem"] = cdisc_sys
                cat["codeSystemVersion"] = cdisc_ver

    # Fix Endpoint.level
    for ep in design.get("endpoints", []):
        level = ep.get("level")
        if isinstance(level, dict):
            code_val = level.get("code", "")
            mapped = _ENDPOINT_LEVEL_MAP.get(code_val)
            if mapped:
                level["code"] = mapped[0]
                level["decode"] = mapped[1]

    # Fix Encounter.type
    for enc in design.get("encounters", []):
        etype = enc.get("type")
        if isinstance(etype, dict):
            code_val = etype.get("code", "")
            mapped = _ENCOUNTER_TYPE_MAP.get(code_val)
            if mapped:
                etype["code"] = mapped[0]
                etype["decode"] = mapped[1]
                etype["codeSystem"] = cdisc_sys
                etype["codeSystemVersion"] = cdisc_ver

    # Fix StudyTitle.type
    for title in version.get("titles", []):
        ttype = title.get("type")
        if isinstance(ttype, dict):
            code_val = ttype.get("code", "")
            mapped = _TITLE_TYPE_MAP.get(code_val)
            if mapped:
                ttype["code"] = mapped[0]
                ttype["decode"] = mapped[1]
                ttype["codeSystem"] = cdisc_sys
                ttype["codeSystemVersion"] = cdisc_ver

    # Fix NarrativeContent: CORE expects "NarrativeContentItem" at narrativeContentItems path
    for nc in version.get("narrativeContentItems", []):
        if nc.get("instanceType") == "NarrativeContent":
            nc["instanceType"] = "NarrativeContentItem"

    # Fix Procedure codes with null codeSystemVersion and ensure procedureType
    for proc in design.get("procedures", []):
        code_obj = proc.get("code")
        if isinstance(code_obj, dict):
            if not code_obj.get("codeSystemVersion"):
                code_obj["codeSystemVersion"] = cdisc_ver
        # Ensure procedureType is present (required by CORE)
        if "procedureType" not in proc:
            proc["procedureType"] = proc.get("name", "Clinical Procedure")
        # Strip 'codes' property — not in USDM v4.0 schema
        proc.pop("codes", None)

    # Fix StudyRole.code to use CDISC codes (DDF00201, DDF00259)
    # Also set appliesToIds (DDF00189, DDF00203)
    version_id = version.get("id")
    design_id = design.get("id")
    for role in version.get("roles", []):
        code_obj = role.get("code")
        if isinstance(code_obj, dict):
            mapped = _map_study_role(role.get("name", ""), code_obj.get("code", ""))
            if mapped:
                code_obj["code"] = mapped[0]
                code_obj["decode"] = mapped[1]
                code_obj["codeSystem"] = cdisc_sys
                code_obj["codeSystemVersion"] = cdisc_ver
                if not code_obj.get("instanceType"):
                    code_obj["instanceType"] = "Code"
                if not code_obj.get("id"):
                    code_obj["id"] = str(uuid.uuid4()).replace("-", "_")
        # Ensure appliesToIds references the version and design
        if not role.get("appliesToIds"):
            applies = []
            if version_id:
                applies.append(version_id)
            if design_id:
                applies.append(design_id)
            role["appliesToIds"] = applies

    # Fix Organization.type to use CDISC codelist C188724 (DDF00200)
    # C188724 codes validated against CDISC USDM golden output:
    #   Sponsor    → C70793  "Clinical Study Sponsor"
    #   Registry   → C93453  "Study Registry"
    #   Regulatory → C188863 "Regulatory Agency"
    #   CRO        → C54499  "Contract Research Organization"
    _C188724_ORG_TYPE = {
        "pharma": ("C70793", "Clinical Study Sponsor"),
        "biotech": ("C70793", "Clinical Study Sponsor"),
        "sponsor": ("C70793", "Clinical Study Sponsor"),
        "registry": ("C93453", "Study Registry"),
        "clinicaltrials": ("C93453", "Study Registry"),
        "ctgov": ("C93453", "Study Registry"),
        "eudract": ("C93453", "Study Registry"),
        "ctis": ("C93453", "Study Registry"),
        "isrctn": ("C93453", "Study Registry"),
        "regulatory": ("C188863", "Regulatory Agency"),
        "fda": ("C188863", "Regulatory Agency"),
        "ema": ("C188863", "Regulatory Agency"),
        "mhra": ("C188863", "Regulatory Agency"),
        "tga": ("C188863", "Regulatory Agency"),
        "pmda": ("C188863", "Regulatory Agency"),
        "cro": ("C54499", "Contract Research Organization"),
        "contract research": ("C54499", "Contract Research Organization"),
    }
    for org in version.get("organizations", []):
        org_type = org.get("type")
        org_name_lower = org.get("name", "").lower()
        # Infer correct C188724 code from org name
        inferred = None
        for keyword, (tc, td) in _C188724_ORG_TYPE.items():
            if keyword in org_name_lower:
                inferred = (tc, td)
                break
        # Use inferred code if available; else keep/fix existing
        if inferred:
            type_code, type_decode = inferred
        elif isinstance(org_type, dict) and org_type.get("code"):
            type_code, type_decode = org_type.get("code"), org_type.get("decode", "")
        else:
            type_code, type_decode = "C70793", "Clinical Study Sponsor"  # default to sponsor
        org["type"] = {
            "id": (org_type or {}).get("id") or str(uuid.uuid4()).replace("-", "_"),
            "code": type_code,
            "codeSystem": cdisc_sys,
            "codeSystemVersion": cdisc_ver,
            "decode": type_decode,
            "instanceType": "Code",
        }

    # Fix StudyIntervention type and role (DDF00128, DDF00112)
    for inv in version.get("studyInterventions", []):
        # Strip properties not in USDM v4.0 schema
        inv.pop("administrationIds", None)
        inv.pop("productIds", None)
        inv.pop("codes", None)

        # Ensure type uses CDISC codeSystem (codelist C99078)
        inv_type = inv.get("type")
        if isinstance(inv_type, dict):
            if inv_type.get("code") in _INTERVENTION_TYPE_CODES:
                inv_type["codeSystem"] = cdisc_sys
                inv_type["codeSystemVersion"] = cdisc_ver

        # Ensure role uses CDISC codeSystem (codelist C207417)
        inv_role = inv.get("role")
        if isinstance(inv_role, dict):
            if inv_role.get("code") in _INTERVENTION_ROLE_CODES:
                inv_role["codeSystem"] = cdisc_sys
                inv_role["codeSystemVersion"] = cdisc_ver

    # Fix StudyAmendment: normalize geographic scope type (DDF00144),
    # amendment reason code (DDF00143), and ensure required `changes` (DDF00125).
    _GEO_SCOPE_TYPE_MAP = {
        "Global": ("C68846", "Global"),
        "Country": ("C25464", "Country"),
        "Region": ("C41129", "Region"),
    }
    for amend in version.get("amendments", []):
        # Normalize geographicScopes type codes to CDISC codelist C207412
        for gs in amend.get("geographicScopes", []):
            gs_type = gs.get("type")
            if isinstance(gs_type, dict):
                code_val = gs_type.get("code", "")
                mapped = _GEO_SCOPE_TYPE_MAP.get(code_val)
                if mapped:
                    gs_type["code"] = mapped[0]
                    gs_type["decode"] = mapped[1]
                gs_type["codeSystem"] = cdisc_sys
                gs_type["codeSystemVersion"] = cdisc_ver
                # DDF00261: if global, code field must be absent
                if gs_type.get("code") == "C68846":
                    gs.pop("code", None)

        # Normalize primaryReason code to CDISC codelist C207415 (DDF00143)
        pr = amend.get("primaryReason")
        if isinstance(pr, dict):
            code_obj = pr.get("code")
            if isinstance(code_obj, dict):
                code_obj["codeSystem"] = cdisc_sys
                code_obj["codeSystemVersion"] = cdisc_ver
                # Map legacy extraction codes to C207415 terms. C98782
                # ("Protocol Amendment") carries no reason, so it becomes
                # Other (with otherReason) rather than a guessed reason.
                _AMEND_REASON_MAP = {
                    "C98782": ("C17649", "Other"),
                }
                old_code = code_obj.get("code", "")
                mapped = _AMEND_REASON_MAP.get(old_code)
                if mapped:
                    code_obj["code"] = mapped[0]
                    code_obj["decode"] = mapped[1]
            # DDF00020: if code is C17649 (Other), otherReason must not be blank
            # If code is NOT C17649, otherReason must be blank/absent
            if isinstance(code_obj, dict):
                if code_obj.get("code") == "C17649":
                    if not pr.get("otherReason"):
                        pr["otherReason"] = amend.get("summary", "Other")
                else:
                    pr.pop("otherReason", None)

        # Ensure required `changes` array (DDF00125)
        if not amend.get("changes"):
            amend["changes"] = [{
                "id": str(uuid.uuid4()).replace("-", "_"),
                "name": amend.get("name", "Amendment Change"),
                "summary": amend.get("summary", "See amendment details."),
                "rationale": amend.get("summary", "See amendment details."),
                "changedSections": [{
                    "id": str(uuid.uuid4()).replace("-", "_"),
                    "sectionNumber": "1",
                    "sectionTitle": "General",
                    "appliesToId": amend.get("id", ""),
                    "instanceType": "DocumentContentReference",
                }],
                "instanceType": "StudyChange",
            }]

    # Fix duplicate NarrativeContentItem names (DDF00010)
    nci_names: Dict[str, int] = {}
    for nci in version.get("narrativeContentItems", []):
        name = nci.get("name", "")
        if name in nci_names:
            nci_names[name] += 1
            nci["name"] = f"{name} ({nci_names[name]})"
        else:
            nci_names[name] = 1

    # Chain epoch ordering via nextId (DDF00088)
    epochs = design.get("epochs", [])
    for i, ep in enumerate(epochs[:-1]):
        if not ep.get("nextId"):
            ep["nextId"] = epochs[i + 1]["id"]

    # Chain encounter ordering via nextId (DDF00087)
    encounters = design.get("encounters", [])
    for i, enc in enumerate(encounters[:-1]):
        if not enc.get("nextId"):
            enc["nextId"] = encounters[i + 1]["id"]

    # Resolve encounter→epoch mapping captured during entity placement.
    # The map was built from vision-extracted epochIds (e.g. "epoch_1") which
    # reference the header_structure epoch IDs, NOT the USDM epoch entity IDs
    # (e.g. "epoch_v_1").  We resolve them here by matching epoch names from
    # the header_structure to the actual USDM epoch entities.
    epochs = design.get("epochs", [])
    raw_enc_epoch_map = design.get("_encounterEpochMap", {})

    if raw_enc_epoch_map and epochs:
        # Build a lookup from header-structure epoch ID → USDM epoch entity ID.
        # The header_structure stores epochs with IDs like "epoch_1" and names
        # like "Screening".  The USDM epoch entities have IDs like "epoch_v_1"
        # and the same names.  Match by name (case-insensitive).
        header_epochs = design.get("_headerEpochs", [])
        header_id_to_name = {ep["id"]: ep.get("name", "") for ep in header_epochs}
        usdm_name_to_id: Dict[str, str] = {}
        for ep in epochs:
            usdm_name_to_id[_normalize_epoch_name(ep.get("name", ""))] = ep["id"]

        stale_to_usdm: Dict[str, str] = {}
        for hdr_id, hdr_name in header_id_to_name.items():
            resolved = usdm_name_to_id.get(_normalize_epoch_name(hdr_name))
            if resolved:
                stale_to_usdm[hdr_id] = resolved

        # Resolve the map values from stale IDs to USDM IDs
        resolved_map: Dict[str, str] = {}
        for enc_id, stale_epoch_id in raw_enc_epoch_map.items():
            resolved = stale_to_usdm.get(stale_epoch_id)
            if resolved:
                resolved_map[enc_id] = resolved
            elif stale_epoch_id in {ep["id"] for ep in epochs}:
                # Already a valid USDM epoch ID
                resolved_map[enc_id] = stale_epoch_id

        design["_encounterEpochMap"] = resolved_map

        # Also set epochId on encounter objects for UI column grouping
        for enc in encounters:
            if not enc.get("epochId"):
                mapped = resolved_map.get(enc.get("id"))
                if mapped:
                    enc["epochId"] = mapped

    # Fix StudyCell epochIds to match actual epoch IDs (DDF00243)
    # Extraction may create cells with epochIds like "epoch_1" while
    # actual epochs are "epoch_v_1". Remap by position.
    # Also ensure each cell has at least one elementId (DDF00126).
    epoch_ids = [ep["id"] for ep in epochs]
    if epoch_ids:
        _remap_study_cells(design, epochs)

    # Fix StudyRole appliesToIds (DDF00189)
    # CORE expects appliesToIds to reference ONLY the version ID
    for role in version.get("roles", []):
        if role.get("appliesToIds"):
            role["appliesToIds"] = [version_id] if version_id else []

    # DDF00201: Ensure exactly one Sponsor role (C70793).
    # Remove roles that don't map to any valid C215480 code (e.g. "Registry"
    # is an Organization type, not a role) and keep one role per code,
    # merging organizationIds of duplicates.
    valid_roles = []
    roles_by_code: Dict[str, Dict[str, Any]] = {}
    for role in version.get("roles", []):
        code_obj = role.get("code")
        if not isinstance(code_obj, dict):
            continue
        mapped = _map_study_role(role.get("name", ""), code_obj.get("code", ""))
        if not mapped:
            continue
        code_obj["code"], code_obj["decode"] = mapped
        if mapped[0] in roles_by_code:
            kept = roles_by_code[mapped[0]]
            for org_id in role.get("organizationIds", []):
                if org_id not in kept.setdefault("organizationIds", []):
                    kept["organizationIds"].append(org_id)
            continue
        roles_by_code[mapped[0]] = role
        valid_roles.append(role)
    has_sponsor = "C70793" in roles_by_code
    # If no sponsor role exists, create one
    if not has_sponsor:
        valid_roles.insert(0, {
            "id": str(uuid.uuid4()).replace("-", "_"),
            "name": "Sponsor",
            "code": {
                "id": str(uuid.uuid4()).replace("-", "_"),
                "code": "C70793",
                "codeSystem": cdisc_sys,
                "codeSystemVersion": cdisc_ver,
                "decode": "Clinical Study Sponsor",
                "instanceType": "Code",
            },
            "appliesToIds": [version_id] if version_id else [],
            "instanceType": "StudyRole",
        })
    version["roles"] = valid_roles

    # DDF00172: Wire organizationId on roles by matching role name to org type.
    # Sponsor role → org with type C70793 (Clinical Study Sponsor) or C54086 (Pharma)
    # This enables CORE to find the sponsor study identifier.
    orgs = version.get("organizations", [])
    for role in version.get("roles", []):
        if role.get("organizationId"):
            continue  # Already linked
        role_code = role.get("code", {}).get("code", "")
        if role_code == "C70793":  # Sponsor
            # Find sponsor org (type C70793 or C54086)
            sponsor_org = next(
                (o for o in orgs if o.get("type", {}).get("code") in ("C70793", "C54086")),
                None
            )
            if sponsor_org:
                role["organizationId"] = sponsor_org["id"]
        elif role_code == "C25936":  # Principal Investigator
            # Find healthcare facility org
            pi_org = next(
                (o for o in orgs if o.get("type", {}).get("code") == "C19326"),
                None
            )
            if pi_org:
                role["organizationId"] = pi_org["id"]


def _fix_activity_names(usdm: Dict[str, Any]) -> None:
    """
    Fix activity names that contain the full repr() string of the Activity
    dataclass instead of just the name value.

    E.g. "Activity(id='act_1', name='Informed Consent', ...)" → "Informed Consent"
    """
    try:
        design = usdm["study"]["versions"][0]["studyDesigns"][0]
    except (KeyError, IndexError):
        return

    name_pattern = re.compile(r"Activity\(.*?name='([^']*)'")
    for activity in design.get("activities", []):
        name = activity.get("name", "")
        if name.startswith("Activity("):
            match = name_pattern.search(name)
            if match:
                activity["name"] = match.group(1)


def _tokenize(text: str) -> set:
    """Split text into lowercase keyword tokens, dropping noise words."""
    _STOP = {"and", "or", "the", "a", "an", "of", "for", "in", "to", "with", "at", "by", "on"}
    return {w for w in re.split(r"[\s/\-\(\),]+", text.lower()) if w and w not in _STOP}


# Keyword → (NCI code, decode) for creating synthetic procedures when no
# existing procedure matches an activity.
_ACTIVITY_PROCEDURE_CODES: Dict[str, tuple] = {
    "informed consent": ("C16735", "Informed Consent"),
    "physical exam": ("C20989", "Physical Examination"),
    "vital signs": ("C25714", "Vital Signs"),
    "ecg": ("C38054", "Electrocardiogram"),
    "electrocardiogram": ("C38054", "Electrocardiogram"),
    "blood pressure": ("C54706", "Blood Pressure Measurement"),
    "weight": ("C25208", "Weight"),
    "height": ("C25347", "Height"),
    "randomization": ("C15417", "Randomization"),
    "laboratory": ("C49286", "Laboratory Test"),
    "urinalysis": ("C79430", "Urinalysis"),
    "adverse event": ("C41331", "Adverse Event"),
    "concomitant medication": ("C53630", "Concomitant Medication"),
    "medication review": ("C53630", "Concomitant Medication"),
    "medical history": ("C18772", "Medical History"),
    "demographics": ("C49672", "Demographics"),
    "pregnancy test": ("C92949", "Pregnancy Test"),
    "pharmacokinetic": ("C15299", "Pharmacokinetics"),
    "antibod": ("C16295", "Antibody Measurement"),
    "genetic analy": ("C15429", "Genetic Analysis"),
    "blood sample": ("C17610", "Blood Sample Collection"),
    "blood collect": ("C17610", "Blood Sample Collection"),
    "tumor imag": ("C17369", "Imaging Technique"),
    "tissue collect": ("C15189", "Biopsy"),
    "biopsy": ("C15189", "Biopsy"),
    "survival": ("C25717", "Survival Assessment"),
    "cbc": ("C64848", "Complete Blood Count"),
    "chemistry panel": ("C49286", "Laboratory Test"),
    "thyroid": ("C79441", "Thyroid Function Test"),
    "serum": ("C49286", "Laboratory Test"),
    "hepatitis": ("C49286", "Laboratory Test"),
    "hbsag": ("C49286", "Laboratory Test"),
    "hep c": ("C49286", "Laboratory Test"),
    "hcv": ("C49286", "Laboratory Test"),
    "tsh": ("C79441", "Thyroid Function Test"),
    "ft4": ("C79441", "Thyroid Function Test"),
    "identification card": ("C25218", "Administrative Procedure"),
    "inclusion": ("C25532", "Eligibility Assessment"),
    "exclusion": ("C25370", "Eligibility Assessment"),
    "eligibility": ("C25370", "Eligibility Assessment"),
    "patient reported outcome": ("C28421", "Patient Reported Outcome"),
    "pro": ("C28421", "Patient Reported Outcome"),
    "hrqol": ("C28421", "Patient Reported Outcome"),
    "anticancer therapy": ("C15632", "Anticancer Therapy Assessment"),
    "coagulation": ("C64847", "Coagulation Test"),
    "pt/inr": ("C64847", "Coagulation Test"),
    "aptt": ("C64847", "Coagulation Test"),
}


def _link_activities_to_procedures(usdm: Dict[str, Any]) -> None:
    """
    Link activities to procedures via definedProcedures.

    Uses three matching strategies in order:
    1. Direct name match (case-insensitive)
    2. Substring containment match
    3. Keyword overlap (>=50% of procedure keywords found in activity name)

    Each matched procedure is embedded as a full Procedure object (with a
    unique ID) in the activity's definedProcedures list.  CORE expects
    instanceType="Procedure" with name, procedureType, and code fields.
    """
    try:
        design = usdm["study"]["versions"][0]["studyDesigns"][0]
    except (KeyError, IndexError):
        return

    procedures = design.get("procedures", [])
    activities = design.get("activities", [])
    if not procedures or not activities:
        return

    # Build name-to-procedure lookup (lowercase, stripped)
    proc_by_name: Dict[str, Dict[str, Any]] = {}
    for proc in procedures:
        pname = proc.get("name", "").lower().strip()
        if pname:
            proc_by_name[pname] = proc
            # Also index without common suffixes for fuzzy matching
            for suffix in (" sampling", " collection", " test", " assessment",
                           " evaluations", " infusion"):
                if pname.endswith(suffix):
                    proc_by_name[pname[: -len(suffix)]] = proc

    # Pre-tokenize procedure names
    proc_tokens = [(proc, _tokenize(proc.get("name", ""))) for proc in procedures]

    def _embed_proc(proc: Dict[str, Any]) -> Dict[str, Any]:
        """Create an embedded copy of a procedure with a fresh unique ID."""
        embedded = {
            "id": str(uuid.uuid4()),
            "name": proc.get("name", ""),
            "instanceType": "Procedure",
        }
        if proc.get("procedureType"):
            embedded["procedureType"] = proc["procedureType"]
        if proc.get("code"):
            # Deep-copy code but give it a unique ID too
            code_copy = dict(proc["code"])
            code_copy["id"] = str(uuid.uuid4())
            embedded["code"] = code_copy
        return embedded

    for activity in activities:
        act_name = activity.get("name", "").lower().strip()
        if not act_name:
            continue

        matched_ids: list = []
        matched_procs: list = []

        # Strategy 1: Direct match
        if act_name in proc_by_name:
            p = proc_by_name[act_name]
            matched_ids.append(p.get("id"))
            matched_procs.append(p)

        # Strategy 2: Substring containment
        for pname, proc in proc_by_name.items():
            pid = proc.get("id")
            if pid in matched_ids:
                continue
            if pname in act_name or act_name in pname:
                matched_ids.append(pid)
                matched_procs.append(proc)

        # Strategy 3: Keyword overlap (if no match yet)
        if not matched_procs:
            act_tokens = _tokenize(act_name)
            if act_tokens:
                for proc, ptokens in proc_tokens:
                    pid = proc.get("id")
                    if pid in matched_ids or not ptokens:
                        continue
                    overlap = act_tokens & ptokens
                    # Match if >=50% of procedure keywords appear in activity
                    if len(overlap) >= max(1, len(ptokens) * 0.5):
                        matched_ids.append(pid)
                        matched_procs.append(proc)

        if matched_procs:
            activity["definedProcedures"] = [_embed_proc(p) for p in matched_procs]
        else:
            # Fallback: create a synthetic procedure from known clinical codes
            act_lower = activity.get("name", "").lower()
            for keyword, (code, decode) in _ACTIVITY_PROCEDURE_CODES.items():
                if keyword in act_lower:
                    # Use activity name as procedure name to avoid DDF00010
                    # duplicate name issues when multiple activities match
                    # the same keyword.
                    act_name_orig = activity.get("name", decode)
                    synth_proc = {
                        "id": str(uuid.uuid4()),
                        "name": act_name_orig,
                        "procedureType": decode,
                        "code": {
                            "id": str(uuid.uuid4()),
                            "code": code,
                            "codeSystem": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl",
                            "codeSystemVersion": "2024-09-27",
                            "decode": decode,
                            "instanceType": "Code",
                        },
                        "instanceType": "Procedure",
                    }
                    activity["definedProcedures"] = [synth_proc]
                    break

            # Absolute fallback: if still no procedure, create a generic one (DDF00263)
            if not activity.get("definedProcedures"):
                act_name_orig = activity.get("name", "Clinical Procedure")
                activity["definedProcedures"] = [{
                    "id": str(uuid.uuid4()),
                    "name": act_name_orig,
                    "procedureType": "Clinical Procedure",
                    "code": {
                        "id": str(uuid.uuid4()),
                        "code": "C25218",
                        "codeSystem": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl",
                        "codeSystemVersion": "2024-09-27",
                        "decode": "Procedure",
                        "instanceType": "Code",
                    },
                    "instanceType": "Procedure",
                }]

    # Remove top-level procedures[] to avoid DDF00010 duplicate name
    # conflicts between procedures[] and embedded definedProcedures[].
    # All procedure data is now embedded in activities.
    design.pop("procedures", None)

    # Link drug-related procedures to study interventions (DDF00101)
    version = usdm["study"]["versions"][0]
    interventions = version.get("studyInterventions", [])
    if interventions:
        inv_by_name: Dict[str, str] = {}
        for inv in interventions:
            inv_name = inv.get("name", "").lower().strip()
            if inv_name:
                inv_by_name[inv_name] = inv.get("id", "")
                # Also index first word for partial matching
                first_word = inv_name.split()[0] if inv_name else ""
                if first_word and len(first_word) > 3:
                    inv_by_name[first_word] = inv.get("id", "")

        for activity in design.get("activities", []):
            for proc in activity.get("definedProcedures", []):
                if proc.get("studyInterventionId"):
                    continue
                proc_name = proc.get("name", "").lower()
                # Try matching procedure name to intervention name
                for inv_key, inv_id in inv_by_name.items():
                    if inv_key in proc_name or proc_name in inv_key:
                        proc["studyInterventionId"] = inv_id
                        break



def _deduplicate_intercurrent_event_names(usdm: Dict[str, Any]) -> None:
    """
    Make IntercurrentEvent names unique across estimands (DDF00010).

    CORE requires globally unique names for IntercurrentEvent instances.
    When the same ICE name appears in multiple estimands, append the
    estimand's variable-of-interest name to disambiguate.
    """
    try:
        design = usdm["study"]["versions"][0]["studyDesigns"][0]
    except (KeyError, IndexError):
        return

    estimands = design.get("estimands", [])
    if not estimands:
        return

    # Collect all ICE names across all estimands to find duplicates
    name_counts: Dict[str, int] = {}
    for est in estimands:
        for ice in est.get("intercurrentEvents", []):
            name = ice.get("name", "")
            if name:
                name_counts[name] = name_counts.get(name, 0) + 1

    # Only fix names that appear more than once
    dup_names = {n for n, c in name_counts.items() if c > 1}
    if not dup_names:
        return

    # Disambiguate by appending estimand context
    for est in estimands:
        # Use the endpoint/variable name as context
        est_context = est.get("name", "") or est.get("summaryMeasure", "")
        # Try variableOfInterestId as fallback
        if not est_context:
            est_context = est.get("variableOfInterestId", est.get("id", ""))

        for ice in est.get("intercurrentEvents", []):
            name = ice.get("name", "")
            if name in dup_names and est_context:
                ice["name"] = f"{name} ({est_context})"


def _sanitize_narrative_xhtml(usdm: Dict[str, Any]) -> None:
    """
    Sanitize NarrativeContentItem text to valid XHTML (DDF00187).

    Escapes bare '&' characters that are not part of XML entities,
    which cause XHTML parsing failures in the CORE engine.
    """
    try:
        version = usdm["study"]["versions"][0]
    except (KeyError, IndexError):
        return

    # Pattern: & not followed by a valid XML entity reference
    amp_pattern = re.compile(r"&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)")

    for nc in version.get("narrativeContentItems", []):
        # Fix the name field (used in section headers)
        name = nc.get("name", "")
        if "&" in name:
            nc["name"] = amp_pattern.sub("&amp;", name)

        # Fix the text/content field
        text = nc.get("text", "")
        if "&" in text:
            nc["text"] = amp_pattern.sub("&amp;", text)

        # Also check sectionTitle if present
        title = nc.get("sectionTitle", "")
        if title and "&" in title:
            nc["sectionTitle"] = amp_pattern.sub("&amp;", title)


_INDICATION_TO_THERAPEUTIC_AREA: Dict[str, tuple] = {
    # keyword (lowercase) → (NCI code, decode label)
    "cancer": ("C17998", "Oncology"),
    "tumor": ("C17998", "Oncology"),
    "carcinoma": ("C17998", "Oncology"),
    "lymphoma": ("C17998", "Oncology"),
    "leukemia": ("C17998", "Oncology"),
    "myeloma": ("C17998", "Oncology"),
    "cardiac": ("C2931", "Cardiovascular"),
    "cardio": ("C2931", "Cardiovascular"),
    "heart failure": ("C2931", "Cardiovascular"),
    "atrial": ("C2931", "Cardiovascular"),
    "hypertension": ("C2931", "Cardiovascular"),
    "coronary": ("C2931", "Cardiovascular"),
    "diabetes": ("C16726", "Metabolic Disease"),
    "metabolic": ("C16726", "Metabolic Disease"),
    "obesity": ("C16726", "Metabolic Disease"),
    "glycemic": ("C16726", "Metabolic Disease"),
    "alzheimer": ("C16910", "Neurology"),
    "parkinson": ("C16910", "Neurology"),
    "neurolog": ("C16910", "Neurology"),
    "epilep": ("C16910", "Neurology"),
    "multiple sclerosis": ("C16910", "Neurology"),
    "rheumatoid": ("C20993", "Immunology"),
    "immunolog": ("C20993", "Immunology"),
    "autoimmune": ("C20993", "Immunology"),
    "psoriasis": ("C20993", "Immunology"),
    "crohn": ("C20993", "Immunology"),
    "lupus": ("C20993", "Immunology"),
    "renal": ("C16540", "Nephrology"),
    "kidney": ("C16540", "Nephrology"),
    "chronic kidney": ("C16540", "Nephrology"),
    "hepat": ("C71844", "Hepatology"),
    "liver": ("C71844", "Hepatology"),
    "respiratory": ("C16542", "Pulmonology"),
    "asthma": ("C16542", "Pulmonology"),
    "copd": ("C16542", "Pulmonology"),
    "pulmonary": ("C16542", "Pulmonology"),
    "infection": ("C16320", "Infectious Disease"),
    "viral": ("C16320", "Infectious Disease"),
    "bacterial": ("C16320", "Infectious Disease"),
    "hiv": ("C16320", "Infectious Disease"),
    "psychiatric": ("C16326", "Psychiatry"),
    "depression": ("C16326", "Psychiatry"),
    "schizophrenia": ("C16326", "Psychiatry"),
    "anxiety": ("C16326", "Psychiatry"),
    "ophthalmolog": ("C16533", "Ophthalmology"),
    "retinal": ("C16533", "Ophthalmology"),
    "macular": ("C16533", "Ophthalmology"),
    "dermatolog": ("C16327", "Dermatology"),
    "skin": ("C16327", "Dermatology"),
    "eczema": ("C16327", "Dermatology"),
}


def _populate_therapeutic_areas(usdm: Dict[str, Any]) -> None:
    """
    Derive businessTherapeuticAreas on StudyVersion from indication names.

    Scans placed indications and maps indication text to NCI therapeutic
    area codes.  Only populates if not already set by extraction.
    """
    try:
        version = usdm["study"]["versions"][0]
        design = version["studyDesigns"][0]
    except (KeyError, IndexError):
        return

    # Skip if already populated by an extraction agent
    if version.get("businessTherapeuticAreas"):
        return

    # Collect text to search: indication names + study name
    search_texts = []
    for ind in design.get("indications", []):
        search_texts.append(ind.get("name", "").lower())
        search_texts.append(ind.get("description", "").lower())
    search_texts.append(usdm.get("study", {}).get("name", "").lower())
    search_texts.append(usdm.get("study", {}).get("description", "").lower())
    combined = " ".join(search_texts)

    seen_codes: set = set()
    tas = []
    for keyword, (nci_code, label) in _INDICATION_TO_THERAPEUTIC_AREA.items():
        if keyword in combined and nci_code not in seen_codes:
            seen_codes.add(nci_code)
            tas.append({
                "id": str(uuid.uuid4()).replace("-", "_"),
                "code": nci_code,
                "codeSystem": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl",
                "codeSystemVersion": "2024-09-27",
                "decode": label,
                "instanceType": "Code",
            })

    if tas:
        version["businessTherapeuticAreas"] = tas


def _ensure_sponsor_identifier(usdm: Dict[str, Any]) -> None:
    """
    Post-processing to fix DDF00172 (sponsor identifier), DDF00201 (sponsor
    role), DDF00012 (main timeline), and DDF00101 (interventions).

    1. Ensures organizations referenced by studyRoles and studyIdentifiers
       are present on the version.
    2. Ensures at least one ScheduleTimeline exists with ``mainTimeline``
       set to ``true`` (DDF00012).
    3. Populates ``studyInterventionIds`` on the design from the version's
       ``studyInterventions`` (DDF00101).
    """
    try:
        version = usdm["study"]["versions"][0]
        design = version["studyDesigns"][0]
    except (KeyError, IndexError):
        return

    # --- DDF00012: Ensure at least one main ScheduleTimeline ---
    timelines = design.get("scheduleTimelines", [])
    has_main = any(tl.get("mainTimeline") is True for tl in timelines)
    if not has_main:
        if timelines:
            # Mark the first timeline as main
            timelines[0]["mainTimeline"] = True
        else:
            # Synthesize a main timeline from existing encounter data
            timeline_id = str(uuid.uuid4()).replace("-", "_")

            epochs = design.get("epochs", [])
            epoch_ids = [ep["id"] for ep in epochs] if epochs else []

            # Use cached encounter→epoch mapping captured during entity placement.
            # The map values may be stale header-structure epoch IDs (e.g. "epoch_1")
            # that need resolving to actual USDM epoch entity IDs (e.g. "epoch_v_1").
            raw_enc_epoch_map = design.pop("_encounterEpochMap", {})
            header_epochs = design.get("_headerEpochs", [])

            # Build stale→USDM epoch ID lookup by matching epoch names
            _stale_to_usdm: Dict[str, str] = {}
            if header_epochs and epochs:
                hdr_id_to_name = {ep["id"]: ep.get("name", "") for ep in header_epochs}
                usdm_name_to_id: Dict[str, str] = {}
                for ep in epochs:
                    usdm_name_to_id[_normalize_epoch_name(ep.get("name", ""))] = ep["id"]
                for hdr_id, hdr_name in hdr_id_to_name.items():
                    resolved = usdm_name_to_id.get(_normalize_epoch_name(hdr_name))
                    if resolved:
                        _stale_to_usdm[hdr_id] = resolved

            valid_epoch_set = set(epoch_ids)
            _enc_epoch_map: Dict[str, str] = {}
            for enc_id, stale_epoch_id in raw_enc_epoch_map.items():
                if stale_epoch_id in valid_epoch_set:
                    _enc_epoch_map[enc_id] = stale_epoch_id
                else:
                    resolved = _stale_to_usdm.get(stale_epoch_id)
                    if resolved:
                        _enc_epoch_map[enc_id] = resolved

            # Restore the resolved map so _normalize_codelists can set
            # epochId on encounter objects for UI column grouping.
            design["_encounterEpochMap"] = _enc_epoch_map

            def _match_epoch(enc_name: str) -> Optional[str]:
                """Match an encounter name to the best epoch by keyword."""
                low = enc_name.lower()
                for ep in epochs:
                    ep_name = ep.get("name", "").lower()
                    if "screen" in low and "screen" in ep_name:
                        return ep["id"]
                    if ("cycle" in low or "treatment" in low or "randomiz" in low) and ("treatment" in ep_name or "cycle" in ep_name):
                        return ep["id"]
                    if ("discon" in low or "end of" in low or "completion" in low or "eot" in low) and ("end" in ep_name or "discon" in ep_name or "eot" in ep_name):
                        return ep["id"]
                    if ("follow" in low or "survival" in low or "ltfu" in low) and ("follow" in ep_name or "ltfu" in ep_name):
                        return ep["id"]
                    if "fu visit" in low and "fu visit" in ep_name:
                        return ep["id"]
                return None

            # Build scheduled instances from extracted SoA tick data (activity_timepoints)
            # Group by encounterId so each instance lists all activities performed at that encounter.
            # Fall back to one empty instance per encounter if no tick data available.
            sched_instances_raw = design.pop("_scheduledInstances", [])

            instances: list = []
            # Collect footnoteRefs per encounter (union of all cell-level refs)
            enc_footnote_labels: dict = {}  # enc_id -> set of footnote labels
            if sched_instances_raw:
                from collections import defaultdict
                enc_to_activities: dict = defaultdict(list)
                for si in sched_instances_raw:
                    enc_id = si.get("encounterId")
                    act_id = si.get("activityId")
                    if enc_id and act_id:
                        enc_to_activities[enc_id].append(act_id)
                    # Collect footnote labels for this encounter
                    fn_refs = si.get("footnoteRefs", [])
                    if fn_refs and enc_id:
                        enc_footnote_labels.setdefault(enc_id, set()).update(fn_refs)

                enc_map = {enc.get("id"): enc for enc in design.get("encounters", []) if enc.get("id")}
                # One instance per encounter in visit order — including
                # encounters with no tick data, so a sparse SoA extraction
                # can't drop visits from the timeline
                ordered_enc_ids = [e for e in enc_map] + [e for e in enc_to_activities if e not in enc_map]
                for enc_id in ordered_enc_ids:
                    enc = enc_map.get(enc_id, {})
                    enc_name = enc.get("name", enc_id)
                    instance = {
                        "id": str(uuid.uuid4()).replace("-", "_"),
                        "name": enc_name,
                        "epochId": _enc_epoch_map.get(enc_id) or enc.get("epochId") or _match_epoch(enc_name),
                        "encounterId": enc_id,
                        "instanceType": "ScheduledActivityInstance",
                    }
                    if enc_to_activities.get(enc_id):
                        instance["activityIds"] = enc_to_activities[enc_id]
                    instances.append(instance)
            else:
                # No tick data — create one instance per encounter (no activityIds)
                for enc in design.get("encounters", []):
                    enc_id = enc.get("id")
                    enc_name = enc.get("name", "Visit")
                    if enc_id:
                        instances.append({
                            "id": str(uuid.uuid4()).replace("-", "_"),
                            "name": enc_name,
                            "epochId": _enc_epoch_map.get(enc_id) or _match_epoch(enc_name),
                            "encounterId": enc_id,
                            "instanceType": "ScheduledActivityInstance",
                        })

            # ── SoAFootnotes: build from header_structure footnotes ─────────
            _build_soa_footnotes(design, instances, enc_footnote_labels,
                                 sched_instances_raw)

            # entryId should reference the first encounter or activity
            entry_id = instances[0]["id"] if instances else None

            # entryCondition describes when the timeline starts
            timeline = {
                "id": timeline_id,
                "name": "Main Study Timeline",
                "description": "Primary schedule of assessments",
                "mainTimeline": True,
                "entryCondition": "Informed consent signed",
                "entryId": entry_id,
                "instanceType": "ScheduleTimeline",
                "plannedDuration": {
                    "id": str(uuid.uuid4()).replace("-", "_"),
                    "durationWillVary": True,
                    "reasonDurationWillVary": "Duration depends on individual subject progression and follow-up.",
                    "text": "Variable",
                    "instanceType": "Duration",
                },
                "timings": [],
                "instances": instances,
            }
            timelines.append(timeline)
            design["scheduleTimelines"] = timelines

    # Wire extracted schedule exits into the main timeline
    pending_exits = design.pop("_pendingExits", [])
    if pending_exits:
        main_tl = next((tl for tl in design.get("scheduleTimelines", [])
                        if tl.get("mainTimeline")), None)
        if main_tl:
            exits = main_tl.setdefault("exits", [])
            for ex in pending_exits:
                if not ex.get("instanceType"):
                    ex["instanceType"] = "ScheduleTimelineExit"
                exits.append(ex)

    # --- DDF00101: Wire up studyInterventionIds on design ---
    # (Interventions may still be on design at this point; they get moved
    # to version by _ensure_study_design_type which runs later.)
    all_interventions = design.get("studyInterventions", []) + version.get("studyInterventions", [])
    if all_interventions and not design.get("studyInterventionIds"):
        design["studyInterventionIds"] = [
            inv.get("id") for inv in all_interventions if inv.get("id")
        ]

    # --- DDF00101: Ensure at least one procedure references a study intervention ---
    # CORE requires that for interventional studies, at least one Procedure has
    # studyInterventionIds linking to a StudyIntervention.
    procedures = design.get("procedures", [])
    has_proc_inv_link = any(
        p.get("studyInterventionIds") for p in procedures
    )
    if all_interventions and not has_proc_inv_link:
        # Find investigational interventions (type decode contains "Investigational")
        inv_interventions = [
            inv for inv in all_interventions
            if inv.get("id") and (
                "investigational" in (inv.get("type", {}).get("decode", "") or "").lower()
                or "investigational" in (inv.get("role", {}).get("decode", "") or "").lower()
            )
        ]
        if not inv_interventions:
            # Fall back to first intervention
            inv_interventions = [all_interventions[0]]

        for inv in inv_interventions:
            inv_id = inv.get("id")
            inv_name = inv.get("name", "Study Drug Administration")
            # Check if a procedure with similar name already exists
            matched_proc = next(
                (p for p in procedures
                 if inv_name.lower() in (p.get("name", "").lower())),
                None
            )
            if matched_proc:
                matched_proc.setdefault("studyInterventionIds", []).append(inv_id)
            else:
                # Create a new procedure linked to this intervention
                procedures.append({
                    "id": str(uuid.uuid4()).replace("-", "_"),
                    "name": f"{inv_name} Administration",
                    "procedureType": "Study Drug Administration",
                    # Procedure.code is required (1); NCIt C70962 "Agent
                    # Administration" — administration of a pharmaceutical product
                    "code": {
                        "id": str(uuid.uuid4()),
                        "code": "C70962",
                        "codeSystem": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl",
                        "codeSystemVersion": "2024-09-27",
                        "decode": "Agent Administration",
                        "instanceType": "Code",
                    },
                    "studyInterventionIds": [inv_id],
                    "instanceType": "Procedure",
                })
        design["procedures"] = procedures


def _build_soa_footnotes(design: Dict[str, Any],
                          instances: List[Dict[str, Any]],
                          enc_footnote_labels: Dict[str, set],
                          sched_instances_raw: List[Dict[str, Any]]) -> None:
    """
    Build SoAFootnote objects from header_structure footnotes and wire
    footnoteIds onto ScheduledActivityInstance objects.

    Footnote text comes from the header_structure entity (vision extraction).
    If the vision LLM missed some footnotes, falls back to PDF text extraction.
    Footnote labels come from cellFootnotes in provenance / footnoteRefs on
    scheduled_instance entities.
    """
    import re as _re

    # Collect ALL unique footnote labels referenced by any cell
    all_labels: set = set()
    for si in sched_instances_raw:
        fn_refs = si.get("footnoteRefs", [])
        if fn_refs:
            all_labels.update(fn_refs)
    for labels in enc_footnote_labels.values():
        all_labels.update(labels)

    if not all_labels:
        return

    # Try to get footnote text from header_structure stored in design notes
    # or from the _headerFootnotes stash (set by _generate)
    raw_footnotes: List[str] = design.pop("_headerFootnotes", [])

    # Parse footnote strings into {label: text} map
    # Formats: "a. text...", "1. text...", "a) text...", "*. text..."
    label_to_text: Dict[str, str] = {}
    for fn_str in raw_footnotes:
        fn_str = fn_str.strip()
        # Match: "a. text", "aa. text", "1. text", "*. text", "a) text"
        m = _re.match(r'^([a-zA-Z]+|\d+|\*)[.\)]\s*(.+)', fn_str, _re.DOTALL)
        if m:
            label = m.group(1).lower()
            text = m.group(2).strip()
            label_to_text[label] = text

    # ── PDF text fallback for missing footnote text ──────────────────────
    # If the vision LLM missed some footnotes, try to extract them from the
    # PDF text layer (deterministic, no LLM involved).
    missing_labels = {lbl.lower() for lbl in all_labels} - set(label_to_text.keys())
    if missing_labels:
        pdf_fallback = _extract_footnotes_from_pdf_text(design)
        filled = 0
        for lbl, txt in pdf_fallback.items():
            if lbl in missing_labels and txt:
                label_to_text[lbl] = txt
                filled += 1
        if filled:
            logger.info(f"PDF text fallback filled {filled}/{len(missing_labels)} missing footnote(s)")

    # Create SoAFootnote objects for each referenced label
    label_to_footnote_id: Dict[str, str] = {}
    soa_footnotes: List[Dict[str, Any]] = []
    for label in sorted(all_labels):
        fn_id = str(uuid.uuid4()).replace("-", "_")
        label_to_footnote_id[label.lower()] = fn_id
        soa_footnotes.append({
            "id": fn_id,
            "instanceType": "SoAFootnote",
            "label": label,
            "text": label_to_text.get(label.lower(), ""),
        })

    if soa_footnotes:
        design.setdefault("soaFootnotes", []).extend(soa_footnotes)

    # Wire footnoteIds onto instances based on per-cell footnoteRefs
    # Build a map: enc_id -> set of footnote IDs
    enc_to_fn_ids: Dict[str, List[str]] = {}
    for enc_id, labels in enc_footnote_labels.items():
        fn_ids = []
        for lbl in sorted(labels):
            fn_id = label_to_footnote_id.get(lbl.lower())
            if fn_id:
                fn_ids.append(fn_id)
        if fn_ids:
            enc_to_fn_ids[enc_id] = fn_ids

    for inst in instances:
        enc_id = inst.get("encounterId")
        if enc_id and enc_id in enc_to_fn_ids:
            inst["footnoteIds"] = enc_to_fn_ids[enc_id]


def _extract_footnotes_from_pdf_text(design: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract footnote label→text from the PDF text layer of SoA pages.

    This is a deterministic fallback when the vision LLM misses footnotes.
    Parses lines like "n. Some footnote text here" from the raw PDF text.
    """
    import re as _re

    pdf_path: str = design.get("_pdfPath", "")
    soa_pages: List[int] = design.get("_soaSourcePages", [])
    if not pdf_path or not soa_pages:
        return {}

    try:
        from core.pdf_utils import extract_text_from_pages
        # Pages in source_pages are 0-indexed (from soa_finder)
        raw_text = extract_text_from_pages(pdf_path, soa_pages,
                                           max_chars_per_page=15000)
        if not raw_text:
            return {}
    except Exception:
        return {}

    # Parse footnotes from the raw text.
    # Clinical protocol footnotes appear in various formats:
    #   "a. Some text"  (letter + period + space)
    #   "a) Some text"  (letter + paren + space)
    #   "a Some text"   (letter + space, no punctuation — common in PDF text layer)
    #   "1. Some text"  (number + period)
    label_to_text: Dict[str, str] = {}
    lines = raw_text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Match: "a. text", "a) text" (letter + punctuation)
        m = _re.match(r'^([a-zA-Z])[.\)]\s+(.+)', line)
        if not m:
            # Match: "1. text", "16. text" (number + punctuation)
            m = _re.match(r'^(\d+)[.\)]\s+(.+)', line)
        if not m:
            # Match: "a Some text" (single letter + space + uppercase or long text)
            # Only match if the text after the letter is substantial (>20 chars)
            # to avoid false positives from table cell content like "X" markers
            m2 = _re.match(r'^([a-zA-Z])\s+([A-Z].{20,})', line)
            if m2:
                m = m2
        if m:
            label = m.group(1).lower()
            text = m.group(2).strip()
            # Continuation: if next lines don't start a new footnote, append them
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                if not next_line:
                    break
                # Check if next line starts a new footnote (letter or number)
                if _re.match(r'^([a-zA-Z])[.\)]\s+', next_line):
                    break
                if _re.match(r'^(\d+)[.\)]\s+', next_line):
                    break
                if _re.match(r'^([a-zA-Z])\s+[A-Z].{20,}', next_line):
                    break
                # Check if next line is a page separator or abbreviations section
                if next_line.startswith('--- Page'):
                    break
                if next_line.startswith('Abbreviations:'):
                    break
                text += ' ' + next_line
                j += 1
            label_to_text[label] = text
            i = j
        else:
            i += 1

    return label_to_text


def _ensure_study_definition_document(usdm: Dict[str, Any]) -> None:
    """Ensure study.documentedBy has at least one StudyDefinitionDocument.

    Every protocol has exactly one governing document. If narrative_agent
    didn't extract one (e.g. title page wasn't recognized), synthesize a
    default one from the study name so `documentedBy` — and its required
    `language`/`type`/`templateName` fields — are never left empty.
    """
    study = usdm.get("study", {})
    if study.get("documentedBy"):
        return
    _place_study_definition_document(usdm, {
        "name": study.get("name") or "Protocol",
        "documentType": "Protocol",
        "language": "en",
    })


def _link_document_versions(usdm: Dict[str, Any]) -> None:
    """Attach staged `document_version` entities to documentedBy[0].versions.

    document_version entities come from docstructure_agent, which runs in
    parallel with narrative_agent (the source of study_definition_document),
    so they're staged in study._pendingDocumentVersions during placement and
    linked here, after _ensure_study_definition_document guarantees a parent
    document exists.
    """
    study = usdm.get("study", {})
    pending = study.pop("_pendingDocumentVersions", [])
    if not pending:
        return

    documents = study.get("documentedBy") or []
    if not documents:
        return
    versions = documents[0].setdefault("versions", [])

    for raw in pending:
        version = {
            "id": raw.get("id") or str(uuid.uuid4()),
            "version": raw.get("version") or raw.get("versionNumber") or "1.0",
            "status": _resolve_ct_code(raw.get("status") or "Final", "C188723"),
            "instanceType": "StudyDefinitionDocumentVersion",
        }
        versions.append(version)


def _alnum(text: Any) -> str:
    return re.sub(r"[^a-z0-9]", "", str(text or "").lower())


def _resolve_epoch_ref(ref: Optional[str], epochs: List[Dict[str, Any]]) -> Optional[str]:
    """Epoch id for a rule's provisional reference ("epoch_period1" -> "Period 1").

    Exact name match first, then containment (min. 4 characters) preferring
    the closest-length name, so "epoch_followup" picks "Follow-up/ED" rather
    than "Additional Follow-up for TE ADA".
    """
    key = _alnum(re.sub(r"^(?:epoch|element|elem)[_\- ]*", "", str(ref or ""), flags=re.IGNORECASE))
    if len(key) < 3:
        return None
    names = [(e["id"], _alnum(e.get("name"))) for e in epochs if e.get("id")]
    for eid, name in names:
        if name == key:
            return eid
    close = [(abs(len(name) - len(key)), eid) for eid, name in names
             if len(name) >= 4 and len(key) >= 4 and (key in name or name in key)]
    return min(close)[1] if close else None


def _link_transition_rules(usdm: Dict[str, Any]) -> None:
    """Attach extracted transition rules to the design's elements/encounters.

    USDM 4.0 holds a TransitionRule on a StudyElement (transitionStartRule /
    transitionEndRule) or an Encounter. For a rule from A to B, in each arm
    the last element matching A gets it as its end rule and the first
    element matching B as its start rule. A reference matches an element by
    the phase named at the end of its name ("... - Maintenance Treatment") or
    by the element's epoch ("epoch_period1" -> epoch "Period 1"); a rule
    between two visits ("visit_1" -> "visit_2") ends/starts those encounters.
    Each slot holds one rule (the first extracted); a rule with no
    resolvable link, or whose slots are all taken, is logged, not forced
    onto an unrelated element.
    """
    study = usdm.get("study", {})
    pending = study.pop("_pendingTransitionRules", [])
    if not pending:
        return
    try:
        design = study["versions"][0]["studyDesigns"][0]
    except (KeyError, IndexError):
        return
    epochs, encounters = design.get("epochs", []), design.get("encounters", [])
    epoch_order = {e["id"]: i for i, e in enumerate(epochs)}
    elements = {e["id"]: e for e in design.get("elements", [])}
    cells = design.get("studyCells", [])

    def _rule(raw: Dict[str, Any]) -> Dict[str, Any]:
        text = (raw.get("text") or raw.get("description") or raw.get("name") or "").strip()
        rule = {"id": str(uuid.uuid4()), "name": raw.get("name") or text[:60], "text": text,
                "instanceType": "TransitionRule"}
        if raw.get("description") and raw["description"] != text:
            rule["description"] = raw["description"]
        return rule

    def _arm_elements(arm_id: str) -> List[tuple]:
        """(epoch id, element) for the arm, in epoch then cell order."""
        arm_cells = sorted((c for c in cells if c.get("armId") == arm_id),
                           key=lambda c: epoch_order.get(c.get("epochId"), 0))
        return [(c["epochId"], elements[eid]) for c in arm_cells for eid in c.get("elementIds", []) if eid in elements]

    def _matching(ref: Optional[str], arm_els: List[tuple]) -> List[Dict[str, Any]]:
        key = _alnum(re.sub(r"^(?:epoch|element|elem)[_\- ]*", "", str(ref or ""), flags=re.IGNORECASE))
        if len(key) < 3:
            return []
        by_phase = []
        for _, el in arm_els:
            phase = _alnum(str(el.get("name", "")).rsplit(" - ", 1)[-1])
            if phase == key or (len(key) >= 4 and len(phase) >= 4 and (key in phase or phase in key)):
                by_phase.append(el)
        if by_phase:
            return by_phase
        epoch_id = _resolve_epoch_ref(ref, epochs)
        return [el for ep, el in arm_els if epoch_id and ep == epoch_id]

    arms = [a["id"] for a in design.get("arms", []) if a.get("id")]
    per_arm = {arm: _arm_elements(arm) for arm in arms}
    placed, unplaced = 0, []
    for raw in pending:
        from_ref, to_ref = raw.get("fromElementId"), raw.get("toElementId")
        used = False
        for arm_els in per_arm.values():
            for el in _matching(from_ref, arm_els)[-1:]:
                if "transitionEndRule" not in el:
                    el["transitionEndRule"] = _rule(raw)
                    used = True
            for el in _matching(to_ref, arm_els)[:1]:
                if "transitionStartRule" not in el:
                    el["transitionStartRule"] = _rule(raw)
                    used = True
        if not used:  # visit-to-visit rules
            enc_from = _instance_by_visit(from_ref and str(from_ref).replace("_", " "), encounters)
            enc_to = _instance_by_visit(to_ref and str(to_ref).replace("_", " "), encounters)
            if enc_from is not None and "transitionEndRule" not in enc_from:
                enc_from["transitionEndRule"] = _rule(raw)
                used = True
            if enc_to is not None and "transitionStartRule" not in enc_to:
                enc_to["transitionStartRule"] = _rule(raw)
                used = True
        if used:
            placed += 1
        else:
            unplaced.append(raw.get("name"))
    logger.info(f"Placed {placed}/{len(pending)} transition rules"
                + (f"; not placed (no resolvable link or slot taken): {unplaced}" if unplaced else ""))


def _link_conditions(usdm: Dict[str, Any]) -> None:
    """Place extracted conditions in StudyVersion.conditions.

    A Condition needs a name and text (the condition itself); label defaults
    to the name. contextIds/appliesToIds (0..*) are left unset: the
    extraction doesn't say which activity a condition concerns, and a guess
    from word overlap links the wrong activity too often to be useful.
    """
    study = usdm.get("study", {})
    pending = study.pop("_pendingConditions", [])
    if not pending:
        return
    try:
        version = study["versions"][0]
    except (KeyError, IndexError):
        return
    conditions = []
    for raw in pending:
        name = (raw.get("name") or "").strip()
        text = (raw.get("text") or raw.get("description") or name).strip()
        if not name or not text:
            continue
        cond = {"id": str(uuid.uuid4()), "name": name, "label": raw.get("label") or name, "text": text,
                "instanceType": "Condition"}
        if raw.get("description"):
            cond["description"] = raw["description"]
        conditions.append(cond)
    version["conditions"] = conditions
    logger.info(f"Placed {len(conditions)} conditions")


_XHTML_NS = "http://www.w3.org/1999/xhtml"


def _classify_document_versions(doc_versions: List[Dict[str, Any]], amendments: List[Dict[str, Any]]) -> tuple:
    """(current, original) StudyDefinitionDocumentVersion; either may be None.

    Document versions aren't reliably ordered and their labels differ from the
    amendment's ("Amendment e" vs version "e", "Amendment a" vs "YDAF(a)"), so
    each is identified through the amendment chain:
    - the latest amendment is the one whose resulting version no other
      amendment amends (else the last listed); its document version is the one
      labelled like its newVersion or its amendment number — that is the
      current version;
    - the original is the version labelled Original/Initial, else the one no
      amendment produced.
    Without an amendment match, the current version is the unique Approved one,
    else the last listed; a lone version is both current and original.
    """
    if not doc_versions:
        return None, None

    def lab(text: Any) -> str:
        return _alnum(text)

    def labels(amendment: Dict[str, Any]) -> set:
        return {lab(amendment.get("newVersion")), lab(amendment.get("number"))} - {""}

    amended_from = {lab(a.get("previousVersion")) for a in amendments}
    ends = [a for a in amendments if lab(a.get("newVersion")) and lab(a.get("newVersion")) not in amended_from]
    latest = (ends or amendments or [None])[-1]

    # A version already holding the protocol sections was chosen as current earlier
    holders = [dv for dv in doc_versions if dv.get("contents")]
    current = holders[0] if len(holders) == 1 else None
    if current is None and latest is not None:
        hit = [dv for dv in doc_versions if lab(dv.get("version")) in labels(latest)]
        if len(hit) == 1:
            current = hit[0]
    if current is None:
        approved = [dv for dv in doc_versions if (dv.get("status") or {}).get("code") == "C25425"]
        current = approved[0] if len(approved) == 1 else doc_versions[-1]

    original = None
    named = [dv for dv in doc_versions if re.search(r"original|initial", str(dv.get("version") or ""), re.IGNORECASE)]
    if len(named) == 1:
        original = named[0]
    elif len(doc_versions) == 1:
        original = doc_versions[0]
    else:
        produced = set().union(*[labels(a) for a in amendments]) if amendments else set()
        unamended = [dv for dv in doc_versions if lab(dv.get("version")) not in produced]
        if len(unamended) == 1:
            original = unamended[0]
        elif len(doc_versions) == 2 and current is not None:
            original = next(dv for dv in doc_versions if dv is not current)
    return current, original


def _build_document_contents(usdm: Dict[str, Any]) -> None:
    """Build the protocol's section hierarchy (USDM 4.0 NarrativeContent).

    A protocol section is a NarrativeContent — name, section number and
    title, whether to display them, links to its parent's children,
    previous/next section and its text item — held in the current
    StudyDefinitionDocumentVersion.contents; the text itself is the
    NarrativeContentItem in StudyVersion.narrativeContentItems. Sections are
    chained in document order (each top-level section followed by its
    subsections). A section whose text is not XHTML yet (a parent section
    holding only its title) is wrapped so every item text is valid XHTML.
    """
    import html

    study = usdm.get("study", {})
    sections = study.pop("_pendingSections", [])
    if not sections:
        return
    try:
        version = study["versions"][0]
    except (KeyError, IndexError):
        return
    documents = study.get("documentedBy") or []
    if not documents:
        logger.warning("No protocol document to hold the sections; NarrativeContent not built")
        return
    doc_versions = documents[0].setdefault("versions", [])
    if not doc_versions:
        # The document structure stage found no version: record the protocol
        # version being converted (its version identifier; status Final, as
        # elsewhere when none is extracted) so the sections have a home
        doc_versions.append({
            "id": str(uuid.uuid4()),
            "version": str(version.get("versionIdentifier") or "1.0"),
            "status": _resolve_ct_code("Final", "C188723"),
            "instanceType": "StudyDefinitionDocumentVersion",
        })
    target, _ = _classify_document_versions(doc_versions, study.get("_amendmentInfo", []))

    items = {item.get("id"): item for item in version.get("narrativeContentItems", [])}
    by_id = {s["id"]: s for s in sections if s["id"] in items}

    # Document order: top-level sections by order, each followed by its children
    ordered: List[Dict[str, Any]] = []
    children_of: Dict[str, List[str]] = {}
    seen = set()
    tops = sorted([s for s in by_id.values() if s["topLevel"]], key=lambda s: s.get("order") or 0)
    for top in tops:
        ordered.append(top); seen.add(top["id"])
        kids = [by_id[c] for c in top["childIds"] if c in by_id]
        children_of[top["id"]] = [k["id"] for k in kids]
        for kid in kids:
            if kid["id"] not in seen:
                ordered.append(kid); seen.add(kid["id"])
    ordered += [s for s in by_id.values() if s["id"] not in seen]

    content_id = {s["id"]: f"nc_{n}" for n, s in enumerate(ordered, 1)}
    names_used: Dict[str, int] = {}
    contents = []
    for n, s in enumerate(ordered):
        name = s.get("name") or s.get("sectionTitle") or f"Section {s.get('sectionNumber') or n + 1}"
        names_used[name] = names_used.get(name, 0) + 1
        if names_used[name] > 1:  # names must be unique across sections
            name = f"{name} ({s.get('sectionNumber') or names_used[name]})"
        content = {
            "id": content_id[s["id"]],
            "name": name,
            "displaySectionNumber": bool(s.get("sectionNumber")),
            "displaySectionTitle": bool(s.get("sectionTitle") or s.get("name")),
            "contentItemId": s["id"],
            "instanceType": "NarrativeContent",
        }
        if s.get("sectionNumber"):
            content["sectionNumber"] = str(s["sectionNumber"])
        if s.get("sectionTitle") or s.get("name"):
            content["sectionTitle"] = s.get("sectionTitle") or s["name"]
        if children_of.get(s["id"]):
            content["childIds"] = [content_id[c] for c in children_of[s["id"]]]
        if n > 0:
            content["previousId"] = content_id[ordered[n - 1]["id"]]
        if n < len(ordered) - 1:
            content["nextId"] = content_id[ordered[n + 1]["id"]]
        contents.append(content)

    for item in items.values():
        text = item.get("text") or item.get("name") or ""
        if not text.lstrip().startswith("<"):
            item["text"] = f'<div xmlns="{_XHTML_NS}"><p>{html.escape(text, quote=False)}</p></div>'
    target["contents"] = contents
    if not version.get("documentVersionIds"):
        version["documentVersionIds"] = [target["id"]]
    logger.info(f"Built {len(contents)} NarrativeContent sections under document version {target.get('version')!r}")


def _attach_document_version_dates(usdm: Dict[str, Any]) -> None:
    """Attach staged document-version dates to their StudyDefinitionDocumentVersion.

    The original protocol's issue date (Document History) belongs to the
    original document version: the one labelled Original/Initial; with a
    single version, that version; with two, the one that isn't the current
    version (the one holding the sections). When the original can't be
    identified, the date goes to StudyVersion.dateValues rather than to an
    arbitrary document version.
    """
    study = usdm.get("study", {})
    pending = study.pop("_pendingDocVersionDates", [])
    if not pending:
        return
    try:
        version = study["versions"][0]
    except (KeyError, IndexError):
        return
    documents = study.get("documentedBy") or []
    doc_versions = documents[0].get("versions", []) if documents else []
    _, original = _classify_document_versions(doc_versions, study.get("_amendmentInfo", []))
    for raw in pending:
        date = {k: v for k, v in raw.items() if k != "documentVersionLabel"}
        target = original if _alnum(raw.get("documentVersionLabel")) == "original" else None
        (target if target is not None else version).setdefault("dateValues", []).append(date)


def _link_change_sections_to_document(usdm: Dict[str, Any]) -> None:
    """Point StudyChange.changedSections[].appliesToId at the protocol document.

    USDM 4.0 DocumentContentReference.appliesTo references a
    StudyDefinitionDocument; the document id isn't known when amendments
    are extracted, so it's wired here once documentedBy exists.
    """
    study = usdm.get("study", {})
    documents = study.get("documentedBy") or []
    if not documents or not documents[0].get("id"):
        return
    doc_id = documents[0]["id"]
    for version in study.get("versions", []):
        for amend in version.get("amendments", []):
            for change in amend.get("changes", []):
                for section in change.get("changedSections", []):
                    section["appliesToId"] = doc_id


def _link_masking_to_roles(usdm: Dict[str, Any]) -> None:
    """Attach staged maskedRoles names to matching existing StudyRole entries.

    maskedRoles (staged in study._pendingMaskedRoles by the study_design
    branch above) lists masking participants such as "Subject",
    "Investigator", "Outcome Assessor" — a different taxonomy from the
    CDISC C215480 organizational StudyRole codelist (Sponsor, CRO,
    Investigator, Statistician, ...). Per user decision, only names that
    match an existing StudyRole by name/label get StudyRole.masking set;
    unmatched names (e.g. "Subject") are skipped and logged rather than
    fabricating a new StudyRole or CDISC code.
    """
    study = usdm.get("study", {})
    pending = study.pop("_pendingMaskedRoles", [])
    if not pending:
        return

    try:
        roles = study["versions"][0]["roles"]
    except (KeyError, IndexError):
        return

    for name in pending:
        matched = False
        for role in roles:
            role_name = role.get("name") or role.get("label") or ""
            if role_name.lower() == str(name).lower():
                role["masking"] = {
                    "id": str(uuid.uuid4()).replace("-", "_"),
                    "text": "Masked",
                    "isMasked": True,
                    "instanceType": "Masking",
                }
                matched = True
        if not matched:
            logger.warning(
                "maskedRoles entry %r has no matching StudyRole; skipping "
                "masking rather than fabricating a new StudyRole", name,
            )


def _link_substances_to_products(usdm: Dict[str, Any]) -> None:
    """Build Ingredient/Substance/Strength.numerator from staged data.

    administrable_product and substance entities may be emitted in the same
    interventions-extraction wave, so placement order between them isn't
    guaranteed — both are staged during placement (._pendingProductStrengths
    / ._pendingSubstances) and resolved here. A link only produces an
    Ingredient when both a real strength value AND a matching Substance are
    present; otherwise it's skipped and logged rather than fabricated.

    Strength.name is required by USDM 4.0 but the protocol rarely names a
    strength distinctly — when the extractor did capture a real strengthName
    it's used verbatim, otherwise "<substance> <value> <unit>" (e.g.
    "Eloralintide 1.5 mg") is built from the protocol's own dosage level.

    USDM 4.0 nests Substance by value inside each Ingredient, so a substance
    shared by several products (one per strength) is emitted once per product
    with its own id — reusing the extracted id would duplicate ids.
    """
    study = usdm.get("study", {})
    pending_links = study.pop("_pendingProductStrengths", [])
    pending_substances = study.pop("_pendingSubstances", {})
    if not pending_links:
        return

    try:
        products = study["versions"][0]["administrableProducts"]
    except (KeyError, IndexError):
        return
    products_by_id = {p.get("id"): p for p in products}
    used_substance_ids: Set[str] = set()

    for link in pending_links:
        product = products_by_id.get(link.get("productId"))
        substance_data = pending_substances.get(link.get("substanceId"))
        value = link.get("value")
        if product is None or substance_data is None or value is None:
            logger.warning(
                "Skipping Strength.numerator for product %r: missing product, "
                "substance, or strength value rather than fabricating one",
                link.get("productId"),
            )
            continue

        substance_name = substance_data.get("name") or "Substance"
        quantity = {
            "id": str(uuid.uuid4()).replace("-", "_"),
            "value": float(value),
            "instanceType": "Quantity",
        }
        unit = link.get("unit")
        if unit:
            quantity["unit"] = _build_unit_alias_code(unit)

        # "Eloralintide (LY3841136)" -> "Eloralintide"; 3.0 -> "3"
        base_name = re.sub(r"\s*\([^)]*\)", "", substance_name).strip() or substance_name
        # Prefer the protocol's casing as written in the product name
        # ("Eloralintide 1.5 mg prefilled syringe" over "eloralintide") for
        # both Substance.name and Strength.name; a parenthetical code such as
        # "(LY3841136)" in the substance name is kept
        in_product = re.search(re.escape(base_name), product.get("name") or "", re.I)
        if in_product:
            substance_name = re.sub(
                re.escape(base_name), lambda _: in_product.group(0), substance_name, count=1, flags=re.I
            )
            base_name = in_product.group(0)
        value_text = f"{float(value):g}"
        default_name = " ".join(p for p in (base_name, value_text, unit) if p)

        strength = {
            "id": str(uuid.uuid4()).replace("-", "_"),
            "name": link.get("name") or default_name,
            "numerator": quantity,
            "instanceType": "Strength",
        }
        if link.get("denominatorValue") is not None:
            # Concentration, e.g. 0.3 U per 1 mL
            denominator_value = float(link["denominatorValue"])
            denominator_unit = link.get("denominatorUnit")
            denominator = {
                "id": str(uuid.uuid4()).replace("-", "_"),
                "value": denominator_value,
                "instanceType": "Quantity",
            }
            if denominator_unit:
                denominator["unit"] = _build_unit_alias_code(denominator_unit)
            strength["denominator"] = denominator
            if not link.get("name"):
                per = denominator_unit if denominator_value == 1 else f"{denominator_value:g} {denominator_unit or ''}".strip()
                strength["name"] = f"{default_name}/{per}" if per else default_name
        substance_id = substance_data.get("id")
        if not substance_id or substance_id in used_substance_ids:
            substance_id = str(uuid.uuid4()).replace("-", "_")
        used_substance_ids.add(substance_id)
        substance = {
            "id": substance_id,
            "name": substance_name,
            "strengths": [strength],
            "instanceType": "Substance",
        }
        if substance_data.get("description"):
            substance["description"] = substance_data["description"]
        if substance_data.get("codes"):
            substance["codes"] = substance_data["codes"]

        ingredient = {
            "id": str(uuid.uuid4()).replace("-", "_"),
            "role": _resolve_ct_code("Active Ingredient"),
            "substance": substance,
            "instanceType": "Ingredient",
        }
        product.setdefault("ingredients", []).append(ingredient)


_ROMAN_PHASE = {"iv": "4", "v": "5", "iii": "3", "ii": "2", "i": "1"}


def _study_phase_term(text: str) -> Optional[dict]:
    """Resolve phase text ("Phase 3", "Phase III", "phase 2/3", "Phase 1b",
    "PHASE 3") to a CDISC Trial Phase (C66737) term via its "Trial Phase N"
    synonyms (e.g. "Trial Phase 2-3" -> PHASE II/III TRIAL)."""
    if not text:
        return None
    for literal in (text, f"{text} Trial"):  # e.g. "Early Phase 1" -> "Early Phase 1 Trial"
        term = cdisc_lookup("C66737", literal)
        if term:
            return term
    t = re.sub(r"(trial|phase|study)", " ", text.lower())
    t = re.sub(r"\b(iv|v|iii|ii|i)(?=[ab]?\b)", lambda m: _ROMAN_PHASE[m.group(1)], t)
    t = re.sub(r"\s+", "", t).upper()
    if not t:
        return None
    for candidate in dict.fromkeys([t, t.replace("/", "-")]):
        term = cdisc_lookup("C66737", f"Trial Phase {candidate}") or cdisc_lookup("C66737", candidate)
        if term:
            return term
    return None


def _conform_codes_to_codelists(usdm: Dict[str, Any]) -> Dict[str, int]:
    """Re-resolve every coded attribute that isn't a term of its codelist.

    The attribute -> codelist map comes from the CDISC usdm4 CT config (e.g.
    StudyDefinitionDocumentVersion.status -> C188723, Quantity.unit ->
    C71620). Codes from LLM output, hand-maintained tables or a free-text
    NCIt search can be valid NCIt codes from the wrong codelist ("Approved
    Protocol" C70745 for a document status) or unrelated concepts ("G Force"
    for unit "g"); those are re-resolved from their decode. Codes with no
    matching term are left unchanged and logged.
    """
    stats = {"valid": 0, "fixed": 0, "unresolved": 0}

    def _conform(value: Any, codelist_id: str, where: str) -> None:
        if isinstance(value, list):
            for item in value:
                _conform(item, codelist_id, where)
            return
        if not isinstance(value, dict):
            return
        code_obj = value.get("standardCode") if value.get("instanceType") == "AliasCode" else value
        if not isinstance(code_obj, dict):
            return
        before = (code_obj.get("code"), code_obj.get("decode"))
        outcome = conform_code(code_obj, codelist_id)
        if outcome is True:
            stats["fixed"] += 1
            logger.info(f"Codelist {codelist_id}: {where} {before} -> ({code_obj['code']}, {code_obj['decode']!r})")
        elif outcome is False:
            stats["valid"] += 1
        elif code_obj.get("code"):
            stats["unresolved"] += 1
            logger.warning(f"Codelist {codelist_id}: {where} {before} matches no term; left unchanged")

    def _walk(node: Any) -> None:
        if isinstance(node, list):
            for item in node:
                _walk(item)
            return
        if not isinstance(node, dict):
            return
        instance_type = node.get("instanceType")
        if instance_type:
            for attr, value in node.items():
                codelist_id = codelist_for(instance_type, attr)
                if codelist_id and value:
                    _conform(value, codelist_id, f"{instance_type}.{attr}")
        for value in node.values():
            _walk(value)

    _walk(usdm)
    logger.info(f"Codelist conformance: {stats}")
    return stats


def _name_words(name: str) -> set:
    return set(re.findall(r"[a-z0-9]+", (name or "").lower()))


def _link_administrations_to_interventions(usdm: Dict[str, Any]) -> None:
    """Nest staged Administration entities under StudyIntervention.administrations.

    USDM 4.0 has no list container for Administration; each belongs to one
    StudyIntervention. The extractor links them via the intervention's
    administrationIds (staged before those are stripped); an administration
    without such a link goes to the intervention sharing the most name words.
    Unmatched administrations are dropped with a warning rather than
    attached to an arbitrary intervention. administrableProductId values that
    don't reference a placed product are removed.
    """
    study = usdm.get("study", {})
    pending = study.pop("_pendingAdministrations", [])
    links = study.pop("_pendingInterventionAdmins", {})
    if not pending:
        return
    try:
        version = study["versions"][0]
    except (KeyError, IndexError):
        return
    interventions = version.get("studyInterventions") or []
    if not interventions:
        try:
            interventions = version["studyDesigns"][0].get("studyInterventions") or []
        except (KeyError, IndexError):
            interventions = []
    by_id = {i.get("id"): i for i in interventions}
    owner_of = {admin_id: int_id for int_id, admin_ids in links.items() for admin_id in admin_ids}
    product_ids = {p.get("id") for p in version.get("administrableProducts", [])}

    for admin in pending:
        if admin.get("administrableProductId") not in product_ids:
            admin.pop("administrableProductId", None)
        intervention = by_id.get(owner_of.get(admin.get("id")))
        if intervention is None:
            # Most shared words; ties go to the intervention whose name is most
            # fully covered ("IV glucose rescue infusion" -> "IV glucose")
            words = _name_words(admin.get("name", ""))
            scored = []
            for inv in interventions:
                inv_words = _name_words(inv.get("name", ""))
                overlap = len(words & inv_words)
                scored.append(((overlap, overlap / len(inv_words) if inv_words else 0.0), inv))
            best = max(scored, key=lambda s: s[0], default=((0, 0.0), None))
            intervention = best[1] if best[0][0] > 0 else None
        if intervention is None:
            logger.warning(f"Administration {admin.get('name')!r} matches no study intervention; dropped")
            continue
        intervention.setdefault("administrations", []).append(admin)


_TIMING_TOKEN_RE = re.compile(r"-?\d+|[a-z]+")
# Words too generic to identify a visit on their own
_TIMING_STOPWORDS = {"visit", "window", "period", "the", "of", "and", "to", "from", "for", "a", "an",
                     "in", "at", "day", "days", "week", "weeks", "study", "summary", "design"}


def _timing_tokens(text: str) -> set:
    return {t for t in _TIMING_TOKEN_RE.findall((text or "").lower()) if t not in _TIMING_STOPWORDS}


def _best_instance(text: str, instances: List[Dict[str, Any]],
                   epoch_names: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
    """The scheduled instance best identified by `text`.

    An instance is described by its name plus its epoch's name (a visit
    named "Days -28 to -2" in the Screening epoch matches "Screening
    Window"). Numbers keep their sign ("Day -1" != "Day 1") and every number
    in the instance name must appear in `text`, so a stray ">2 weeks" can't
    select "V2 (Week -2)". Instance tokens missing from `text` count
    against it, so "Day 1 Dosing" prefers "Period 1 Day 1" over
    "Period 1 Day -1".
    """
    tokens = _timing_tokens(text)
    if not tokens:
        return None
    epoch_names = epoch_names or {}
    text_has_numbers = any(re.fullmatch(r"-?\d+", t) for t in tokens)
    per_epoch: Dict[Any, int] = {}
    for inst in instances:
        per_epoch[inst.get("epochId")] = per_epoch.get(inst.get("epochId"), 0) + 1
    best, best_score = None, float("-inf")
    for inst in instances:
        name_tokens = _timing_tokens(inst.get("name", ""))
        inst_tokens = name_tokens | _timing_tokens(epoch_names.get(inst.get("epochId"), ""))
        name_numbers = {t for t in name_tokens if re.fullmatch(r"-?\d+", t)}
        if text_has_numbers and name_numbers - tokens:
            continue
        shared = tokens & inst_tokens
        if not shared:
            continue
        # Matching only on the epoch name identifies a visit only when the
        # epoch has one visit ("Screening"), not e.g. a 16-visit treatment epoch
        if not (tokens & name_tokens) and per_epoch.get(inst.get("epochId"), 0) != 1:
            continue
        score = len(shared) - 0.5 * len(inst_tokens - tokens)
        if score > best_score:
            best, best_score = inst, score
    return best


_VISIT_NUMBER_RE = re.compile(r"\b(?:visit|v)\s*(\d+)\b", re.IGNORECASE)


def _instance_by_visit(label: Optional[str], instances: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """The instance the SoA visit label names.

    Normalised exact match first; otherwise by visit number, since labels and
    instance names spell it differently ("Visit 1" vs "V1 (Week -5)").
    """
    if not label:
        return None
    key = re.sub(r"[^a-z0-9-]+", " ", label.lower()).strip()
    exact = next((i for i in instances
                  if re.sub(r"[^a-z0-9-]+", " ", (i.get("name") or "").lower()).strip() == key), None)
    if exact:
        return exact
    number = _VISIT_NUMBER_RE.search(label)
    if number:
        same = [i for i in instances
                if any(m == number.group(1) for m in _VISIT_NUMBER_RE.findall(i.get("name") or ""))]
        if len(same) == 1:
            return same[0]
    return None


def _link_timings_to_timeline(usdm: Dict[str, Any]) -> None:
    """Attach staged Timing entities to the main ScheduleTimeline.

    Extracted timings name the visit they describe ("Period 1 Admission
    (Day -1)", "Screening Window") but their instance references are not
    resolvable, so each is anchored to the timeline instance sharing the
    most distinctive name tokens; its anchor ("First Dose", "Last Dose",
    "Previous Visit") becomes relativeToScheduledInstanceId when an instance
    matches it. Direction is expressed by the CDISC C201264 type (Before /
    After / Fixed Reference) with an unsigned ISO 8601 value; free-text
    types such as "Within"/"Between" are derived from the value's sign.
    Timings that match no instance (study-level durations such as "Total
    Treatment Period Duration") are dropped with a log message rather than
    left with dangling references.
    """
    study = usdm.get("study", {})
    pending = study.pop("_pendingTimings", [])
    if not pending:
        return
    try:
        design = study["versions"][0]["studyDesigns"][0]
    except (KeyError, IndexError):
        return
    timeline = next((t for t in design.get("scheduleTimelines", []) if t.get("mainTimeline")), None)
    instances = (timeline or {}).get("instances") or []
    if not instances:
        logger.warning(f"{len(pending)} timing(s) dropped: no main timeline instances to anchor them to")
        return

    epoch_names = {e.get("id"): e.get("name", "") for e in design.get("epochs", [])}
    timings, dropped = [], []
    for raw in pending:
        name = raw.get("name") or ""
        source = (_instance_by_visit(raw.get("visitName"), instances)
                  or _best_instance(raw.get("visitName") or "", instances, epoch_names)
                  or _best_instance(name, instances, epoch_names))
        if source is None:
            dropped.append(name)
            continue
        value = str(raw.get("value") or "").strip()
        negative = value.startswith("-")
        value = value.lstrip("-+") or "P0D"
        raw_type = raw.get("type")
        raw_type = (raw_type.get("decode") if isinstance(raw_type, dict) else raw_type) or ""
        type_term = cdisc_lookup("C201264", raw_type)
        if not type_term:
            zero = re.fullmatch(r"P(T)?0+[A-Z]", value) is not None
            type_term = cdisc_lookup("C201264", "Fixed Reference" if zero else ("Before" if negative else "After"))
        anchor_text = raw.get("relativeToFrom")
        anchor_text = anchor_text.get("decode") if isinstance(anchor_text, dict) else anchor_text
        relative_to_from = cdisc_lookup("C201265", anchor_text) or cdisc_lookup("C201265", "Start to Start")
        timing = {
            "id": raw.get("id") or str(uuid.uuid4()),
            "name": name,
            "type": {"id": str(uuid.uuid4()), **to_code(type_term, "C201264"), "instanceType": "Code"},
            "value": value,
            "valueLabel": raw.get("valueLabel") or value,
            "relativeToFrom": {"id": str(uuid.uuid4()), **to_code(relative_to_from, "C201265"), "instanceType": "Code"},
            "relativeFromScheduledInstanceId": source["id"],
            "instanceType": "Timing",
        }
        others = [i for i in instances if i is not source]
        anchor = (_instance_by_visit(raw.get("relativeToVisitName"), others)
                  or _best_instance(raw.get("relativeToVisitName") or "", others, epoch_names)
                  or _best_instance(anchor_text or "", others, epoch_names))
        if anchor is not None:
            timing["relativeToScheduledInstanceId"] = anchor["id"]
        for key in ("description", "label", "windowLower", "windowUpper", "windowLabel"):
            if raw.get(key):
                timing[key] = raw[key]
        timings.append(timing)

    timeline["timings"] = timings
    if dropped:
        logger.info(f"{len(dropped)} timing(s) not anchored to a scheduled instance, dropped: {dropped}")
    logger.info(f"Linked {len(timings)} timing(s) to the main timeline")


def _prune_unreferenced_biomedical_concepts(version: Dict[str, Any]) -> None:
    """Drop BiomedicalConcepts no Activity uses, and categories left empty.

    A BC is used when an Activity lists it in biomedicalConceptIds or lists
    a category it belongs to in bcCategoryIds. An unused BC (e.g. an extra
    "Urine Drug Screen Safety" variant of "Urine Drug Screen") triggers no
    data collection and only confuses consumers. Nothing is pruned when no
    Activity references any BC, since that means linking failed outright.
    """
    activities = [a for d in version.get("studyDesigns", []) for a in d.get("activities", [])]
    categories = version.get("bcCategories", [])
    used = {bid for a in activities for bid in a.get("biomedicalConceptIds") or []}
    if not used:
        return
    used_cats = {cid for a in activities for cid in a.get("bcCategoryIds") or []}
    for cat in categories:
        if cat.get("id") in used_cats:
            used.update(cat.get("memberIds") or [])
    bcs = version.get("biomedicalConcepts", [])

    # Link an unused BC to the activity it was evidently made for: every word
    # of the BC name (or a synonym) appears in the activity name ("FSH" ->
    # "FSH (Female patients only)"); the most specific BC wins per activity.
    def _words(text: str) -> set:
        return set(re.findall(r"[a-z0-9]+", (text or "").lower()))

    for activity in activities:
        act_words = _words(activity.get("name", ""))
        candidates = []
        for bc in bcs:
            if bc.get("id") in used:
                continue
            for label in [bc.get("name", "")] + list(bc.get("synonyms") or []):
                if _words(label) and _words(label) <= act_words:
                    candidates.append((len(_words(label)), bc))
                    break
        if candidates:
            top = max(c[0] for c in candidates)
            best = [bc for n, bc in candidates if n == top]
            if len(best) == 1:
                activity.setdefault("biomedicalConceptIds", []).append(best[0]["id"])
                used.add(best[0]["id"])

    dropped = [bc.get("name") for bc in bcs if bc.get("id") not in used]
    if not dropped:
        return
    version["biomedicalConcepts"] = [bc for bc in bcs if bc.get("id") in used]
    for cat in categories:
        if cat.get("memberIds"):
            cat["memberIds"] = [m for m in cat["memberIds"] if m in used]
    version["bcCategories"] = [
        c for c in categories if c.get("memberIds") or c.get("childIds") or c.get("id") in used_cats
    ]
    logger.info(f"Dropped {len(dropped)} BiomedicalConcept(s) not used by any activity: {dropped}")


def _remap_study_cells(design: Dict[str, Any], epochs: List[Dict[str, Any]]) -> None:
    """Point StudyCells at the real epochs while keeping their elements.

    The study-design extraction builds one cell per arm x epoch referencing
    arm-specific elements ("Sequence A: LY900018 -> IMG - Period 1"), but with
    provisional epoch ids ("epoch_1") while the USDM epochs come from the SoA
    with other ids. Each cell is remapped to the epoch named at the end of
    its element name ("... - Period 1" -> epoch "Period 1"), else to the
    epoch at the same position as its provisional epoch id; its elementIds
    are kept. Generic per-epoch elements are created only for arm x epoch
    combinations no cell covers, and elements referenced by no cell are
    removed (DDF00126/DDF00243).
    """
    epoch_ids = [ep["id"] for ep in epochs]
    valid_epochs = set(epoch_ids)
    norm_epoch = {ep["id"]: _normalize_epoch_name(ep.get("name", "")) for ep in epochs}
    elements = {e.get("id"): e for e in design.get("elements", [])}
    cells = design.get("studyCells", [])

    # Provisional epoch ids in first-appearance order ("epoch_1", "epoch_2", ...)
    def _order_key(eid: str):
        m = re.search(r"(\d+)$", eid or "")
        return (0, int(m.group(1))) if m else (1, eid or "")
    provisional = sorted({c.get("epochId") for c in cells if c.get("epochId") not in valid_epochs},
                         key=_order_key)
    by_position = {old: epoch_ids[i] for i, old in enumerate(provisional) if i < len(epoch_ids)}

    def _epoch_from_elements(cell: Dict[str, Any]) -> Optional[str]:
        """Epoch named by the element's phase (text after the last " - "):
        the phase contains the epoch name ("Period 1 Treatment" -> "Period 1")
        or the epoch name contains the phase ("TE ADA" vs footnoted "TE ADAa")."""
        for eid in cell.get("elementIds") or []:
            full = elements.get(eid, {}).get("name", "")
            # Spaces/punctuation ignored: "Washout" == "Wash out"
            phase = re.sub(r"[^a-z0-9]", "", _normalize_epoch_name(full.rsplit(" - ", 1)[-1]))
            # Longest epoch name first so "follow up for te ada" beats "follow up"
            for ep_id in sorted(norm_epoch, key=lambda k: -len(norm_epoch[k])):
                ep_name = re.sub(r"[^a-z0-9]", "", norm_epoch[ep_id])
                if ep_name and phase and (ep_name in phase or phase in ep_name):
                    return ep_id
        return None

    for cell in cells:
        if cell.get("epochId") not in valid_epochs:
            target = _epoch_from_elements(cell) or by_position.get(cell.get("epochId"))
            if target:
                cell["epochId"] = target
        cell["elementIds"] = [e for e in cell.get("elementIds") or [] if e in elements]
    cells = [c for c in cells if c.get("epochId") in valid_epochs]

    # Several design phases can fall in one SoA epoch ("Dose Escalation" and
    # "Maintenance" in "Treatment"): one cell per arm x epoch holds their
    # elements in order
    merged: Dict[tuple, Dict[str, Any]] = {}
    for cell in cells:
        key = (cell.get("armId"), cell.get("epochId"))
        if key in merged:
            merged[key]["elementIds"] += [e for e in cell["elementIds"] if e not in merged[key]["elementIds"]]
        else:
            merged[key] = cell
    cells = list(merged.values())

    # One cell per arm x epoch; fill gaps (and empty cells) with a generic
    # per-epoch element, created only when needed
    generic: Dict[str, str] = {}

    def _generic_element(ep_id: str) -> str:
        if ep_id not in generic:
            name = next((ep.get("name", "Element") for ep in epochs if ep["id"] == ep_id), "Element")
            existing = next((e for e in elements.values() if e.get("name") == name), None)
            if existing:
                generic[ep_id] = existing["id"]
            else:
                elem_id = str(uuid.uuid4()).replace("-", "_")
                elements[elem_id] = {"id": elem_id, "name": name, "instanceType": "StudyElement"}
                generic[ep_id] = elem_id
        return generic[ep_id]

    covered = {(c.get("armId"), c.get("epochId")) for c in cells}
    for arm in design.get("arms", []):
        for ep_id in epoch_ids:
            if (arm.get("id"), ep_id) not in covered:
                cells.append({
                    "id": str(uuid.uuid4()).replace("-", "_"),
                    "armId": arm.get("id"),
                    "epochId": ep_id,
                    "elementIds": [],
                    "instanceType": "StudyCell",
                })
    for cell in cells:
        if not cell["elementIds"]:
            cell["elementIds"] = [_generic_element(cell["epochId"])]

    used = {e for c in cells for e in c["elementIds"]}
    design["studyCells"] = cells
    design["elements"] = [e for eid, e in elements.items() if eid in used]


def _set_version_rationale(usdm: Dict[str, Any]) -> None:
    """StudyVersion.rationale from the protocol: the latest amendment's stated
    rationale when the version is an amendment, else "Original protocol
    version" — replacing the generic "Protocol version" placeholder."""
    try:
        version = usdm["study"]["versions"][0]
    except (KeyError, IndexError):
        return
    if version.get("rationale") and version["rationale"] != "Protocol version":
        return
    summaries = [a.get("summary") for a in version.get("amendments", [])
                 if a.get("summary") and not re.fullmatch(r"Amendment \S+ to the protocol", a["summary"])]
    version["rationale"] = summaries[-1] if summaries else "Original protocol version"


def _post_normalize_cleanup(usdm: Dict[str, Any]) -> None:
    """
    Final cleanup pass after normalize_usdm_data().

    Removes non-USDM-4.0 fields that may be re-introduced by normalize_usdm_data()
    or other post-processing, and wraps fields that must be AliasCode.
    """
    try:
        study = usdm.get("study", {})
        version = study.get("versions", [{}])[0]
        design = version.get("studyDesigns", [{}])[0]
    except (KeyError, IndexError):
        return

    # Strip documentVersions from Study (extra property — DDF00125)
    # documentedBy is the correct USDM 4.0 field; documentVersions is legacy.
    study.pop("documentVersions", None)

    # Remove internal staging list (should already be consumed by
    # _link_document_versions during _generate; defensive cleanup only)
    study.pop("_pendingDocumentVersions", None)
    study.pop("_pendingMaskedRoles", None)
    study.pop("_pendingProductStrengths", None)
    study.pop("_pendingSubstances", None)
    study.pop("_pendingAdministrations", None)
    study.pop("_pendingInterventionAdmins", None)
    study.pop("_pendingTimings", None)
    study.pop("_pendingSections", None)
    study.pop("_amendmentInfo", None)
    study.pop("_pendingDocVersionDates", None)
    study.pop("_pendingTransitionRules", None)
    study.pop("_pendingConditions", None)

    # Strip 'type' from all StudyIdentifiers (not in USDM 4.0 — DDF00125)
    for sid in version.get("studyIdentifiers", []):
        sid.pop("type", None)
        sid.pop("identifierType", None)

    # Strip epochId from all Encounters (not in USDM 4.0 Encounter schema — DDF00125)
    for enc in design.get("encounters", []):
        enc.pop("epochId", None)

    # Remove internal encounter→epoch cache (used during timeline synthesis)
    design.pop("_encounterEpochMap", None)

    # Remove internal header footnotes stash (consumed by _build_soa_footnotes)
    design.pop("_headerFootnotes", None)

    # Remove internal header epoch stash (consumed by _normalize_codelists)
    design.pop("_headerEpochs", None)

    # Remove internal PDF path and SoA source pages stash (consumed by _build_soa_footnotes)
    design.pop("_pdfPath", None)
    design.pop("_soaSourcePages", None)

    # Strip null entryId from ScheduleTimelines (must be string or absent — DDF00082)
    for tl in design.get("scheduleTimelines", []):
        if tl.get("entryId") is None:
            tl.pop("entryId", None)

    # Strip 'procedures' from InterventionalStudyDesign (not a valid property — DDF00125)
    design.pop("procedures", None)

    # Strip criteria from StudyDesignPopulation if empty (DDF00125)
    pop = design.get("population", {})
    if isinstance(pop, dict) and "criteria" in pop and not pop["criteria"]:
        pop.pop("criteria", None)

    # Normalize all GovernanceDates: date→dateValue, fix codeSystem, add geographicScopes (DDF00125, DDF00142)
    cdisc_sys = "http://www.cdisc.org"
    cdisc_ver = "2024-09-27"
    def _fix_governance_dates(dates: list) -> None:
        for gd in dates:
            if not isinstance(gd, dict):
                continue
            # date → dateValue
            if "date" in gd and "dateValue" not in gd:
                gd["dateValue"] = gd.pop("date")
            # Normalize dateValue format: replace underscores with hyphens (2020_08_18 → 2020-08-18)
            dv = gd.get("dateValue", "")
            if isinstance(dv, str) and "_" in dv:
                gd["dateValue"] = dv.replace("_", "-")
            # add geographicScopes if absent (required — DDF00126)
            if "geographicScopes" not in gd:
                gd["geographicScopes"] = []
            # fix type.codeSystem
            gd_type = gd.get("type")
            if isinstance(gd_type, dict):
                gd_type["codeSystem"] = cdisc_sys
                gd_type["codeSystemVersion"] = cdisc_ver

    _fix_governance_dates(version.get("dateValues", []))
    for amend in version.get("amendments", []):
        _fix_governance_dates(amend.get("dateValues", []))
    for document in study.get("documentedBy", []):
        for doc_version in document.get("versions", []):
            _fix_governance_dates(doc_version.get("dateValues", []))

    # Fix administrableDoseForm: must be AliasCode not a hybrid Code+standardCode object (DDF00081)
    for ap in version.get("administrableProducts", []):
        adf = ap.get("administrableDoseForm")
        if isinstance(adf, dict) and adf.get("instanceType") != "AliasCode":
            # Build proper AliasCode - move top-level Code fields into standardCode
            sc = adf.get("standardCode") or {
                "id": str(uuid.uuid4()),
                "code": adf.get("code", ""),
                "codeSystem": adf.get("codeSystem", cdisc_sys),
                "codeSystemVersion": adf.get("codeSystemVersion", cdisc_ver),
                "decode": adf.get("decode", ""),
                "instanceType": "Code",
            }
            ap["administrableDoseForm"] = {
                "id": adf.get("id") or str(uuid.uuid4()),
                "instanceType": "AliasCode",
                "standardCode": sc,
                "standardCodeAliases": [],
            }

    # Ensure studyPhase is AliasCode with SDTM C66737 code (DDF00229 + DDF00125)
    _PHASE_CODE_MAP = {
        "phase1": ("PHASE 1", "Phase 1"),
        "phase 1": ("PHASE 1", "Phase 1"),
        "phase2": ("PHASE 2", "Phase 2"),
        "phase 2": ("PHASE 2", "Phase 2"),
        "phase3": ("PHASE 3", "Phase 3"),
        "phase 3": ("PHASE 3", "Phase 3"),
        "phase4": ("PHASE 4", "Phase 4"),
        "phase 4": ("PHASE 4", "Phase 4"),
        "phase1/2": ("PHASE 1/2", "Phase 1/2"),
        "phase 1/2": ("PHASE 1/2", "Phase 1/2"),
        "phase2/3": ("PHASE 2/3", "Phase 2/3"),
        "phase 2/3": ("PHASE 2/3", "Phase 2/3"),
        "phase1b/2": ("PHASE 1B/2", "Phase 1b/2"),
        "phase 1b": ("PHASE 1B", "Phase 1b"),
        "phase 2a": ("PHASE 2A", "Phase 2a"),
        "phase 2b": ("PHASE 2B", "Phase 2b"),
    }
    sp = design.get("studyPhase")
    if sp and isinstance(sp, dict):
        # Get or build the inner Code
        sc = sp.get("standardCode") if sp.get("instanceType") == "AliasCode" else sp
        if isinstance(sc, dict):
            raw_code = sc.get("code", sc.get("decode", "")).lower()
            phase_term = _study_phase_term(sc.get("decode") or "") or _study_phase_term(raw_code)
            mapped = _PHASE_CODE_MAP.get(raw_code)
            if phase_term:
                sc.update(to_code(phase_term, "C66737"))
            elif mapped:
                sc["code"] = mapped[0]
                sc["decode"] = mapped[1]
                sc["codeSystem"] = "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl"
                sc["codeSystemVersion"] = "24.09e"
            if not sc.get("instanceType"):
                sc["instanceType"] = "Code"
            if not sc.get("id"):
                sc["id"] = str(uuid.uuid4())
        if sp.get("instanceType") != "AliasCode":
            design["studyPhase"] = {
                "id": str(uuid.uuid4()),
                "standardCode": sc,
                "standardCodeAliases": [],
                "instanceType": "AliasCode",
            }


def _fix_duplicate_code_decodes(usdm: Dict[str, Any]) -> None:
    """
    Fix code/decode one-to-one relationship violations (DDF00035).

    When the same code value is used with different decode values within
    the same codeSystem+codeSystemVersion, CORE flags a violation.
    Fix by making the decode consistent (use the first one seen).
    """
    try:
        design = usdm["study"]["versions"][0]["studyDesigns"][0]
    except (KeyError, IndexError):
        return

    # Collect all code objects and track (codeSystem, codeSystemVersion, code) → decode
    # Pre-seed canonical decodes for known codes to enforce consistency
    code_registry: Dict[tuple, str] = {
        ("http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl", "24.09e", "C17998"): "Unknown",
    }

    def _fix_codes(obj: Any) -> None:
        if isinstance(obj, dict):
            if _is_code_object(obj):
                key = (obj.get("codeSystem", ""),
                       obj.get("codeSystemVersion", ""),
                       obj.get("code", ""))
                if key[2]:  # Only if code is non-empty
                    if key in code_registry:
                        # Enforce consistent decode
                        obj["decode"] = code_registry[key]
                    else:
                        code_registry[key] = obj.get("decode", "")
            for v in obj.values():
                _fix_codes(v)
        elif isinstance(obj, list):
            for item in obj:
                _fix_codes(item)

    # Walk entire USDM to catch BCs on version level (not just design)
    _fix_codes(usdm)


def _ensure_study_design_type(usdm: Dict[str, Any]) -> None:
    """
    Ensure the study design has the correct ``instanceType`` and required
    fields for USDM v4.0.

    USDM v4.0 uses ``InterventionalStudyDesign`` or
    ``ObservationalStudyDesign`` — there is no generic ``StudyDesign``.
    Missing ``instanceType`` prevents CORE from properly parsing the
    design and its child entities (objectives, endpoints, etc.).
    """
    try:
        design = usdm["study"]["versions"][0]["studyDesigns"][0]
    except (KeyError, IndexError):
        return

    # Default to interventional (most common for clinical trials)
    if not design.get("instanceType"):
        design["instanceType"] = "InterventionalStudyDesign"

    # ``studyType`` is required for CORE to check intervention references (DDF00101)
    if design["instanceType"] == "InterventionalStudyDesign" and not design.get("studyType"):
        design["studyType"] = {
            "id": str(uuid.uuid4()).replace("-", "_"),
            "code": "C98388",
            "codeSystem": "http://www.cdisc.org",
            "codeSystemVersion": "2024-09-27",
            "decode": "Interventional Study",
            "instanceType": "Code",
        }

    # ``model`` is required for InterventionalStudyDesign. Normally extracted
    # (studydesign prompt / crossover text fallback); when absent, a one-arm
    # study is Single Group, otherwise Parallel.
    if design["instanceType"] == "InterventionalStudyDesign" and not design.get("model"):
        default_model = "Single Group" if len(design.get("arms", [])) == 1 else "Parallel"
        design["model"] = _resolve_ct_code(default_model, "C99076")

    # ``rationale`` is required
    if not design.get("rationale"):
        design["rationale"] = "See protocol synopsis."

    # ``blindingSchema`` is required for InterventionalStudyDesign.
    # Extraction stores it as a simple Code-like dict; USDM v4.0 expects
    # an AliasCode with ``standardCode`` nested inside.
    blinding = design.get("blindingSchema")
    if design["instanceType"] == "InterventionalStudyDesign":
        if isinstance(blinding, dict) and "standardCode" not in blinding:
            # Simple code dict from extraction — wrap in AliasCode
            blinding_code = blinding.get("code", "")
            _BLINDING_MAP = {
                "Open Label": ("C49659", "Open Label Study"),
                "open": ("C49659", "Open Label Study"),
                "Single Blind": ("C15228", "Single Blind Study"),
                "single": ("C15228", "Single Blind Study"),
                "Double Blind": ("C15227", "Double Blind Study"),
                "double": ("C15227", "Double Blind Study"),
                "Triple Blind": ("C156593", "Triple Blind Study"),
                "triple": ("C156593", "Triple Blind Study"),
            }
            mapped = _BLINDING_MAP.get(blinding_code, ("C49659", "Open Label Study"))
            design["blindingSchema"] = {
                "id": str(uuid.uuid4()).replace("-", "_"),
                "instanceType": "AliasCode",
                "standardCode": {
                    "id": str(uuid.uuid4()).replace("-", "_"),
                    "code": mapped[0],
                    "codeSystem": "http://www.cdisc.org",
                    "codeSystemVersion": "2024-09-27",
                    "decode": mapped[1],
                    "instanceType": "Code",
                },
                "standardCodeAliases": [],
            }
        elif not blinding:
            # No blinding at all — default to Open Label
            design["blindingSchema"] = {
                "id": str(uuid.uuid4()).replace("-", "_"),
                "instanceType": "AliasCode",
                "standardCode": {
                    "id": str(uuid.uuid4()).replace("-", "_"),
                    "code": "C49659",
                    "codeSystem": "http://www.cdisc.org",
                    "codeSystemVersion": "2024-09-27",
                    "decode": "Open Label Study",
                    "instanceType": "Code",
                },
                "standardCodeAliases": [],
            }

    # ``name`` should not be empty
    if not design.get("name"):
        study_name = usdm.get("study", {}).get("name", "Study Design")
        design["name"] = study_name or "Study Design"

    # Move properties that don't belong on the design to the correct level
    version = usdm["study"]["versions"][0]

    # Ensure Study has required instanceType
    study = usdm.get("study", {})
    if not study.get("instanceType"):
        study["instanceType"] = "Study"

    # Ensure StudyVersion has required instanceType
    if not version.get("instanceType"):
        version["instanceType"] = "StudyVersion"

    # ``studyPhase`` belongs on the design, not on the version
    if "studyPhase" in version and version["studyPhase"]:
        if not design.get("studyPhase"):
            design["studyPhase"] = version["studyPhase"]
        version.pop("studyPhase", None)

    # ``studyInterventions`` belongs on StudyVersion, not StudyDesign.
    # Merge design interventions into version (don't overwrite if version
    # already has them from direct placement).
    if "studyInterventions" in design:
        design_interventions = design.pop("studyInterventions")
        existing = version.get("studyInterventions", [])
        existing_ids = {inv.get("id") for inv in existing}
        for inv in design_interventions:
            if inv.get("id") not in existing_ids:
                existing.append(inv)
        version["studyInterventions"] = existing

    # Populate studyInterventionIds on design as ref list to version interventions.
    design["studyInterventionIds"] = [
        inv.get("id") for inv in version.get("studyInterventions", [])
        if inv.get("id")
    ]

    # ``geographicScopes`` is not a StudyDesign property in v4.0
    # (only on GovernanceDate and StudyAmendment)
    design.pop("geographicScopes", None)

    # ``epochs`` must have at least one entry (DDF00126).
    # If empty, synthesize epochs from study cell references.
    if not design.get("epochs"):
        epoch_ids = []
        for cell in design.get("studyCells", []):
            eid = cell.get("epochId") or cell.get("epoch")
            if isinstance(eid, str) and eid not in epoch_ids:
                epoch_ids.append(eid)
        if epoch_ids:
            design["epochs"] = [
                {
                    "id": eid,
                    "name": f"Epoch {i + 1}",
                    "type": {
                        "id": str(uuid.uuid4()),
                        "code": "C99079",
                        "codeSystem": "http://www.cdisc.org",
                        "codeSystemVersion": "2024-09-27",
                        "decode": "Treatment Epoch",
                        "instanceType": "Code",
                    },
                    "instanceType": "StudyEpoch",
                }
                for i, eid in enumerate(epoch_ids)
            ]


def _ensure_primary_objective(usdm: Dict[str, Any]) -> None:
    """
    Ensure the study design has exactly one primary objective and link
    endpoints to objectives via the ``endpoints`` array.

    CORE checks (JSONata-based):
    - DDF00084: Exactly one objective with level.code = C85826
    - DDF00041: ``objectives.endpoints[level.code="C94496"]`` count > 0
    - DDF00096: Each primary endpoint must be a child of a primary objective

    The CORE engine resolves ``objectives.endpoints`` by looking for an
    ``endpoints`` array nested inside each objective.
    """
    try:
        design = usdm["study"]["versions"][0]["studyDesigns"][0]
    except (KeyError, IndexError):
        return

    objectives = design.get("objectives", [])
    endpoints = design.get("endpoints", [])
    if not objectives or not endpoints:
        return

    # --- Build level-code lookup for endpoints ---
    # Map: level_code -> list of endpoints
    eps_by_level: Dict[str, list] = {}
    for ep in endpoints:
        lv = ep.get("level", {})
        code = lv.get("code", "") if isinstance(lv, dict) else ""
        eps_by_level.setdefault(code, []).append(ep)

    # --- Merge multiple primary objectives into one ---
    primary_objs = [o for o in objectives if isinstance(o.get("level"), dict) and o["level"].get("code") == "C85826"]
    if len(primary_objs) > 1:
        # Keep the first, merge names/text from others
        keeper = primary_objs[0]
        for extra in primary_objs[1:]:
            # Append extra's text to keeper
            extra_text = extra.get("text", "")
            if extra_text and extra_text not in keeper.get("text", ""):
                keeper["text"] = (keeper.get("text", "") + " " + extra_text).strip()
            # Append extra's name info
            extra_name = extra.get("name", "")
            if extra_name and extra_name not in keeper.get("name", ""):
                keeper["name"] = keeper["name"] + " / " + extra_name
            objectives.remove(extra)

    # --- Assign endpoints to objectives by matching level ---
    LEVEL_MAP = {
        "C85826": "C94496",    # Primary Objective -> Primary Endpoint
        "C85827": "C139173",   # Secondary Objective -> Secondary Endpoint
        "C163559": "C170559",  # Exploratory Objective -> Exploratory Endpoint
    }

    # Group objectives by level code
    objs_by_level: Dict[str, list] = {}
    for obj in objectives:
        obj_level = obj.get("level", {})
        obj_code = obj_level.get("code", "") if isinstance(obj_level, dict) else ""
        objs_by_level.setdefault(obj_code, []).append(obj)

    for obj_code, obj_group in objs_by_level.items():
        ep_code = LEVEL_MAP.get(obj_code, "")
        matching_eps = eps_by_level.get(ep_code, [])
        if not matching_eps:
            continue

        if len(obj_group) == 1:
            # Single objective gets all matching endpoints
            embedded = []
            for ep in matching_eps:
                ep_copy = dict(ep)
                ep_copy["id"] = str(uuid.uuid4())
                if ep_copy.get("level"):
                    lv_copy = dict(ep_copy["level"])
                    lv_copy["id"] = str(uuid.uuid4())
                    ep_copy["level"] = lv_copy
                embedded.append(ep_copy)
            obj_group[0]["endpoints"] = embedded
        else:
            # Multiple objectives: distribute endpoints round-robin
            # so each endpoint name appears exactly once
            for idx, ep in enumerate(matching_eps):
                target_obj = obj_group[idx % len(obj_group)]
                ep_copy = dict(ep)
                ep_copy["id"] = str(uuid.uuid4())
                if ep_copy.get("level"):
                    lv_copy = dict(ep_copy["level"])
                    lv_copy["id"] = str(uuid.uuid4())
                    ep_copy["level"] = lv_copy
                target_obj.setdefault("endpoints", []).append(ep_copy)

    # Remove top-level endpoints array after embedding into objectives
    # to avoid DDF00010 (duplicate names) and DDF00096 (orphaned endpoints).
    design.pop("endpoints", None)



def _fix_required_fields(usdm: Dict[str, Any]) -> None:
    """
    Ensure required USDM v4.0 fields are present on entities that may have
    been built from partial extraction data.

    Covers the most common validator errors:
      - BiomedicalConcept: reference, code
      - BiomedicalConceptProperty: isEnabled, code
      - AnalysisPopulation: text
      - studyPhase: must be AliasCode wrapping the Code object
    """
    version = usdm.get("study", {}).get("versions", [{}])[0]

    # ── BiomedicalConcepts ──────────────────────────────────────────────────
    # BC.code and BCProperty.code must be AliasCode (DDF00081 — 'AliasCode' was expected).
    def _to_alias_code(code_obj: Dict[str, Any]) -> Dict[str, Any]:
        """Wrap a plain Code dict in AliasCode if not already wrapped."""
        if not isinstance(code_obj, dict):
            return code_obj
        if code_obj.get("instanceType") == "AliasCode":
            return code_obj
        # It is a plain Code — wrap it
        if not code_obj.get("id"):
            code_obj["id"] = str(uuid.uuid4())
        if not code_obj.get("instanceType"):
            code_obj["instanceType"] = "Code"
        return {
            "id": str(uuid.uuid4()),
            "instanceType": "AliasCode",
            "standardCode": code_obj,
            "standardCodeAliases": [],
        }

    bc_name_to_id: Dict[str, str] = {}  # for BCCategory.memberIds wiring
    for bc in version.get("biomedicalConcepts", []):
        if not bc.get("reference"):
            bc["reference"] = bc.get("name", "unknown")
        bc_name_to_id[bc.get("name", "")] = bc.get("id", "")
        if not bc.get("code"):
            bc["code"] = _to_alias_code({
                "id": str(uuid.uuid4()),
                "code": "C17998",
                "codeSystem": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl",
                "codeSystemVersion": "24.09e",
                "decode": "Unknown",
                "instanceType": "Code",
            })
        else:
            bc["code"] = _to_alias_code(bc["code"])
        bc_name = bc.get("name", "")
        prop_names_seen: Dict[str, int] = {}
        for prop in bc.get("properties", []):
            if "isEnabled" not in prop:
                prop["isEnabled"] = True
            # Deduplicate property names: prefix with BC name (DDF00010)
            raw_name = prop.get("name", "Property")
            unique_name = f"{bc_name} - {raw_name}" if bc_name else raw_name
            if unique_name in prop_names_seen:
                prop_names_seen[unique_name] += 1
                prop["name"] = f"{unique_name} ({prop_names_seen[unique_name]})"
            else:
                prop_names_seen[unique_name] = 1
                prop["name"] = unique_name
            if not prop.get("code"):
                prop["code"] = _to_alias_code({
                    "id": str(uuid.uuid4()),
                    "code": "C17998",
                    "codeSystem": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl",
                    "codeSystemVersion": "24.09e",
                    "decode": "Unknown",  # canonical NCI decode for C17998 (DDF00035)
                    "instanceType": "Code",
                })
            else:
                prop["code"] = _to_alias_code(prop["code"])

    # ── BCCategory: wire memberIds from bcName lookup (DDF00014) ────────────
    for cat in version.get("bcCategories", []):
        if not cat.get("memberIds") and not cat.get("childIds"):
            # Try to match BCs whose name contains the category name
            cat_name = cat.get("name", "").lower()
            matched_ids = [
                bid for bname, bid in bc_name_to_id.items()
                if cat_name and (cat_name in bname.lower() or bname.lower() in cat_name)
            ]
            # No fallback to "all BCs": a category without identified members
            # is left empty (memberIds is 0..*) rather than claiming every BC
            if matched_ids:
                cat["memberIds"] = matched_ids
    _prune_unreferenced_biomedical_concepts(version)

    # ── AnalysisPopulations ─────────────────────────────────────────────────
    designs = version.get("studyDesigns", [])
    for design in designs:
        for pop in design.get("analysisPopulations", []):
            if not pop.get("text"):
                pop["text"] = pop.get("description") or pop.get("name") or "Study population"

        # ── studyPhase: must be AliasCode, not a bare Code ──────────────────
        sp = design.get("studyPhase")
        if sp and isinstance(sp, dict):
            inst = sp.get("instanceType", "")
            # Wrap if plain Code OR a code-like dict missing instanceType
            if inst in ("Code", "") and sp.get("code") and sp.get("instanceType") != "AliasCode":
                if not sp.get("instanceType"):
                    sp["instanceType"] = "Code"
                if not sp.get("id"):
                    sp["id"] = str(uuid.uuid4())
                design["studyPhase"] = {
                    "id": str(uuid.uuid4()),
                    "standardCode": sp,
                    "standardCodeAliases": [],
                    "instanceType": "AliasCode",
                }
            elif sp.get("instanceType") == "AliasCode" and not sp.get("standardCode"):
                # AliasCode missing standardCode — build a default
                sp["standardCode"] = {
                    "id": str(uuid.uuid4()),
                    "code": "C48660",
                    "codeSystem": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl",
                    "codeSystemVersion": "24.09e",
                    "decode": "Not Applicable",
                    "instanceType": "Code",
                }


def _validate_usdm_structure(usdm: Dict[str, Any]) -> List[USDMValidationIssue]:
    """Basic structural validation of the generated USDM."""
    issues = []

    study = usdm.get("study", {})
    if not study.get("name"):
        issues.append(USDMValidationIssue("warning", "study.name", "Study name is empty"))

    versions = study.get("versions", [])
    if not versions:
        issues.append(USDMValidationIssue("error", "study.versions", "No study versions"))
        return issues

    version = versions[0]
    if not version.get("studyIdentifiers"):
        issues.append(USDMValidationIssue("warning", "study.versions[0].studyIdentifiers",
                                           "No study identifiers"))

    designs = version.get("studyDesigns", [])
    if not designs:
        issues.append(USDMValidationIssue("error", "study.versions[0].studyDesigns",
                                           "No study designs"))
        return issues

    design = designs[0]
    if not design.get("arms"):
        issues.append(USDMValidationIssue("warning", "studyDesigns[0].arms", "No study arms"))
    if not design.get("epochs"):
        issues.append(USDMValidationIssue("warning", "studyDesigns[0].epochs", "No study epochs"))
    if not design.get("objectives"):
        issues.append(USDMValidationIssue("warning", "studyDesigns[0].objectives", "No objectives"))

    return issues


class USDMGeneratorAgent(BaseAgent):
    """
    Agent that generates USDM v4.0 JSON from Context Store entities.

    Queries the Context Store for all extracted entities, places them
    into the correct USDM hierarchy, validates the structure, and
    writes the final JSON output.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id="usdm-generator", config=config or {})
        self._indent = (config or {}).get("json_indent", 2)

    def initialize(self) -> None:
        self.set_state(AgentState.READY)
        self._logger.info(f"[{self.agent_id}] Initialized")

    def terminate(self) -> None:
        self.set_state(AgentState.TERMINATED)

    def get_capabilities(self) -> AgentCapabilities:
        return AgentCapabilities(
            agent_type="support",
            input_types=["context_store"],
            output_types=["usdm_json"],
        )

    def execute(self, task: AgentTask) -> AgentResult:
        """
        Generate USDM v4.0 JSON from Context Store.

        Input data:
        - output_path (str, optional): Path to write the JSON file
        - include_types (list[str], optional): Only include these entity types
        - exclude_types (list[str], optional): Exclude these entity types
        """
        if not self._context_store:
            return AgentResult(
                task_id=task.task_id, agent_id=self.agent_id,
                success=False, error="No Context Store available",
            )

        try:
            result = self._generate(task)

            # Post-assembly step 1: type-inference normalization
            try:
                from core.usdm_types_generated import normalize_usdm_data
                result.usdm_json = normalize_usdm_data(result.usdm_json)
                self._logger.debug(f"[{self.agent_id}] Type normalization applied")
            except Exception as e:
                self._logger.debug(f"[{self.agent_id}] Normalization skipped: {e}")

            # Post-assembly step 1b: final schema cleanup (strip non-schema fields
            # that may have been re-added by normalize_usdm_data or other passes)
            try:
                _post_normalize_cleanup(result.usdm_json)
                self._logger.debug(f"[{self.agent_id}] Post-normalize cleanup applied")
            except Exception as e:
                self._logger.debug(f"[{self.agent_id}] Post-normalize cleanup skipped: {e}")

            # Post-assembly step 1c: every coded attribute must use a term
            # of its CDISC codelist (runs last so it sees final values)
            try:
                _conform_codes_to_codelists(result.usdm_json)
            except Exception as e:
                self._logger.warning(f"[{self.agent_id}] Codelist conformance skipped: {e}")

            # Post-assembly step 2: convert simple IDs to UUID format
            id_map: dict = {}
            output_path = task.input_data.get("output_path")
            output_dir = os.path.dirname(output_path) if output_path else task.input_data.get("output_dir")
            try:
                from core.validation import convert_ids_to_uuids
                result.usdm_json, id_map = convert_ids_to_uuids(result.usdm_json)
                self._logger.info(f"[{self.agent_id}] Converted {len(id_map)} IDs to UUIDs")
                if output_dir and id_map:
                    id_map_path = os.path.join(output_dir, "id_mapping.json")
                    os.makedirs(output_dir, exist_ok=True)
                    with open(id_map_path, "w", encoding="utf-8") as f:
                        json.dump(id_map, f, indent=2)
            except Exception as e:
                self._logger.debug(f"[{self.agent_id}] UUID conversion skipped: {e}")

            # Post-assembly step 3: USDM schema validation via validate_and_fix_schema
            schema_valid = None
            semantic_issues = 0
            try:
                from core.validation import validate_and_fix_schema
                fixed_data, schema_result, fixer_result, usdm_result, _ = validate_and_fix_schema(
                    result.usdm_json, output_dir or ".", use_llm=False, convert_to_uuids=False
                )
                result.usdm_json = fixed_data
                schema_errors = getattr(schema_result, "error_count", 0) if schema_result else 0
                semantic_issues = getattr(usdm_result, "error_count", 0) if usdm_result else 0
                schema_valid = schema_errors == 0 and semantic_issues == 0
                if schema_valid:
                    self._logger.info(f"[{self.agent_id}] USDM schema validation PASSED")
                else:
                    self._logger.warning(
                        f"[{self.agent_id}] USDM validation FAILED: "
                        f"{schema_errors} schema errors, {semantic_issues} semantic errors"
                    )
            except Exception as e:
                self._logger.debug(f"[{self.agent_id}] USDM validation skipped: {e}")

            # Write assembled (and normalized) USDM to file
            if output_path:
                os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(result.usdm_json, f, indent=self._indent, ensure_ascii=False)
                result.output_path = output_path

            return AgentResult(
                task_id=task.task_id, agent_id=self.agent_id,
                success=True,
                data={
                    "usdm": result.usdm_json,
                    "id_map_size": len(id_map),
                    "schema_valid": schema_valid,
                    "semantic_issues": semantic_issues,
                    **result.to_dict(),
                },
                confidence_score=1.0 if not result.validation_issues else 0.8,
                provenance={
                    "agent_id": self.agent_id,
                    "entity_count": result.entity_count,
                    "entity_types": result.entity_types_included,
                    "validation_issues": len(result.validation_issues),
                    "id_map_size": len(id_map),
                    "schema_valid": schema_valid,
                    "semantic_issues": semantic_issues,
                    "timestamp": datetime.now().isoformat(),
                },
            )
        except Exception as e:
            self._logger.error(f"[{self.agent_id}] USDM generation failed: {e}")
            return AgentResult(
                task_id=task.task_id, agent_id=self.agent_id,
                success=False, error=str(e),
            )

    def _generate(self, task: AgentTask) -> USDMGenerationResult:
        """Build the USDM JSON from Context Store entities."""
        include_types = set(task.input_data.get("include_types", []))
        exclude_types = set(task.input_data.get("exclude_types", []))

        usdm = _build_empty_usdm_skeleton()
        result = USDMGenerationResult(usdm_json=usdm)

        # Query all entities from Context Store
        all_entities = self._context_store.query_entities()
        types_seen = set()

        for entity in all_entities:
            etype = entity.entity_type

            # Skip internal/infrastructure types
            if etype in ("pdf_page", "checkpoint", "error_record"):
                continue

            # study_design: extract design-level properties (blindingSchema,
            # randomizationType, etc.) and apply them to the skeleton design.
            if etype == "study_design":
                try:
                    design = usdm["study"]["versions"][0]["studyDesigns"][0]
                    sd_data = dict(entity.data)
                    sd_data = _sanitize_entity_data(sd_data)

                    # Only place properties that exist in the USDM v4.0 schema
                    # for InterventionalStudyDesign.
                    if sd_data.get("blindingSchema") and not design.get("blindingSchema"):
                        design["blindingSchema"] = sd_data["blindingSchema"]
                    # Intervention model (C99076), e.g. Crossover — otherwise
                    # _ensure_study_design_type falls back to Parallel/Single Group
                    if isinstance(sd_data.get("model"), dict) and not design.get("model"):
                        design["model"] = sd_data["model"]
                    # Protocol's own "Overall Design" / "Scientific Rationale
                    # for Study Design" text (otherwise placeholders are used)
                    for key in ("description", "rationale"):
                        if isinstance(sd_data.get(key), str) and sd_data[key].strip() and not design.get(key):
                            design[key] = sd_data[key]

                    # maskedRoles (e.g. "Subject", "Investigator", "Outcome
                    # Assessor") don't live on StudyDesign in USDM 4.0 — they
                    # map to StudyRole.masking on matching StudyRole entries.
                    # study_role entities may not be placed yet (different
                    # wave), so stage the names and resolve them once all
                    # entities are placed, in _link_masking_to_roles().
                    masked_roles = sd_data.get("maskedRoles")
                    if masked_roles:
                        pending = usdm["study"].setdefault("_pendingMaskedRoles", [])
                        for name in masked_roles:
                            if name and name not in pending:
                                pending.append(name)

                    # trialIntentTypes → intentTypes (schema property name)
                    intent = sd_data.get("trialIntentTypes")
                    if intent and not design.get("intentTypes"):
                        # Map extraction intent types to CDISC codes
                        _INTENT_MAP = {
                            "Treatment": ("C49656", "Treatment Study"),
                            "Prevention": ("C49655", "Prevention Study"),
                            "Diagnostic": ("C15220", "Diagnostic Study"),
                            "Supportive Care": ("C15313", "Supportive Care Study"),
                            "Screening": ("C15417", "Screening Study"),
                            "Health Services Research": ("C15245", "Health Services Research Study"),
                            "Basic Science": ("C15188", "Basic Science Study"),
                        }
                        codes = []
                        for item in (intent if isinstance(intent, list) else [intent]):
                            if isinstance(item, dict):
                                raw_code = item.get("code", "")
                                mapped = _INTENT_MAP.get(raw_code)
                                if mapped:
                                    codes.append({
                                        "id": str(uuid.uuid4()).replace("-", "_"),
                                        "code": mapped[0],
                                        "codeSystem": "http://www.cdisc.org",
                                        "codeSystemVersion": "2024-09-27",
                                        "decode": mapped[1],
                                        "instanceType": "Code",
                                    })
                            elif isinstance(item, str):
                                mapped = _INTENT_MAP.get(item)
                                if mapped:
                                    codes.append({
                                        "id": str(uuid.uuid4()).replace("-", "_"),
                                        "code": mapped[0],
                                        "codeSystem": "http://www.cdisc.org",
                                        "codeSystemVersion": "2024-09-27",
                                        "decode": mapped[1],
                                        "instanceType": "Code",
                                    })
                        if codes:
                            design["intentTypes"] = codes

                    # therapeuticAreas — must be Code objects, not strings
                    ta = sd_data.get("therapeuticAreas")
                    if ta and not design.get("therapeuticAreas"):
                        codes = []
                        for item in (ta if isinstance(ta, list) else [ta]):
                            if isinstance(item, dict) and item.get("code"):
                                codes.append(_ensure_code_id(dict(item)))
                            elif isinstance(item, str):
                                codes.append({
                                    "id": str(uuid.uuid4()).replace("-", "_"),
                                    "code": item,
                                    "codeSystem": "http://www.cdisc.org",
                                    "codeSystemVersion": "2024-09-27",
                                    "decode": item,
                                    "instanceType": "Code",
                                })
                        if codes:
                            design["therapeuticAreas"] = codes

                    # Use extracted name/instanceType if present
                    if sd_data.get("name") and not design.get("name"):
                        design["name"] = sd_data["name"]
                    if sd_data.get("instanceType"):
                        design["instanceType"] = sd_data["instanceType"]
                except (KeyError, IndexError):
                    pass
                types_seen.add(etype)
                continue

            # header_structure: stash footnote text and epoch data for later use
            if etype == "header_structure":
                try:
                    hs_data = entity.data or {}
                    structure = hs_data.get("structure", {})
                    design = usdm["study"]["versions"][0]["studyDesigns"][0]
                    footnotes = structure.get("footnotes", [])
                    if footnotes:
                        design["_headerFootnotes"] = footnotes
                    # Stash SoA source pages and PDF path so _build_soa_footnotes
                    # can fall back to PDF text extraction for missing footnote text.
                    soa_pages = hs_data.get("page_numbers", [])
                    if soa_pages:
                        design["_soaSourcePages"] = soa_pages
                    pdf_path = task.input_data.get("pdf_path", "")
                    if pdf_path:
                        design["_pdfPath"] = pdf_path
                    # Stash header epoch data so _normalize_codelists can resolve
                    # stale epoch IDs (e.g. "epoch_1") to USDM epoch entity IDs.
                    col_hierarchy = structure.get("columnHierarchy", {})
                    hdr_epochs = col_hierarchy.get("epochs", [])
                    if hdr_epochs:
                        design["_headerEpochs"] = hdr_epochs
                except (KeyError, IndexError):
                    pass
                continue

            # Apply include/exclude filters
            if include_types and etype not in include_types:
                continue
            if exclude_types and etype in exclude_types:
                continue

            # Build entity data dict with id
            entity_data = dict(entity.data)
            if "id" not in entity_data:
                entity_data["id"] = entity.id

            # StudyAmendment.newVersion/previousVersion (the document versions an
            # amendment links) are not USDM attributes and are stripped on
            # placement; they identify the current and the original document version
            if etype in ("study_amendment", "amendment"):
                usdm["study"].setdefault("_amendmentInfo", []).append({
                    "number": entity_data.get("number"),
                    "newVersion": entity_data.get("newVersion"),
                    "previousVersion": entity_data.get("previousVersion"),
                })

            # A date that belongs to a document version (not the study version)
            # is attached to that version after the documents are assembled
            if etype == "governance_date" and entity_data.get("documentVersionLabel"):
                usdm["study"].setdefault("_pendingDocVersionDates", []).append(entity_data)
                result.entity_count += 1
                types_seen.add(etype)
                continue

            # Transition rules and conditions have no list container: staged
            # with their raw links, and attached to elements/encounters and
            # StudyVersion.conditions after the design is assembled
            if etype in ("transition_rule", "condition"):
                key = "_pendingTransitionRules" if etype == "transition_rule" else "_pendingConditions"
                usdm["study"].setdefault(key, []).append(entity_data)
                result.entity_count += 1
                types_seen.add(etype)
                continue

            # Section structure (number, title, parent/child links) isn't part
            # of NarrativeContentItem and is stripped on placement — keep it to
            # build the NarrativeContent hierarchy in _build_document_contents()
            if etype in ("narrative_content", "narrative_content_item"):
                usdm["study"].setdefault("_pendingSections", []).append({
                    "id": entity_data.get("id"),
                    "name": entity_data.get("name"),
                    "sectionNumber": entity_data.get("sectionNumber"),
                    "sectionTitle": entity_data.get("sectionTitle"),
                    "childIds": list(entity_data.get("childIds") or []),
                    "order": entity_data.get("order", 0),
                    "topLevel": etype == "narrative_content",
                })

            # Capture encounter→epochId mapping BEFORE epochId gets stripped.
            # Timeline synthesis (_ensure_sponsor_identifier) needs this mapping
            # but runs before _normalize_codelists where it was previously built.
            if etype == "encounter" and entity_data.get("epochId"):
                try:
                    enc_epoch_stash = usdm["study"]["versions"][0]["studyDesigns"][0].setdefault("_encounterEpochMap", {})
                    enc_epoch_stash[entity_data["id"]] = entity_data["epochId"]
                except (KeyError, IndexError):
                    pass

            # Strip internal/debug properties not in USDM schema
            entity_data = _sanitize_entity_data(entity_data)

            # StudyIntervention.administrationIds is not a USDM attribute and is
            # stripped below — record it first so administrations can be
            # nested under the right intervention after placement
            if etype in ("study_intervention", "intervention") and entity_data.get("administrationIds"):
                usdm["study"].setdefault("_pendingInterventionAdmins", {})[entity_data.get("id")] = \
                    list(entity_data.get("administrationIds") or [])

            # Strip entity-specific extra properties not in USDM v4.0
            extras = _ENTITY_EXTRA_PROPERTIES.get(etype)
            if extras:
                for prop in extras:
                    entity_data.pop(prop, None)

            # StudyArm: ensure required dataOriginDescription and dataOriginType
            if etype == "study_arm":
                if "dataOriginDescription" not in entity_data:
                    entity_data["dataOriginDescription"] = "Collected during study conduct"
                if "dataOriginType" not in entity_data:
                    entity_data["dataOriginType"] = {
                        "id": str(uuid.uuid4()).replace("-", "_"),
                        "code": "C188866",
                        "codeSystem": "http://www.cdisc.org",
                        "codeSystemVersion": "2024-09-27",
                        "decode": "Data Generated Within Study",
                        "instanceType": "Code",
                    }

            # Epoch: extraction uses instanceType "Epoch" but USDM v4.0
            # expects "StudyEpoch" and requires a ``type`` Code object.
            if etype == "epoch":
                if entity_data.get("instanceType") == "Epoch":
                    entity_data["instanceType"] = "StudyEpoch"
                if not isinstance(entity_data.get("type"), dict):
                    # Infer epoch type from name (like legacy code)
                    epoch_name = entity_data.get("name", "").lower()
                    if "screen" in epoch_name:
                        ep_code, ep_decode = "C98779", "Screening Epoch"
                    elif "follow" in epoch_name or "post" in epoch_name:
                        ep_code, ep_decode = "C98781", "Follow-up Epoch"
                    elif "run-in" in epoch_name or "runin" in epoch_name or "washout" in epoch_name:
                        ep_code, ep_decode = "C98782", "Run-in Epoch"
                    else:
                        ep_code, ep_decode = "C99079", "Treatment Epoch"
                    entity_data["type"] = {
                        "id": str(uuid.uuid4()).replace("-", "_"),
                        "code": ep_code,
                        "codeSystem": "http://www.cdisc.org",
                        "codeSystemVersion": "2024-09-27",
                        "decode": ep_decode,
                        "instanceType": "Code",
                    }

            # Organization: ensure instanceType
            if etype == "organization":
                if not entity_data.get("instanceType"):
                    entity_data["instanceType"] = "Organization"

            # StudyRole: ensure instanceType and fix code
            if etype == "study_role":
                if not entity_data.get("instanceType"):
                    entity_data["instanceType"] = "StudyRole"

            # AdministrableProduct: strengthValue/strengthUnit/strengthName/
            # substanceIds are staging keys (see extraction/interventions/schema.py) —
            # pop them here and record a pending link, resolved once the
            # matching Substance entity is placed, in
            # _link_substances_to_products(). Only stage when there's a
            # real strength value and a substance to attach it to; never
            # fabricate either.
            if etype == "administrable_product":
                strength_value = entity_data.pop("strengthValue", None)
                strength_unit = entity_data.pop("strengthUnit", None)
                denominator_value = entity_data.pop("strengthDenominatorValue", None)
                denominator_unit = entity_data.pop("strengthDenominatorUnit", None)
                strength_name = entity_data.pop("strengthName", None)
                substance_ids = entity_data.pop("substanceIds", None) or []
                if strength_value is not None and substance_ids:
                    pending = usdm["study"].setdefault("_pendingProductStrengths", [])
                    pending.append({
                        "productId": entity_data.get("id"),
                        "substanceId": substance_ids[0],
                        "value": strength_value,
                        "unit": strength_unit,
                        "denominatorValue": denominator_value,
                        "denominatorUnit": denominator_unit,
                        "name": strength_name,
                    })

            # Administration entities (nested in USDM 4.0, not a list
            # container) are staged and linked by
            # _link_administrations_to_interventions() after placement.
            if etype == "administration":
                usdm["study"].setdefault("_pendingAdministrations", []).append(entity_data)
                result.entity_count += 1
                types_seen.add(etype)
                continue
            # Timings reference ScheduledActivityInstances that only exist once
            # the main timeline is built; staged for _link_timings_to_timeline()
            if etype == "timing":
                usdm["study"].setdefault("_pendingTimings", []).append(entity_data)
                result.entity_count += 1
                types_seen.add(etype)
                continue

            placed = _place_entity(usdm, etype, entity_data)
            if placed:
                result.entity_count += 1
                types_seen.add(etype)

        result.entity_types_included = sorted(types_seen)

        # Ensure study design has correct instanceType and required fields
        # (must run early — moves studyInterventions to version, adds studyType)
        _ensure_study_design_type(usdm)

        # Ensure sponsor identifier, role, timeline, and intervention refs
        _ensure_sponsor_identifier(usdm)

        # Derive businessTherapeuticAreas from indications if not already set
        _populate_therapeutic_areas(usdm)

        # Post-process: normalize codelist codes to CDISC-expected values
        # (must run after _ensure_study_design_type so interventions are on version)
        _normalize_codelists(usdm)

        # Fix activity names (repr strings → actual names) and link to procedures
        _fix_activity_names(usdm)
        _link_activities_to_procedures(usdm)

        # Fix duplicate IntercurrentEvent names across estimands
        _deduplicate_intercurrent_event_names(usdm)

        # Sanitize NarrativeContentItem text to valid XHTML
        _sanitize_narrative_xhtml(usdm)

        # Fix code/decode one-to-one relationship violations
        _fix_duplicate_code_decodes(usdm)

        # Ensure primary objective exists and links to primary endpoints
        _ensure_primary_objective(usdm)

        # Ensure study.documentedBy has a StudyDefinitionDocument, then
        # attach any staged document_version entities to it
        _ensure_study_definition_document(usdm)
        _link_document_versions(usdm)
        _link_change_sections_to_document(usdm)
        _build_document_contents(usdm)
        _attach_document_version_dates(usdm)
        _link_transition_rules(usdm)
        _link_conditions(usdm)

        # Attach staged maskedRoles (from study_design) to matching
        # StudyRole entries — must run after _ensure_sponsor_identifier
        # and _normalize_codelists so role names/codes are finalized.
        _link_masking_to_roles(usdm)

        # Build Ingredient/Substance/Strength.numerator from staged
        # administrable_product + substance entities — run after all
        # entities are placed since the two types may arrive in the same
        # extraction wave with no guaranteed order.
        _link_substances_to_products(usdm)

        # Nest staged Administration entities under their StudyIntervention
        # (dose, route, frequency, duration, administered product)
        _link_administrations_to_interventions(usdm)

        # Anchor extracted visit timings/windows to the main timeline's
        # scheduled instances (relative day offsets, visit windows)
        _link_timings_to_timeline(usdm)

        # StudyVersion.rationale: why this version exists
        _set_version_rationale(usdm)

        # Attach staged geographic_scope/country entities to real v4.0
        # locations (StudyAmendment/GovernanceDate.geographicScopes) — must
        # run before _fix_required_fields() so its geographicScopes
        # normalization/default logic sees real data when available.
        _link_geographic_scopes(usdm)

        _fix_required_fields(usdm)
        result.validation_issues = _validate_usdm_structure(usdm)
        return result
