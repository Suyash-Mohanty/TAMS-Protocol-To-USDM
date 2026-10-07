"""
Interventions & Products Extractor - Phase 5 of USDM Expansion

Extracts study interventions and products from protocol.
"""

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any

from core.llm_client import call_llm
from core.pdf_utils import extract_text_from_pages, get_page_count
from .schema import (
    InterventionsData,
    StudyIntervention,
    AdministrableProduct,
    Administration,
    MedicalDevice,
    Substance,
    RouteOfAdministration,
    DoseForm,
    InterventionRole,
)
from .prompts import build_interventions_extraction_prompt

logger = logging.getLogger(__name__)


@dataclass
class InterventionsExtractionResult:
    """Result of interventions extraction."""
    success: bool
    data: Optional[InterventionsData] = None
    raw_response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    pages_used: List[int] = field(default_factory=list)
    model_used: Optional[str] = None


def find_intervention_pages(
    pdf_path: str,
    max_pages_to_scan: int = 50,
) -> List[int]:
    """
    Find pages containing intervention/product information using heuristics.
    """
    import fitz
    
    intervention_keywords = [
        r'investigational\s+product',
        r'study\s+drug',
        r'study\s+treatment',
        r'study\s+intervention',
        r'study\s+medication',
        r'dose\s+and\s+administration',
        r'dosing\s+regimen',
        r'route\s+of\s+administration',
        r'formulation',
        r'pharmaceutical\s+form',
        r'active\s+ingredient',
        r'placebo',
        r'comparator',
    ]
    
    pattern = re.compile('|'.join(intervention_keywords), re.IGNORECASE)
    
    intervention_pages = []
    
    try:
        doc = fitz.open(pdf_path)
        total_pages = min(len(doc), max_pages_to_scan)
        
        for page_num in range(total_pages):
            page = doc[page_num]
            text = page.get_text().lower()
            
            if pattern.search(text):
                intervention_pages.append(page_num)
                logger.debug(f"Found intervention keywords on page {page_num + 1}")
        
        doc.close()
        
        # Include adjacent pages for context
        if intervention_pages:
            expanded = set()
            for p in intervention_pages:
                expanded.add(p)
                if p > 0:
                    expanded.add(p - 1)
                if p < total_pages - 1:
                    expanded.add(p + 1)
            intervention_pages = sorted(expanded)
        
        logger.info(f"Found {len(intervention_pages)} potential intervention pages")
        
    except Exception as e:
        logger.error(f"Error scanning PDF: {e}")
        
    return intervention_pages


def extract_interventions(
    pdf_path: str,
    model_name: str = "gemini-2.5-pro",
    pages: Optional[List[int]] = None,
    protocol_text: Optional[str] = None,
    existing_arms: Optional[List[Dict[str, Any]]] = None,
    study_indication: Optional[str] = None,
) -> InterventionsExtractionResult:
    """
    Extract interventions and products from a protocol PDF.
    
    Args:
        pdf_path: Path to protocol PDF
        model_name: LLM model to use
        pages: Specific pages to use
        protocol_text: Optional pre-extracted text
        existing_arms: Treatment arms from study design for reference
        study_indication: Indication from metadata for context
    """
    result = InterventionsExtractionResult(success=False, model_used=model_name)
    
    try:
        # Auto-detect intervention pages if not specified
        if pages is None:
            pages = find_intervention_pages(pdf_path)
            if not pages:
                logger.warning("No intervention pages detected, scanning first 30 pages")
                pages = list(range(min(30, get_page_count(pdf_path))))
        
        result.pages_used = pages
        
        # Extract text from pages
        if protocol_text is None:
            logger.info(f"Extracting text from pages {pages}...")
            protocol_text = extract_text_from_pages(pdf_path, pages)
        
        if not protocol_text:
            result.error = "Failed to extract text from PDF"
            return result
        
        # Call LLM for extraction
        logger.info("Extracting interventions with LLM...")
        
        # Build context hints from prior extractions
        context_hints = ""
        if existing_arms:
            arm_names = [a.get('name', '') for a in existing_arms if a.get('name')]
            if arm_names:
                context_hints += f"\nKnown treatment arms: {', '.join(arm_names)}"
        if study_indication:
            context_hints += f"\nStudy indication: {study_indication}"
        
        prompt = build_interventions_extraction_prompt(protocol_text, context_hints=context_hints)
        
        response = call_llm(
            prompt=prompt,
            model_name=model_name,
            json_mode=True,
            extractor_name="interventions",
        )
        
        if 'error' in response:
            result.error = response['error']
            return result
        
        # Parse response
        raw_response = _parse_json_response(response.get('response', ''))
        if not raw_response:
            result.error = "Failed to parse LLM response as JSON"
            return result
        
        result.raw_response = raw_response
        
        # Convert to structured data
        result.data = _parse_interventions_response(raw_response)
        result.success = result.data is not None
        
        if result.success:
            logger.info(
                f"Extracted {len(result.data.interventions)} interventions, "
                f"{len(result.data.products)} products, "
                f"{len(result.data.administrations)} administration regimens"
            )
        
    except Exception as e:
        logger.error(f"Interventions extraction failed: {e}")
        result.error = str(e)
        
    return result


def _parse_json_response(response_text: str) -> Optional[Dict[str, Any]]:
    """Parse JSON from LLM response, handling markdown code blocks."""
    if not response_text:
        return None
        
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
    if json_match:
        response_text = json_match.group(1)
    
    response_text = response_text.strip()
    
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse JSON response: {e}")
        return None


def _parse_interventions_response(raw: Dict[str, Any]) -> Optional[InterventionsData]:
    """Parse raw LLM response into InterventionsData object.
    
    Handles both legacy format and new USDM-compliant format with ids.
    """
    try:
        # Handle case where LLM returns a list instead of a dict
        if isinstance(raw, list):
            if len(raw) == 1 and isinstance(raw[0], dict):
                raw = raw[0]
            else:
                # Assume list contains interventions directly
                raw = {'interventions': raw}
        
        interventions = []
        products = []
        administrations = []
        substances = []
        devices = []
        
        # Process interventions - accept both 'interventions' and 'studyInterventions' keys
        int_list = raw.get('interventions', []) or raw.get('studyInterventions', [])
        for i, int_data in enumerate(int_list):
            if not isinstance(int_data, dict):
                continue
            
            role_str = int_data.get('role')
            role = _map_intervention_role(role_str) if role_str else None
            
            interventions.append(StudyIntervention(
                id=int_data.get('id', f"int_{i+1}"),
                name=int_data.get('name', f'Intervention {i+1}'),
                description=int_data.get('description'),
                role=role,
                intervention_type=int_data.get('type') or int_data.get('interventionType'),
            ))
        
        # Process products - accept both 'products' and 'administrableProducts' keys
        prod_list = raw.get('products', []) or raw.get('administrableProducts', [])
        for i, prod_data in enumerate(prod_list):
            if not isinstance(prod_data, dict):
                continue
            
            dose_form = _map_dose_form(prod_data.get('doseForm', ''))
            strength_value, strength_unit = _extract_strength(prod_data)
            denominator_value, denominator_unit = _extract_strength_denominator(prod_data)
            if denominator_value is not None and strength_unit and "/" in strength_unit:
                strength_unit = strength_unit.split("/")[0].strip()  # "mg/mL" -> "mg" over 1 mL
            strength_name = prod_data.get('strengthName') or prod_data.get('strength_name')

            products.append(AdministrableProduct(
                id=prod_data.get('id', f"prod_{i+1}"),
                name=prod_data.get('name', f'Product {i+1}'),
                description=prod_data.get('description'),
                dose_form=dose_form,
                dose_form_text=prod_data.get('doseForm'),
                designation=next((v for v in (prod_data.get('designation'), prod_data.get('productDesignation'))
                                  if isinstance(v, str) and v.strip()), None),
                active_ingredients=[n for n in (prod_data.get('activeIngredients') or []) if isinstance(n, str)],
                strength_value=strength_value,
                strength_unit=strength_unit,
                strength_denominator_value=denominator_value,
                strength_denominator_unit=denominator_unit,
                strength_name=strength_name,
                manufacturer=prod_data.get('manufacturer'),
            ))
        
        # Process administrations
        for i, admin_data in enumerate(raw.get('administrations', [])):
            if not isinstance(admin_data, dict):
                continue
            
            route = _map_route(admin_data.get('route', ''))
            
            administrations.append(Administration(
                id=admin_data.get('id', f"admin_{i+1}"),
                name=admin_data.get('name', f'Administration {i+1}'),
                dose=admin_data.get('dose'),
                dose_frequency=admin_data.get('frequency') or admin_data.get('doseFrequency'),
                route=route,
                route_text=admin_data.get('route'),
                duration=admin_data.get('duration'),
                description=admin_data.get('description'),
            ))
        
        # Process substances
        for i, sub_data in enumerate(raw.get('substances', [])):
            if not isinstance(sub_data, dict):
                continue
            
            substances.append(Substance(
                id=sub_data.get('id', f"sub_{i+1}"),
                name=sub_data.get('name', f'Substance {i+1}'),
                description=sub_data.get('description'),
            ))
        
        # Process devices - accept both 'devices' and 'medicalDevices' keys
        dev_list = raw.get('devices', []) or raw.get('medicalDevices', [])
        for i, dev_data in enumerate(dev_list):
            if not isinstance(dev_data, dict):
                continue
            
            devices.append(MedicalDevice(
                id=dev_data.get('id', f"dev_{i+1}"),
                name=dev_data.get('name', f'Device {i+1}'),
                description=dev_data.get('description'),
                manufacturer=dev_data.get('manufacturer'),
            ))
        
        # Link administrations and products to interventions by name — the
        # lists are independent (e.g. 2 interventions, 5 products, 6
        # administrations), so pairing by position mismatches them.
        for admin in administrations:
            owner = _best_intervention(admin.name, interventions)
            if owner is not None:
                owner.administration_ids.append(admin.id)
            product = _best_product(admin.name, admin.dose, products)
            if product is not None:
                admin.product_id = product.id
        for product in products:
            owner = _best_intervention(product.name, interventions)
            if owner is not None:
                owner.product_ids.append(product.id)
        
        # Link substances to products by name — one substance is typically
        # shared by several products (one per strength), so positional
        # pairing would leave every product after the first unlinked.
        for product in products:
            owner = _best_intervention(product.name, interventions)
            context = " ".join(filter(None, [product.description,
                                             owner.name if owner else None,
                                             owner.description if owner else None]))
            product.substance_ids.extend(
                _match_substances(product.name, substances, product.active_ingredients, context))
            if not product.designation:
                product.designation = _derive_designation(product.name, interventions)

        # Concomitant (permitted/prohibited) medications are not study
        # interventions — CDISC C207417 has no role for them — so they are
        # dropped, together with products that belong only to them.
        interventions, products = _drop_concomitant(interventions, products)
        
        return InterventionsData(
            interventions=interventions,
            products=products,
            administrations=administrations,
            substances=substances,
            devices=devices,
        )
        
    except Exception as e:
        logger.error(f"Failed to parse interventions response: {e}")
        return None


def _match_substances(product_name: str, substances: List[Substance],
                      active_ingredients: Optional[List[str]] = None,
                      context: str = "") -> List[str]:
    """Return ids of the substances a product contains.

    1. The ingredients the LLM listed for the product (`activeIngredients`).
    2. A substance whose name (or its name without a parenthetical code, e.g.
       "eloralintide" from "Eloralintide (LY3841136)") appears in the product
       name.
    3. The same in `context` — the product description and its intervention's
       name/description — for products named by code or brand ("LY900018",
       "GlucaGen") whose intervention says "intramuscular glucagon".
    4. With exactly one substance, every non-placebo product contains it.
    """
    def _variants(sub_name: str) -> set:
        sub_name = (sub_name or "").lower()
        variants = {sub_name, re.sub(r"\s*\([^)]*\)", "", sub_name).strip()}
        variants |= set(re.findall(r"\(([^)]+)\)", sub_name))  # e.g. "ly3841136"
        return {v for v in variants if v}

    def _find(text: str) -> List[str]:
        text = (text or "").lower()
        return [sub.id for sub in substances
                if any(re.search(rf"\b{re.escape(v)}\b", text) for v in _variants(sub.name))]

    if active_ingredients:
        listed = {v for name in active_ingredients if isinstance(name, str) for v in _variants(name)}
        matched = [sub.id for sub in substances if _variants(sub.name) & listed]
        if matched:
            return matched
    name = (product_name or "").lower()
    matched = _find(name) or _find(context)
    if not matched and len(substances) == 1 and "placebo" not in name:
        matched.append(substances[0].id)
    return matched


_IMP_ROLES = {InterventionRole.INVESTIGATIONAL, InterventionRole.COMPARATOR, InterventionRole.PLACEBO}


def _derive_designation(product_name: str, interventions: List[StudyIntervention]) -> str:
    """IMP/NIMP for a product from the role of the intervention it belongs to.

    Investigational, comparator and placebo products are IMPs (tested or used
    as a reference); everything else (challenge agent, rescue, background,
    concomitant) is an auxiliary NIMP. The intervention is the one sharing
    the most name words with the product; with no match the product is
    assumed to be an IMP, since protocols list study drugs as products.
    """
    best = _best_intervention(product_name, interventions)
    if best is None or best.role in _IMP_ROLES:
        return "IMP"
    return "NIMP"


def _best_intervention(product_name: str, interventions: List[StudyIntervention]) -> Optional[StudyIntervention]:
    """The intervention sharing the most name words with a product, if any.

    Ties go to the intervention whose name is most fully covered ("IV
    glucose rescue infusion" -> "IV glucose", not "Human regular insulin
    (IV infusion)").
    """
    product_words = set(re.findall(r"[a-z0-9]+", (product_name or "").lower()))
    best, best_score = None, (0, 0.0)
    for intervention in interventions:
        words = set(re.findall(r"[a-z0-9]+", (intervention.name or "").lower()))
        overlap = len(product_words & words)
        score = (overlap, overlap / len(words) if words else 0.0)
        if overlap and score > best_score:
            best, best_score = intervention, score
    return best


def _best_product(name: str, dose: Optional[str], products: List[AdministrableProduct]) -> Optional[AdministrableProduct]:
    """The product an administration gives.

    The dose actually given decides the strength ("Eloralintide 6 mg QW –
    escalation step 1" with dose "3 mg" gives the 3 mg product); among
    products of that strength (or all, when the dose isn't numeric) the one
    sharing the most name words wins.
    """
    words = set(re.findall(r"[a-z0-9]+", f"{name} {dose or ''}".lower()))
    dose_match = re.match(r"\s*(\d+(?:\.\d+)?)", dose or "")
    candidates = products
    if dose_match:
        amount = float(dose_match.group(1))
        same_strength = [
            p for p in products
            if (p.strength_value is not None and abs(p.strength_value - amount) < 1e-9)
            or f"{amount:g}" in re.findall(r"\d+(?:\.\d+)?", p.name or "")
        ]
        candidates = same_strength or [
            p for p in products if p.strength_value is None and not re.search(r"\d", p.name or "")
        ]
    best, best_score = None, 0
    for product in candidates:
        score = len(words & set(re.findall(r"[a-z0-9]+", (product.name or "").lower())))
        if score > best_score:
            best, best_score = product, score
    return best


def _drop_concomitant(interventions: List[StudyIntervention], products: List[AdministrableProduct]):
    """Remove concomitant-medication interventions and their products."""
    concomitant = [i for i in interventions if i.role == InterventionRole.CONCOMITANT]
    if not concomitant:
        return interventions, products
    kept_products = []
    for product in products:
        owner = _best_intervention(product.name, interventions)
        if owner is not None and owner.role == InterventionRole.CONCOMITANT:
            logger.info(f"Dropping product {product.name!r}: belongs to concomitant medication {owner.name!r}")
            continue
        kept_products.append(product)
    logger.info(f"Dropping {len(concomitant)} concomitant medication(s) from study interventions: "
                f"{[i.name for i in concomitant]}")
    return [i for i in interventions if i.role != InterventionRole.CONCOMITANT], kept_products


def _map_intervention_role(role_str: str) -> InterventionRole:
    """Map string to InterventionRole enum. Returns UNKNOWN if input is empty."""
    if not role_str:
        return InterventionRole.UNKNOWN
    role_lower = role_str.lower()
    if 'placebo' in role_lower:
        return InterventionRole.PLACEBO
    elif 'comparator' in role_lower or 'reference' in role_lower:
        return InterventionRole.COMPARATOR
    elif 'challenge' in role_lower or 'provocation' in role_lower or 'induc' in role_lower:
        return InterventionRole.CHALLENGE
    elif 'rescue' in role_lower:
        return InterventionRole.RESCUE
    elif 'concomitant' in role_lower or 'prohibited' in role_lower or 'permitted' in role_lower:
        return InterventionRole.CONCOMITANT
    elif 'background' in role_lower:
        return InterventionRole.BACKGROUND
    elif 'additional required' in role_lower or 'auxiliary' in role_lower:
        return InterventionRole.ADDITIONAL_REQUIRED
    elif 'diagnostic' in role_lower:
        return InterventionRole.DIAGNOSTIC
    elif ('investigational' in role_lower or 'experimental' in role_lower
          or 'study drug' in role_lower or 'study intervention' in role_lower):
        return InterventionRole.INVESTIGATIONAL
    return InterventionRole.UNKNOWN  # Return UNKNOWN for unrecognized


def _extract_strength(prod_data: Dict[str, Any]) -> tuple:
    """Get (value, unit) for a product's strength numerator.

    Prefers the structured strengthValue/strengthUnit fields; falls back to
    parsing the legacy composite "strength" string (e.g. "15 mg") for
    responses that don't follow the current prompt format.
    """
    value = prod_data.get('strengthValue')
    if value is not None:
        try:
            return float(value), (prod_data.get('strengthUnit') or None)
        except (TypeError, ValueError):
            pass

    raw = prod_data.get('strength')
    if isinstance(raw, str):
        match = re.match(r'^\s*([\d.]+)\s*([^/]*)', raw)
        if match:
            try:
                return float(match.group(1)), (match.group(2).strip() or None)
            except ValueError:
                pass

    return None, None


def _extract_strength_denominator(prod_data: Dict[str, Any]) -> tuple:
    """(value, unit) of a concentration's denominator ("1 mg/mL" -> (1.0, "mL")),
    from strengthDenominatorValue/Unit or the unit text after "/"."""
    value = prod_data.get('strengthDenominatorValue')
    unit = prod_data.get('strengthDenominatorUnit')
    if value is None and unit is None:
        unit_text = prod_data.get('strengthUnit') or prod_data.get('strength') or ''
        match = re.search(r'/\s*(\d+(?:\.\d+)?)?\s*(mL|ml|L|dL|g|mg|kg)\b', str(unit_text))
        if not match:
            return None, None
        value, unit = match.group(1) or 1, match.group(2)
    try:
        return (float(value) if value is not None else 1.0), unit
    except (TypeError, ValueError):
        return None, None


def _map_dose_form(form_str: str) -> Optional[DoseForm]:
    """Map string to DoseForm enum."""
    if not form_str:
        return None
    form_lower = form_str.lower()
    if 'tablet' in form_lower:
        return DoseForm.TABLET
    elif 'capsule' in form_lower:
        return DoseForm.CAPSULE
    elif 'solution' in form_lower:
        return DoseForm.SOLUTION
    elif 'suspension' in form_lower:
        return DoseForm.SUSPENSION
    elif 'injection' in form_lower:
        return DoseForm.INJECTION
    elif 'cream' in form_lower:
        return DoseForm.CREAM
    elif 'ointment' in form_lower:
        return DoseForm.OINTMENT
    elif 'gel' in form_lower:
        return DoseForm.GEL
    elif 'patch' in form_lower:
        return DoseForm.PATCH
    elif 'powder' in form_lower:
        return DoseForm.POWDER
    elif 'spray' in form_lower:
        return DoseForm.SPRAY
    elif 'inhaler' in form_lower:
        return DoseForm.INHALER
    return DoseForm.OTHER


def _map_route(route_str: str) -> Optional[RouteOfAdministration]:
    """Map string to RouteOfAdministration enum."""
    if not route_str:
        return None
    route_lower = route_str.lower()
    if 'oral' in route_lower:
        return RouteOfAdministration.ORAL
    elif 'intravenous' in route_lower or route_lower == 'iv':
        return RouteOfAdministration.INTRAVENOUS
    elif 'subcutaneous' in route_lower or route_lower == 'sc':
        return RouteOfAdministration.SUBCUTANEOUS
    elif 'intramuscular' in route_lower or route_lower == 'im':
        return RouteOfAdministration.INTRAMUSCULAR
    elif 'topical' in route_lower:
        return RouteOfAdministration.TOPICAL
    elif 'inhalation' in route_lower:
        return RouteOfAdministration.INHALATION
    elif 'intranasal' in route_lower:
        return RouteOfAdministration.INTRANASAL
    elif 'ophthalmic' in route_lower:
        return RouteOfAdministration.OPHTHALMIC
    elif 'transdermal' in route_lower:
        return RouteOfAdministration.TRANSDERMAL
    elif 'rectal' in route_lower:
        return RouteOfAdministration.RECTAL
    elif 'sublingual' in route_lower:
        return RouteOfAdministration.SUBLINGUAL
    return RouteOfAdministration.OTHER


def save_interventions_result(
    result: InterventionsExtractionResult,
    output_path: str,
) -> None:
    """Save interventions extraction result to JSON file."""
    output = {
        "success": result.success,
        "pagesUsed": result.pages_used,
        "modelUsed": result.model_used,
    }
    
    if result.data:
        output["interventions"] = result.data.to_dict()
    if result.error:
        output["error"] = result.error
    if result.raw_response:
        output["rawResponse"] = result.raw_response
        
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
        
    logger.info(f"Saved interventions to {output_path}")
