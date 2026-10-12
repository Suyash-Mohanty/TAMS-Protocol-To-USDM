"""Text helpers for the SDR merge: normalisation, emptiness and similarity."""
import re
from difflib import SequenceMatcher
from typing import Any, Set

_TAG = re.compile(r"<[^>]+>")
_NON_ALNUM = re.compile(r"[^a-z0-9]+")
_ID_TAIL = re.compile(r"[A-Za-z]$")


def strip_markup(text: Any) -> str:
    return _TAG.sub(" ", str(text or ""))


def norm(text: Any) -> str:
    """Lower-case alphanumerics only (markup, case, spacing, punctuation ignored)."""
    return _NON_ALNUM.sub("", strip_markup(text).lower())


def tokens(text: Any) -> Set[str]:
    return {t for t in re.split(r"[^a-z0-9]+", strip_markup(text).lower()) if t}


def similarity(a: Any, b: Any) -> float:
    """0..1; max of sequence ratio and token containment (handles 'Foo' vs 'Foo (Local)')."""
    na, nb = norm(a), norm(b)
    if not na or not nb:
        return 0.0
    if na == nb:
        return 1.0
    ratio = SequenceMatcher(None, na, nb).ratio()
    nums_a, nums_b = re.findall(r"\d+", strip_markup(a)), re.findall(r"\d+", strip_markup(b))
    if nums_a and nums_b and nums_a != nums_b:
        return min(ratio, 0.5)       # 'Period 1' / 'Period 2', 'V2' / 'V12' are different items
    ta, tb = tokens(a), tokens(b)
    if ta and tb:
        overlap = len(ta & tb) / min(len(ta), len(tb))
        if min(len(ta), len(tb)) >= 2:
            ratio = max(ratio, 0.9 * overlap)
        short, long_ = (ta, tb) if len(ta) <= len(tb) else (tb, ta)
        if short <= long_ and len(short) <= 3 and len(norm(" ".join(short))) >= 5:
            ratio = max(ratio, 0.88)   # 'GlucaGen' within 'GlucaGen (intramuscular glucagon)'
    return ratio


def is_empty(value: Any) -> bool:
    """None, '', [], {} , an empty XHTML wrapper, or a dict/list holding nothing but empties."""
    if value is None:
        return True
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return True
        return stripped.startswith("<") and not strip_markup(stripped).strip()
    if isinstance(value, (list, tuple)):
        return all(is_empty(v) for v in value)
    if isinstance(value, dict):
        return all(is_empty(v) for k, v in value.items() if k not in ("id", "instanceType"))
    return False
