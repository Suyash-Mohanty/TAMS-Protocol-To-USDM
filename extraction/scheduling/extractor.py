"""
Scheduling Logic Extractor - Phase 11 of USDM Expansion

Extracts timing constraints, transition rules, and conditional logic from protocol.
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
    SchedulingData,
    SchedulingResult,
    Timing,
    Condition,
    ConditionAssignment,
    TransitionRule,
    ScheduleTimelineExit,
    ScheduledDecisionInstance,
    TimingType,
    TimingRelativeToFrom,
    TransitionType,
)
from .prompts import get_scheduling_prompt, get_system_prompt

logger = logging.getLogger(__name__)


def find_scheduling_pages(
    pdf_path: str,
    max_pages_to_scan: int = 60,
) -> List[int]:
    """
    Find pages containing scheduling/timing information using heuristics.
    """
    import fitz
    
    scheduling_keywords = [
        r'visit\s+window',
        r'visit\s+schedule',
        r'study\s+schedule',
        r'study\s+duration',
        r'±\s*\d+\s*days?',
        r'\+/-\s*\d+\s*days?',
        r'within\s+\d+\s*days?',
        r'screening\s+period',
        r'treatment\s+period',
        r'follow-up\s+period',
        r'washout',
        r'discontinuation',
        r'early\s+termination',
        r'withdrawal',
        r'stopping\s+rule',
        r'transition',
        r'rescue\s+therapy',
        r'dose\s+modification',
        r'dose\s+reduction',
    ]
    
    pattern = re.compile('|'.join(scheduling_keywords), re.IGNORECASE)
    
    scheduling_pages = []
    
    try:
        doc = fitz.open(pdf_path)
        total_pages = min(len(doc), max_pages_to_scan)
        
        for page_num in range(total_pages):
            page = doc[page_num]
            text = page.get_text().lower()
            
            matches = len(pattern.findall(text))
            if matches >= 2:
                scheduling_pages.append(page_num)
                logger.debug(f"Found scheduling keywords on page {page_num + 1}")
        
        doc.close()
        
        if len(scheduling_pages) > 20:
            scheduling_pages = scheduling_pages[:20]
        
        logger.info(f"Found {len(scheduling_pages)} potential scheduling pages")
        
    except Exception as e:
        logger.error(f"Error scanning PDF: {e}")
        scheduling_pages = list(range(min(30, get_page_count(pdf_path))))
    
    return scheduling_pages


def parse_timing_type(type_str: str) -> Optional[TimingType]:
    """Parse timing type string to enum."""
    if not type_str:
        return None
    type_map = {
        'before': TimingType.BEFORE,
        'after': TimingType.AFTER,
        'within': TimingType.WITHIN,
        'at': TimingType.AT,
        'between': TimingType.BETWEEN,
    }
    return type_map.get(type_str.lower())


def parse_relative_to(relative_str: str) -> Optional[TimingRelativeToFrom]:
    """Parse relative-to string to enum."""
    if not relative_str:
        return None
    rel_map = {
        'study start': TimingRelativeToFrom.STUDY_START,
        'randomization': TimingRelativeToFrom.RANDOMIZATION,
        'first dose': TimingRelativeToFrom.FIRST_DOSE,
        'last dose': TimingRelativeToFrom.LAST_DOSE,
        'previous visit': TimingRelativeToFrom.PREVIOUS_VISIT,
        'screening': TimingRelativeToFrom.SCREENING,
        'baseline': TimingRelativeToFrom.BASELINE,
        'end of treatment': TimingRelativeToFrom.END_OF_TREATMENT,
    }
    return rel_map.get(relative_str.lower())


def parse_transition_type(type_str: str) -> Optional[TransitionType]:
    """Parse transition type string to enum."""
    if not type_str:
        return None
    type_map = {
        'epoch transition': TransitionType.EPOCH_TRANSITION,
        'arm transition': TransitionType.ARM_TRANSITION,
        'discontinuation': TransitionType.DISCONTINUATION,
        'early termination': TransitionType.EARLY_TERMINATION,
        'rescue therapy': TransitionType.RESCUE_THERAPY,
        'dose modification': TransitionType.DOSE_MODIFICATION,
    }
    return type_map.get(type_str.lower())


def extract_scheduling(
    pdf_path: str,
    model: str = "gemini-2.5-pro",
    output_dir: Optional[str] = None,
) -> SchedulingResult:
    """
    Extract scheduling logic from protocol PDF.
    """
    logger.info("Starting scheduling logic extraction...")
    
    pages = find_scheduling_pages(pdf_path)
    if not pages:
        logger.warning("No scheduling pages found, using first 30 pages")
        pages = list(range(min(30, get_page_count(pdf_path))))
    
    text = extract_text_from_pages(pdf_path, pages)
    if not text:
        return SchedulingResult(
            success=False,
            error="Failed to extract text from PDF",
            pages_used=pages,
            model_used=model,
        )
    
    prompt = get_scheduling_prompt(text)
    system_prompt = get_system_prompt()
    
    try:
        # Combine system prompt with user prompt
        full_prompt = f"{system_prompt}\n\n{prompt}"
        result = call_llm(
            prompt=full_prompt,
            model_name=model,
            json_mode=True,
            extractor_name="scheduling",
            temperature=0.1,
        )
        response = result.get('response', '')
        
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = response
        
        raw_data = json.loads(json_str)

        citations: Dict[str, Dict[str, Dict[str, Any]]] = {}

        # Parse timings
        timings = []
        for t in raw_data.get('timings', []):
            timing_id = t.get('id', f"timing_{len(timings)+1}")
            name_raw = t.get('name', '')
            visit_raw = t.get('visit') or t.get('visitName')
            rel_visit_raw = t.get('relativeToVisit') or t.get('relativeToVisitName')
            value_raw = t.get('value')
            value_min_raw = t.get('valueMin')
            value_max_raw = t.get('valueMax')
            window_lower_raw = t.get('windowLower')
            window_upper_raw = t.get('windowUpper')

            for field_name, field_raw in (
                ('name', name_raw), ('visit', visit_raw), ('relativeToVisit', rel_visit_raw),
                ('value', value_raw), ('valueMin', value_min_raw), ('valueMax', value_max_raw),
                ('windowLower', window_lower_raw), ('windowUpper', window_upper_raw),
            ):
                _collect_citation(citations, timing_id, field_name, field_raw)

            timing = Timing(
                id=timing_id,
                name=_unwrap(name_raw, ''),
                timing_type=parse_timing_type(t.get('timingType')) or TimingType.AT,
                value=_unwrap(value_raw),
                value_min=_unwrap(value_min_raw),
                value_max=_unwrap(value_max_raw),
                unit=t.get('unit', 'days'),
                relative_to=parse_relative_to(t.get('relativeTo')),
                relative_to_timepoint_id=t.get('relativeToTimepointId'),
                window_lower=_unwrap(window_lower_raw),
                window_upper=_unwrap(window_upper_raw),
                visit_name=_unwrap(visit_raw),
                relative_to_visit_name=_unwrap(rel_visit_raw),
            )
            timings.append(timing)

        # Parse conditions
        conditions = []
        for c in raw_data.get('conditions', []):
            cond_id = c.get('id', f"cond_{len(conditions)+1}")
            name_raw = c.get('name', '')
            desc_raw = c.get('description')
            text_raw = c.get('text')
            for field_name, field_raw in (
                ('name', name_raw), ('description', desc_raw), ('text', text_raw),
            ):
                _collect_citation(citations, cond_id, field_name, field_raw)
            condition = Condition(
                id=cond_id,
                name=_unwrap(name_raw, ''),
                description=_unwrap(desc_raw),
                text=_unwrap(text_raw),
            )
            conditions.append(condition)

        # Parse transition rules
        transition_rules = []
        for tr in raw_data.get('transitionRules', []):
            trans_id = tr.get('id', f"trans_{len(transition_rules)+1}")
            name_raw = tr.get('name', '')
            desc_raw = tr.get('description')
            text_raw = tr.get('text')
            for field_name, field_raw in (
                ('name', name_raw), ('description', desc_raw), ('text', text_raw),
            ):
                _collect_citation(citations, trans_id, field_name, field_raw)
            rule = TransitionRule(
                id=trans_id,
                name=_unwrap(name_raw, ''),
                description=_unwrap(desc_raw),
                transition_type=parse_transition_type(tr.get('transitionType')),
                from_element_id=tr.get('fromElementId'),
                to_element_id=tr.get('toElementId'),
                condition_id=tr.get('conditionId'),
                text=_unwrap(text_raw),
            )
            transition_rules.append(rule)

        # Parse schedule exits
        schedule_exits = []
        for e in raw_data.get('scheduleExits', []):
            exit_id = e.get('id', f"exit_{len(schedule_exits)+1}")
            name_raw = e.get('name', '')
            desc_raw = e.get('description')
            for field_name, field_raw in (
                ('name', name_raw), ('description', desc_raw),
            ):
                _collect_citation(citations, exit_id, field_name, field_raw)
            exit_item = ScheduleTimelineExit(
                id=exit_id,
                name=_unwrap(name_raw, ''),
                description=_unwrap(desc_raw),
                exit_type=e.get('exitType', 'Early Termination'),
                condition_id=e.get('conditionId'),
            )
            schedule_exits.append(exit_item)

        # Parse decision instances
        decision_instances = []
        for d in raw_data.get('decisionInstances', []):
            dec_id = d.get('id', f"dec_{len(decision_instances)+1}")
            name_raw = d.get('name', '')
            desc_raw = d.get('description')
            for field_name, field_raw in (
                ('name', name_raw), ('description', desc_raw),
            ):
                _collect_citation(citations, dec_id, field_name, field_raw)
            decision = ScheduledDecisionInstance(
                id=dec_id,
                name=_unwrap(name_raw, ''),
                description=_unwrap(desc_raw),
                timepoint_id=d.get('timepointId', ''),
                condition_ids=d.get('conditionIds', []),
                default_transition_id=d.get('defaultTransitionId'),
            )
            decision_instances.append(decision)

        data = SchedulingData(
            timings=timings,
            conditions=conditions,
            transition_rules=transition_rules,
            schedule_exits=schedule_exits,
            decision_instances=decision_instances,
            citations=citations,
        )
        
        confidence = 0.0
        if timings or transition_rules or conditions:
            confidence = min(1.0, (len(timings) + len(transition_rules) + len(conditions)) / 15)
        
        result = SchedulingResult(
            success=True,
            data=data,
            pages_used=pages,
            model_used=model,
            confidence=confidence,
        )
        
        if output_dir:
            output_path = Path(output_dir) / "11_extraction_scheduling_logic.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
            logger.info(f"Saved scheduling logic to {output_path}")
        
        logger.info(f"Extracted {len(timings)} timings, {len(transition_rules)} rules, {len(conditions)} conditions")
        
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response: {e}")
        return SchedulingResult(
            success=False,
            error=f"JSON parse error: {e}",
            pages_used=pages,
            model_used=model,
        )
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        return SchedulingResult(
            success=False,
            error=str(e),
            pages_used=pages,
            model_used=model,
        )
