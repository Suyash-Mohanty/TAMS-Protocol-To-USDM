"""
PDF Utility Functions.

Common PDF operations used across the pipeline.
"""

import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


def extract_text_from_pages(
    pdf_path: str,
    pages: List[int],
    max_chars_per_page: int = 10000,
) -> Optional[str]:
    """
    Extract text from specific pages of a PDF.
    
    Args:
        pdf_path: Path to the PDF file
        pages: List of 0-indexed page numbers to extract
        max_chars_per_page: Maximum characters per page (to avoid huge texts)
        
    Returns:
        Combined text from all specified pages, or None on failure
    """
    try:
        import fitz  # PyMuPDF
        
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        
        texts = []
        for page_num in pages:
            if page_num < 0 or page_num >= total_pages:
                logger.warning(f"Page {page_num} out of range (0-{total_pages-1})")
                continue
                
            page = doc[page_num]
            text = page.get_text()
            
            # Truncate if too long
            if len(text) > max_chars_per_page:
                text = text[:max_chars_per_page] + "\n...[truncated]..."
                
            texts.append(f"--- Page {page_num + 1} ---\n{text}")
            
        doc.close()
        
        if texts:
            return "\n\n".join(texts)
        return None
        
    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {e}")
        return None


def get_page_count(pdf_path: str) -> int:
    """Get the number of pages in a PDF."""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        count = len(doc)
        doc.close()
        return count
    except Exception as e:
        logger.error(f"Failed to get page count: {e}")
        return 0


def render_page_to_image(
    pdf_path: str,
    page_num: int,
    output_path: str,
    dpi: int = 150,
) -> Optional[str]:
    """
    Render a PDF page to an image file.
    
    Args:
        pdf_path: Path to the PDF file
        page_num: 0-indexed page number
        output_path: Path for the output image
        dpi: Resolution in dots per inch
        
    Returns:
        Path to the created image, or None on failure
    """
    try:
        import fitz
        
        doc = fitz.open(pdf_path)
        if page_num < 0 or page_num >= len(doc):
            logger.error(f"Page {page_num} out of range")
            doc.close()
            return None
            
        page = doc[page_num]
        
        # Calculate zoom factor for DPI
        zoom = dpi / 72  # 72 is default PDF DPI
        matrix = fitz.Matrix(zoom, zoom)
        
        # Render page
        pix = page.get_pixmap(matrix=matrix)
        pix.save(output_path)
        
        doc.close()
        logger.info(f"Rendered page {page_num} to {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to render page: {e}")
        return None


def render_pages_to_images(
    pdf_path: str,
    pages: List[int],
    output_dir: str,
    dpi: int = 150,
    prefix: str = "page",
) -> List[str]:
    """
    Render multiple PDF pages to images.
    
    Args:
        pdf_path: Path to the PDF file
        pages: List of 0-indexed page numbers
        output_dir: Directory for output images
        dpi: Resolution in dots per inch
        prefix: Filename prefix
        
    Returns:
        List of paths to created images
    """
    from pathlib import Path
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    image_paths = []
    for page_num in pages:
        img_path = str(output_path / f"{prefix}_{page_num:03d}.png")
        result = render_page_to_image(pdf_path, page_num, img_path, dpi)
        if result:
            image_paths.append(result)
            
    return image_paths


# A numbered section heading on its own line ("5.4." / "4.2") or with its
# title ("4.2. Scientific Rationale ..."); top-level "6. Study Population".
_SECTION_NUMBER_LINE = r"\d{1,2}(?:\.\d{1,2})*\.?"


def extract_section_text(pdf_path: str, title_pattern: str, max_chars: int = 6000) -> Optional[str]:
    """Verbatim body text of a numbered protocol section, found by its title.

    `title_pattern` is a regex for the heading title (e.g. r"(scientific\s+)?
    rationale\s+for\s+(the\s+)?study\s+design"). Only numbered headings
    count ("4.2. Scientific Rationale ..." or "5.4." with the title on the
    next line), which excludes synopsis labels and running text; table-of-
    contents pages are skipped. When the title occurs under several numbers
    the occurrence with the most body text wins. The text runs to the next
    numbered heading; running page headers/footers (lines repeated on many
    pages) are removed. Returns None when the section isn't found.
    """
    import re
    from collections import Counter

    try:
        import fitz
        doc = fitz.open(pdf_path)
        pages = [doc[i].get_text() for i in range(len(doc))]
        doc.close()
    except Exception as e:
        logger.error(f"Section extraction failed for {pdf_path}: {e}")
        return None

    def _norm(line: str) -> str:
        return re.sub(r"\d+", "#", line.strip().lower())

    # Running headers/footers: lines with words (digits ignored) on >= 30% of
    # pages — bare section numbers ("5.4.") repeat too but are headings
    counts = Counter(n for p in pages for n in {_norm(l) for l in p.splitlines()
                                                if len(re.findall(r"[a-z]", l.lower())) >= 3})
    repeated = {n for n, c in counts.items() if len(pages) >= 5 and c >= 0.3 * len(pages)}

    lines: List[str] = []
    for text in pages:
        # TOC pages, and amendment summary tables whose rows cite section titles
        if len(re.findall(r"\.{5,}\s*\d", text)) >= 3 or re.search(
                r"description\s+of\s+change|summary\s+of\s+changes|brief\s+rationale", text, re.IGNORECASE):
            lines.append("")
            continue
        lines.extend(l for l in text.splitlines() if _norm(l) not in repeated)

    title_re = re.compile(rf"^\s*{title_pattern}\s*$", re.IGNORECASE)
    inline_re = re.compile(rf"^\s*{_SECTION_NUMBER_LINE}\s+{title_pattern}\s*$", re.IGNORECASE)
    number_re = re.compile(rf"^\s*{_SECTION_NUMBER_LINE}\s*$")
    heading_re = re.compile(rf"^\s*(?:{_SECTION_NUMBER_LINE}\s*$|\d{{1,2}}(?:\.\d{{1,2}})+\.?\s+[A-Z]|\d{{1,2}}\.\s+[A-Z][A-Za-z ,/&-]{{2,60}}$)")

    def _joined(i: int) -> str:
        return " ".join(l.strip() for l in lines[i:i + 3])

    best = None
    for i, line in enumerate(lines):
        start = None
        if inline_re.match(line):
            start = i + 1
        elif number_re.match(line):
            # title may wrap: "4.2 Scientific Rationale for" / "Study Design"
            for span in (1, 2):
                title = " ".join(l.strip() for l in lines[i + 1:i + 1 + span])
                if title_re.match(title):
                    start = i + 1 + span
                    break
        else:
            m = re.match(rf"^\s*{_SECTION_NUMBER_LINE}\s+(.*)$", line)
            if m and i + 1 < len(lines) and title_re.match(f"{m.group(1)} {lines[i + 1].strip()}"):
                start = i + 2
        if start is None:
            continue
        body = []
        for line2 in lines[start:]:
            if heading_re.match(line2):
                break
            body.append(line2.strip())
        text = re.sub(r"\s+", " ", " ".join(body)).strip()
        if text and (best is None or len(text) > len(best)):
            best = text
    if not best:
        return None
    return best[:max_chars]


def _protocol_body_lines(pdf_path: str, skip_amendment_tables: bool = False) -> Optional[List[str]]:
    """All protocol lines in order, without running page headers/footers
    (lines with words repeated on >= 30% of pages) and table-of-contents pages
    (optionally also amendment summary-of-changes pages)."""
    import re
    from collections import Counter
    try:
        import fitz
        doc = fitz.open(pdf_path)
        pages = [doc[i].get_text() for i in range(len(doc))]
        doc.close()
    except Exception as e:
        logger.error(f"Text extraction failed for {pdf_path}: {e}")
        return None

    def _norm(line: str) -> str:
        return re.sub(r"\d+", "#", line.strip().lower())

    counts = Counter(n for p in pages for n in {_norm(l) for l in p.splitlines()
                                                if len(re.findall(r"[a-z]", l.lower())) >= 3})
    repeated = {n for n, c in counts.items() if len(pages) >= 5 and c >= 0.3 * len(pages)}
    lines: List[str] = []
    for text in pages:
        if len(re.findall(r"\.{5,}\s*\d", text)) >= 3:
            continue
        if skip_amendment_tables and re.search(
                r"description\s+of\s+change|summary\s+of\s+changes|brief\s+rationale", text, re.IGNORECASE):
            continue
        lines.extend(l.rstrip() for l in text.splitlines() if _norm(l) not in repeated)
    return lines


def _to_xhtml(lines: List[str]) -> str:
    """Protocol lines as an XHTML fragment: a paragraph ends at a line ending
    in sentence punctuation or at a bullet/numbered line; text is escaped."""
    import html
    import re
    paragraphs, current = [], []
    for line in lines:
        text = line.strip()
        if not text:
            continue
        if current and re.match(r"^(?:[•▪◦\-–]|\(?[a-z0-9]{1,3}[.)])\s", text):
            paragraphs.append(" ".join(current))
            current = []
        current.append(text)
        if re.search(r"[.:;]$", text):
            paragraphs.append(" ".join(current))
            current = []
    if current:
        paragraphs.append(" ".join(current))
    body = "".join(f"<p>{html.escape(p, quote=False)}</p>" for p in paragraphs)
    return f'<div xmlns="http://www.w3.org/1999/xhtml">{body}</div>' if body else ""


def extract_numbered_sections(pdf_path: str, sections: List[tuple]) -> dict:
    """Verbatim XHTML text of each protocol section, keyed by section number.

    `sections` is [(number, title), ...] in document order (e.g. from the
    table of contents: ("6.2", "Exclusion Criteria"), ("10.8", "Appendix 8:
    Select Medications ...")). Each heading is located in the body as its
    number on its own line followed by the title, or "number title" on one
    line, searching forward from the previous section so earlier mentions
    (synopsis, cross-references) aren't taken. A section's text runs to the
    next located heading, so subsection text belongs to the subsection.
    Sections that can't be located are omitted.
    """
    import re
    lines = _protocol_body_lines(pdf_path)
    if not lines:
        return {}

    def _words(text: str) -> List[str]:
        text = re.sub(r"^(appendix|annex)\s+\d+[a-z]?\s*[:.\-–]?\s*", "", (text or "").lower())
        return re.findall(r"[a-z0-9]+", text)

    # Every candidate heading line for every section
    candidates = []  # per section: [(heading index, body start index)]
    numbers = []
    for number, title in sections:
        want = _words(title)[:3]
        if not number or not want:
            continue
        num = re.escape(str(number).rstrip("."))
        number_only = re.compile(rf"^\s*{num}\.?\s*$")
        inline = re.compile(rf"^\s*{num}\.?\s+(.*)$")
        found = []
        for i, line in enumerate(lines):
            if number_only.match(line):
                if _words(" ".join(l.strip() for l in lines[i + 1:i + 4]))[:len(want)] == want:
                    first = _words(lines[i + 1]) if i + 1 < len(lines) else []
                    found.append((i, i + (2 if len(first) >= len(want) else 3)))
                continue
            m = inline.match(line)
            if m:
                rest = _words(m.group(1))
                nxt = _words(lines[i + 1]) if i + 1 < len(lines) else []
                if (rest + nxt)[:len(want)] == want:
                    found.append((i, i + (1 if len(rest) >= len(want) else 2)))
        candidates.append(found)
        numbers.append(str(number))

    # Choose at most one candidate per section so the chosen headings appear
    # in document order and as many sections as possible are placed (one
    # stray match, e.g. a section title quoted in an amendment appendix, must
    # not displace the rest)
    best = {-1: (0, None, None)}  # last heading index -> (count, previous key, choice)
    states = [(-1, 0)]  # (last heading index, count)
    chains = {-1: []}
    for k, found in enumerate(candidates):
        new_chains = dict(chains)
        for last, chain in chains.items():
            for head, body in found:
                if head > last and (head not in new_chains or len(new_chains[head]) < len(chain) + 1):
                    new_chains[head] = chain + [(head, body, numbers[k])]
        chains = new_chains
    positions = max(chains.values(), key=len) if chains else []

    texts = {}
    for k, (head, start, number) in enumerate(positions):
        end = positions[k + 1][0] if k + 1 < len(positions) else len(lines)
        xhtml = _to_xhtml(lines[start:end])
        if xhtml:
            texts[number] = xhtml
    return texts
