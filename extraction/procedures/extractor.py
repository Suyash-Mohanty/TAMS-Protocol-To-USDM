"""
Procedures & Devices Extractor - Phase 10 of USDM Expansion

Extracts clinical procedures, medical devices, and drug ingredients from protocol.
"""

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any

from core.llm_client import call_llm
from core.pdf_utils import extract_text_from_pages, get_page_count
from ..citations import unwrap as _unwrap, collect_citation as _collect_citation
from .schema import (
    ProceduresDevicesData,
    ProceduresDevicesResult,
    Procedure,
    MedicalDevice,
    MedicalDeviceIdentifier,
    Ingredient,
    Strength,
    BiospecimenRetention,
    ProcedureType,
    DeviceType,
)
from .prompts import get_procedures_prompt, get_system_prompt

logger = logging.getLogger(__name__)


def find_procedure_pages(
    pdf_path: str,
    max_pages_to_scan: int = 60,
) -> List[int]:
    """
    Find pages containing procedure and device information using heuristics.
    """
    import fitz
    
    procedure_keywords = [
        r'procedure',
        r'blood\s+draw',
        r'blood\s+sample',
        r'venipuncture',
        r'biopsy',
        r'imaging',
        r'x-ray',
        r'ct\s+scan',
        r'mri',
        r'ultrasound',
        r'ecg',
        r'electrocardiogram',
        r'echocardiogram',
        r'infusion',
        r'injection',
        r'administration\s+of',
        r'specimen\s+collection',
        r'sample\s+collection',
        r'physical\s+examination',
        r'vital\s+signs',
        r'medical\s+device',
        r'drug\s+delivery',
        r'autoinjector',
        r'prefilled\s+syringe',
        r'infusion\s+pump',
        r'inhaler',
        r'nebulizer',
        r'retain',
        r'future\s+research',
        r'residual\s+sample',
        r'genetic\s+testing',
        r'destroy.*specimen',
    ]
    
    pattern = re.compile('|'.join(procedure_keywords), re.IGNORECASE)
    
    procedure_pages = []
    
    try:
        doc = fitz.open(pdf_path)
        total_pages = min(len(doc), max_pages_to_scan)
        
        for page_num in range(total_pages):
            page = doc[page_num]
            text = page.get_text().lower()
            
            # Count keyword matches on this page
            matches = len(pattern.findall(text))
            if matches >= 2:  # Require at least 2 keyword matches
                procedure_pages.append(page_num)
                logger.debug(f"Found procedure keywords on page {page_num + 1} ({matches} matches)")
        
        doc.close()
        
        # Limit to most relevant pages
        if len(procedure_pages) > 15:
            procedure_pages = procedure_pages[:15]
        
        logger.info(f"Found {len(procedure_pages)} potential procedure pages")
        
    except Exception as e:
        logger.error(f"Error scanning PDF: {e}")
        procedure_pages = list(range(min(20, get_page_count(pdf_path))))
    
    return procedure_pages


def parse_procedure_type(type_str: str) -> Optional[ProcedureType]:
    """Parse procedure type string to enum."""
    if not type_str:
        return None
    type_map = {
        'diagnostic': ProcedureType.DIAGNOSTIC,
        'therapeutic': ProcedureType.THERAPEUTIC,
        'surgical': ProcedureType.SURGICAL,
        'sampling': ProcedureType.SAMPLING,
        'sample collection': ProcedureType.SAMPLING,
        'imaging': ProcedureType.IMAGING,
        'monitoring': ProcedureType.MONITORING,
        'assessment': ProcedureType.ASSESSMENT,
    }
    return type_map.get(type_str.lower())


def parse_device_type(type_str: str) -> Optional[DeviceType]:
    """Parse device type string to enum."""
    if not type_str:
        return None
    type_map = {
        'drug delivery device': DeviceType.DRUG_DELIVERY,
        'drug delivery': DeviceType.DRUG_DELIVERY,
        'diagnostic device': DeviceType.DIAGNOSTIC,
        'diagnostic': DeviceType.DIAGNOSTIC,
        'monitoring device': DeviceType.MONITORING,
        'monitoring': DeviceType.MONITORING,
        'implantable device': DeviceType.IMPLANTABLE,
        'implantable': DeviceType.IMPLANTABLE,
        'wearable device': DeviceType.WEARABLE,
        'wearable': DeviceType.WEARABLE,
        'imaging equipment': DeviceType.IMAGING,
        'imaging': DeviceType.IMAGING,
        'laboratory equipment': DeviceType.LABORATORY,
        'laboratory': DeviceType.LABORATORY,
    }
    return type_map.get(type_str.lower())


def extract_procedures_devices(
    pdf_path: str,
    model: str = "gemini-2.5-pro",
    output_dir: Optional[str] = None,
) -> ProceduresDevicesResult:
    """
    Extract procedures and devices from protocol PDF.
    """
    logger.info("Starting procedures/devices extraction...")
    
    # Find relevant pages
    pages = find_procedure_pages(pdf_path)
    if not pages:
        logger.warning("No procedure pages found, using first 20 pages")
        pages = list(range(min(20, get_page_count(pdf_path))))
    
    # Extract text from pages
    text = extract_text_from_pages(pdf_path, pages)
    if not text:
        return ProceduresDevicesResult(
            success=False,
            error="Failed to extract text from PDF",
            pages_used=pages,
            model_used=model,
        )
    
    # Build prompt and call LLM
    prompt = get_procedures_prompt(text)
    system_prompt = get_system_prompt()
    
    try:
        # Combine system prompt with user prompt
        full_prompt = f"{system_prompt}\n\n{prompt}"
        
        # Retry logic for empty or failed responses
        max_retries = 3
        response = ""
        last_error = None
        
        for attempt in range(max_retries):
            result = call_llm(
                prompt=full_prompt,
                model_name=model,
                json_mode=True,
                extractor_name="procedures",
                temperature=0.1,
            )
            response = result.get('response', '')
            
            if response and response.strip():
                break
            else:
                last_error = "Empty response from LLM"
                logger.warning(f"Attempt {attempt+1}/{max_retries}: Empty response, retrying...")
        
        if not response or not response.strip():
            logger.error(f"All {max_retries} attempts failed: {last_error}")
            return ProceduresDevicesResult(
                success=False,
                error=f"LLM returned empty response after {max_retries} attempts",
                pages_used=pages,
                model_used=model,
            )
        
        # Parse JSON from response
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = response
        
        raw_data = json.loads(json_str)
        
        # Handle case where LLM returns a list instead of a dict
        if isinstance(raw_data, list):
            # Try to find wrapped dict or convert list to expected structure
            if len(raw_data) == 1 and isinstance(raw_data[0], dict):
                raw_data = raw_data[0]
            else:
                # Assume list contains procedures directly
                raw_data = {'procedures': raw_data}
        
        # Parse procedures
        procedures = []
        citations: Dict[str, Dict[str, Dict[str, Any]]] = {}
        for p in raw_data.get('procedures', []):
            proc_id = p.get('id', f"proc_{len(procedures)+1}")
            name_raw = p.get('name', '')
            label_raw = p.get('label')
            description_raw = p.get('description')
            proc = Procedure(
                id=proc_id,
                name=_unwrap(name_raw, ''),
                label=_unwrap(label_raw),
                description=_unwrap(description_raw),
                procedure_type=parse_procedure_type(p.get('procedureType')),
                code=p.get('code'),
            )
            procedures.append(proc)
            _collect_citation(citations, proc_id, 'name', name_raw)
            _collect_citation(citations, proc_id, 'label', label_raw)
            _collect_citation(citations, proc_id, 'description', description_raw)

        # Parse medical devices
        devices = []
        for d in raw_data.get('medicalDevices', []):
            dev_id = d.get('id', f"dev_{len(devices)+1}")
            name_raw = d.get('name', '')
            label_raw = d.get('label')
            description_raw = d.get('description')
            manufacturer_raw = d.get('manufacturer')
            model_number_raw = d.get('modelNumber')
            device = MedicalDevice(
                id=dev_id,
                name=_unwrap(name_raw, ''),
                label=_unwrap(label_raw),
                description=_unwrap(description_raw),
                device_type=parse_device_type(d.get('deviceType')),
                manufacturer=_unwrap(manufacturer_raw),
                model_number=_unwrap(model_number_raw),
            )
            devices.append(device)
            _collect_citation(citations, dev_id, 'name', name_raw)
            _collect_citation(citations, dev_id, 'label', label_raw)
            _collect_citation(citations, dev_id, 'description', description_raw)
            _collect_citation(citations, dev_id, 'manufacturer', manufacturer_raw)
            _collect_citation(citations, dev_id, 'modelNumber', model_number_raw)

        # Parse device identifiers
        device_identifiers = []
        for di in raw_data.get('deviceIdentifiers', []):
            did_id = di.get('id', f"dev_id_{len(device_identifiers)+1}")
            text_raw = di.get('text', '')
            identifier = MedicalDeviceIdentifier(
                id=did_id,
                text=_unwrap(text_raw, ''),
                scope_id=di.get('scopeId'),
            )
            device_identifiers.append(identifier)
            _collect_citation(citations, did_id, 'text', text_raw)

        # Parse ingredients - use empty string for role if not extracted
        ingredients = []
        for i in raw_data.get('ingredients', []):
            ing_id = i.get('id', f"ing_{len(ingredients)+1}")
            name_raw = i.get('name', '')
            ing = Ingredient(
                id=ing_id,
                name=_unwrap(name_raw, ''),
                role=i.get('role') or '',  # Empty if not extracted, don't inject 'Active'
                substance_id=i.get('substanceId'),
            )
            ingredients.append(ing)
            _collect_citation(citations, ing_id, 'name', name_raw)

        # Parse strengths
        strengths = []
        for s in raw_data.get('strengths', []):
            str_id = s.get('id', f"str_{len(strengths)+1}")
            value_raw = s.get('value', 0)
            unit_raw = s.get('unit', '')
            num_val_raw = s.get('numeratorValue')
            num_unit_raw = s.get('numeratorUnit')
            den_val_raw = s.get('denominatorValue')
            den_unit_raw = s.get('denominatorUnit')
            strength = Strength(
                id=str_id,
                value=_unwrap(value_raw, 0),
                unit=_unwrap(unit_raw, ''),
                numerator_value=_unwrap(num_val_raw),
                numerator_unit=_unwrap(num_unit_raw),
                denominator_value=_unwrap(den_val_raw),
                denominator_unit=_unwrap(den_unit_raw),
            )
            strengths.append(strength)
            _collect_citation(citations, str_id, 'value', value_raw)
            _collect_citation(citations, str_id, 'unit', unit_raw)
            _collect_citation(citations, str_id, 'numeratorValue', num_val_raw)
            _collect_citation(citations, str_id, 'numeratorUnit', num_unit_raw)
            _collect_citation(citations, str_id, 'denominatorValue', den_val_raw)
            _collect_citation(citations, str_id, 'denominatorUnit', den_unit_raw)

        # Parse biospecimen retentions — isRetained has no safe default to
        # fabricate, so skip (log) entries missing it rather than guessing.
        biospecimen_retentions = []
        for b in raw_data.get('biospecimenRetentions', []):
            if not isinstance(b, dict) or 'isRetained' not in b or _unwrap(b.get('isRetained')) is None:
                logger.warning(
                    "Skipping biospecimenRetention entry with no isRetained value: %r", b,
                )
                continue
            bior_id = b.get('id', f"bior_{len(biospecimen_retentions)+1}")
            name_raw = b.get('name', 'Biospecimen Retention')
            is_retained_raw = b.get('isRetained')
            description_raw = b.get('description')
            includes_dna_raw = b.get('includesDNA')
            biospecimen_retentions.append(BiospecimenRetention(
                id=bior_id,
                name=_unwrap(name_raw, 'Biospecimen Retention'),
                is_retained=bool(_unwrap(is_retained_raw)),
                label=b.get('label'),
                description=_unwrap(description_raw),
                includes_dna=_unwrap(includes_dna_raw),
            ))
            _collect_citation(citations, bior_id, 'name', name_raw)
            _collect_citation(citations, bior_id, 'isRetained', is_retained_raw)
            _collect_citation(citations, bior_id, 'description', description_raw)
            _collect_citation(citations, bior_id, 'includesDNA', includes_dna_raw)

        data = ProceduresDevicesData(
            procedures=procedures,
            devices=devices,
            device_identifiers=device_identifiers,
            ingredients=ingredients,
            strengths=strengths,
            biospecimen_retentions=biospecimen_retentions,
            citations=citations,
        )
        
        # Calculate confidence
        confidence = 0.0
        if procedures or devices or ingredients:
            confidence = min(1.0, (len(procedures) + len(devices) + len(ingredients)) / 10)
        
        result = ProceduresDevicesResult(
            success=True,
            data=data,
            pages_used=pages,
            model_used=model,
            confidence=confidence,
        )
        
        # Save output if directory specified
        if output_dir:
            output_path = Path(output_dir) / "09_extraction_procedures_devices.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
            logger.info(f"Saved procedures/devices to {output_path}")
        
        logger.info(f"Extracted {len(procedures)} procedures, {len(devices)} devices, {len(ingredients)} ingredients, {len(biospecimen_retentions)} biospecimen retentions")
        
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response: {e}")
        return ProceduresDevicesResult(
            success=False,
            error=f"JSON parse error: {e}",
            pages_used=pages,
            model_used=model,
        )
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        return ProceduresDevicesResult(
            success=False,
            error=str(e),
            pages_used=pages,
            model_used=model,
        )
