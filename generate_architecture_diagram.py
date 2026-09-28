"""Render docs/architecture_diagram.png — the PDF-to-USDM execution workflow.

Draws the pipeline described in docs/extraction-pipeline.md: wave-based agent
execution over a shared ContextStore, followed by USDM assembly, provenance,
and optional CORE validation. Uses Pillow only (already a project dependency)
so it needs no extra tools (graphviz/mermaid) to run.

Re-run any time the wave/agent structure in docs/extraction-pipeline.md changes:
    python generate_architecture_diagram.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH = 1600
MARGIN = 40
SPINE_X0, SPINE_X1 = 260, 1080          # main vertical flow column
RAIL_X0, RAIL_X1 = 1140, 1560           # ContextStore side rail
GAP = 34


def load_font(names, size):
    for name in names:
        for base in (r"C:\Windows\Fonts", ""):
            path = f"{base}\\{name}" if base else name
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


TITLE_FONT = load_font(["segoeuib.ttf", "arialbd.ttf"], 30)
BOX_TITLE_FONT = load_font(["segoeuib.ttf", "arialbd.ttf"], 19)
BODY_FONT = load_font(["segoeui.ttf", "arial.ttf"], 15)
SMALL_FONT = load_font(["segoeuii.ttf", "ariali.ttf"], 13)


def wrap(draw, text, font, max_width):
    words = text.split(" ")
    lines, current = [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textbbox((0, 0), trial, font=font)[2] <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def box_height(draw, title, bullets, width, has_note=False):
    pad = 16
    h = pad * 2 + 26  # title line
    inner_w = width - pad * 2
    for b in bullets or []:
        for line in wrap(draw, f"\u2022 {b}", BODY_FONT, inner_w - 10):
            h += 21
        h += 4
    if has_note:
        h += 20
    return max(h, 60)


def draw_box(draw, x0, y0, x1, y1, title, bullets=None, note=None,
             fill="#DCE8FA", outline="#3B6EA5", title_color="#1B3A5C"):
    draw.rounded_rectangle([x0, y0, x1, y1], radius=12, fill=fill, outline=outline, width=2)
    pad = 16
    tx, ty = x0 + pad, y0 + pad
    draw.text((tx, ty), title, font=BOX_TITLE_FONT, fill=title_color)
    ty += 26
    inner_w = (x1 - x0) - pad * 2
    for b in bullets or []:
        for i, line in enumerate(wrap(draw, f"\u2022 {b}", BODY_FONT, inner_w - 10)):
            prefix_x = tx if i == 0 else tx + 14
            draw.text((prefix_x, ty), line, font=BODY_FONT, fill="#222222")
            ty += 21
        ty += 4
    if note:
        draw.text((tx, ty), note, font=SMALL_FONT, fill="#555555")
    return (x0, y0, x1, y1)


def arrow(draw, points, color="#444444", width=3, head=9):
    for i in range(len(points) - 1):
        draw.line([points[i], points[i + 1]], fill=color, width=width)
    (x0, y0), (x1, y1) = points[-2], points[-1]
    dx, dy = x1 - x0, y1 - y0
    length = max((dx ** 2 + dy ** 2) ** 0.5, 1e-6)
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    tip = (x1, y1)
    left = (x1 - ux * head - px * head * 0.6, y1 - uy * head - py * head * 0.6)
    right = (x1 - ux * head + px * head * 0.6, y1 - uy * head + py * head * 0.6)
    draw.polygon([tip, left, right], fill=color)


def main():
    # -- Layout pass 1: figure out heights with a throwaway image/draw ---------
    probe = Image.new("RGB", (WIDTH, 10))
    pd = ImageDraw.Draw(probe)

    spine_w = SPINE_X1 - SPINE_X0
    rail_w = RAIL_X1 - RAIL_X0

    nodes = []  # (kind, title, bullets, note)
    nodes.append(("input", "Input: Clinical Trial Protocol PDF", [], None))
    nodes.append(("plain", "OrchestratorAgent.create_execution_plan()",
                  ["Builds a wave-based dependency DAG from each agent's declared capabilities/dependencies"], None))
    nodes.append(("wave", "Wave 0 \u2014 no dependencies (parallel)",
                  ["PDF Parser \u2014 pdf_page (text, images, tables)",
                   "Metadata Agent \u2014 study_title, study_identifier, organization, study_role, indication, study_phase",
                   "Narrative Agent \u2014 narrative_content_item, abbreviation, study_definition_document",
                   "Doc Structure Agent \u2014 comment_annotation, document_version",
                   "SoA Vision Agent \u2014 epoch, encounter, activity, header_structure"], None))
    nodes.append(("wave", "Wave 1 \u2014 depends on Metadata / Vision",
                  ["Eligibility Agent \u2014 eligibility_criterion, criterion_item, study_population",
                   "Objectives Agent \u2014 objective, endpoint, estimand, analysis_population",
                   "Study Design Agent \u2014 study_design, study_arm, study_cell, study_element",
                   "Advanced Agent \u2014 study_amendment, geographic_scope",
                   "SoA Text Agent \u2014 activity, scheduled_instance"], None))
    nodes.append(("wave", "Wave 2 \u2014 depends on Vision + Text + Design",
                  ["Interventions Agent \u2014 study_intervention, administrable_product, substance, medical_device",
                   "Procedures Agent \u2014 procedure, medical_device",
                   "Execution Agent \u2014 dosing_regimen, visit_window, state_machine, footnote_condition"], None))
    nodes.append(("wave", "Wave 3 \u2014 depends on Execution + all prior",
                  ["Scheduling Agent \u2014 timing, schedule_exit, transition_rule",
                   "Biomedical Concepts Agent \u2014 biomedical_concept, biomedical_concept_category",
                   "Post-Processing Agent \u2014 fixes/normalizes entities in place",
                   "Validation Agent \u2014 validation_report",
                   "Reconciliation Agent \u2014 reconciliation_report",
                   "Enrichment Agent \u2014 adds NCI EVS terminology codes"], None))
    nodes.append(("generator", "USDMGeneratorAgent.execute()",
                  ["Reads every entity from the ContextStore",
                   "Places each into the USDM v4.0 JSON skeleton (study, studyDesigns, epochs, encounters, "
                   "activities, objectives, endpoints, interventions, eligibility, scheduleTimelines, ...)",
                   "Runs post-processing fixups (sponsor identifier, therapeutic areas, codelists, masking links, "
                   "document-version links, required-field defaults)"], None))
    nodes.append(("output", "Output: USDM v4.0 JSON",
                  ["study.versions[0].studyDesigns[0] fully populated per Entity Type \u2192 USDM Placement Mapping"], None))

    heights = []
    for kind, title, bullets, note in nodes:
        w = rail_w if kind == "rail" else spine_w
        heights.append(box_height(pd, title, bullets, w, has_note=bool(note)))

    branch_h = box_height(pd, "ProvenanceAgent.execute()",
                           ["Generates provenance.json mapping each USDM entity to its source PDF page(s)"],
                           (spine_w - 40) // 2)
    branch_h = max(branch_h, box_height(pd, "CDISC CORE Engine (optional)",
                                         ["Runs conformance checks against official USDM/CORE validation rules"],
                                         (spine_w - 40) // 2))

    # -- Compute y-coordinates ---------------------------------------------------
    y = MARGIN + 50  # leave room for title text
    wave_top = None
    wave_bottom = None
    box_rects = []
    for i, ((kind, title, bullets, note), h) in enumerate(zip(nodes, heights)):
        if kind == "wave" and wave_top is None:
            wave_top = y
        box_rects.append((y, y + h))
        if kind == "wave":
            wave_bottom = y + h
        y += h + GAP
        if kind == "wave" and i + 1 < len(nodes) and nodes[i + 1][0] != "wave":
            y += 40  # extra room for the rail's merge arrow after the last wave

    branch_top = box_rects[-2][1] + GAP
    branch_bottom = branch_top + branch_h
    box_rects[-1] = (branch_bottom + GAP, branch_bottom + GAP + heights[-1])
    total_h = box_rects[-1][1] + MARGIN

    # -- Render -------------------------------------------------------------------
    img = Image.new("RGB", (WIDTH, total_h), "#FFFFFF")
    draw = ImageDraw.Draw(img)
    draw.text((MARGIN, 10), "Protocol2USDM \u2014 Execution Workflow: PDF \u2192 USDM v4.0 JSON",
              font=TITLE_FONT, fill="#111111")

    palette = {
        "input": ("#DCEFDC", "#2E7D32", "#1B4D1F"),
        "plain": ("#EDEDED", "#777777", "#333333"),
        "wave": ("#DCE8FA", "#3B6EA5", "#1B3A5C"),
        "generator": ("#E8DCF5", "#6A3FA0", "#3B2060"),
        "output": ("#DCEFDC", "#2E7D32", "#1B4D1F"),
    }

    rects = {}
    for (kind, title, bullets, note), (y0, y1) in zip(nodes, box_rects):
        fill, outline, tcolor = palette[kind]
        rects[title] = draw_box(draw, SPINE_X0, y0, SPINE_X1, y1, title, bullets, note,
                                 fill=fill, outline=outline, title_color=tcolor)

    # Spine arrows between consecutive nodes (skip the merge point after last wave)
    for i in range(len(box_rects) - 1):
        y0a, y1a = box_rects[i]
        y0b, y1b = box_rects[i + 1]
        if nodes[i][0] == "wave" and nodes[i + 1][0] == "generator":
            continue  # generator is fed via the ContextStore rail instead
        cx = (SPINE_X0 + SPINE_X1) // 2
        arrow(draw, [(cx, y1a), (cx, y0b)])

    # ContextStore rail spanning all wave boxes
    rail_y0, rail_y1 = wave_top, wave_bottom
    draw.rounded_rectangle([RAIL_X0, rail_y0, RAIL_X1, rail_y1], radius=12,
                           fill="#FFF3CD", outline="#B8860B", width=2)
    rail_cx = (RAIL_X0 + RAIL_X1) // 2
    draw.text((RAIL_X0 + 16, rail_y0 + 16), "ContextStore", font=BOX_TITLE_FONT, fill="#7A5A00")
    for line_no, line in enumerate(wrap(draw, "Shared entity store \u2014 every agent above reads and writes "
                                         "its entities here via ContextStore.add_entity()",
                                         BODY_FONT, rail_w - 32)):
        draw.text((RAIL_X0 + 16, rail_y0 + 46 + line_no * 21), line, font=BODY_FONT, fill="#333333")

    # Short arrows from each wave box into the rail
    for (kind, *_r), (y0, y1) in zip(nodes, box_rects):
        if kind != "wave":
            continue
        cy = (y0 + y1) // 2
        arrow(draw, [(SPINE_X1, cy), (RAIL_X0, cy)])

    # Rail -> USDM Generator
    gen_y0, gen_y1 = box_rects[len(nodes) - 3]  # generator index is fixed: -3 from end (before branch+output... )
    # locate generator rect precisely by title
    gen_idx = [n[0] for n in nodes].index("generator")
    gen_y0, gen_y1 = box_rects[gen_idx]
    gen_cx = (SPINE_X0 + SPINE_X1) // 2
    mid_y = rail_y1 + 20
    arrow(draw, [(rail_cx, rail_y1), (rail_cx, mid_y), (gen_cx, mid_y), (gen_cx, gen_y0)])

    # Generator -> branch (Provenance / CORE validation)
    branch_w = (spine_w - 40) // 2
    left_x0, left_x1 = SPINE_X0, SPINE_X0 + branch_w
    right_x0, right_x1 = SPINE_X1 - branch_w, SPINE_X1
    branch_mid_y = gen_y1 + GAP // 2
    arrow(draw, [(gen_cx, gen_y1), (gen_cx, branch_mid_y)])
    arrow(draw, [(gen_cx, branch_mid_y), ((left_x0 + left_x1) // 2, branch_mid_y), ((left_x0 + left_x1) // 2, branch_top)])
    arrow(draw, [(gen_cx, branch_mid_y), ((right_x0 + right_x1) // 2, branch_mid_y), ((right_x0 + right_x1) // 2, branch_top)])

    draw_box(draw, left_x0, branch_top, left_x1, branch_bottom, "ProvenanceAgent.execute()",
             ["Generates provenance.json mapping each USDM entity to its source PDF page(s)"],
             fill="#FCE8D5", outline="#B5651D", title_color="#7A3B0F")
    draw_box(draw, right_x0, branch_top, right_x1, branch_bottom, "CDISC CORE Engine (optional)",
             ["Runs conformance checks against official USDM/CORE validation rules"],
             fill="#EDEDED", outline="#777777", title_color="#333333")

    # Branch -> Output
    out_y0, out_y1 = box_rects[-1]
    arrow(draw, [((left_x0 + left_x1) // 2, branch_bottom), ((left_x0 + left_x1) // 2, out_y0 - 15), (gen_cx, out_y0 - 15), (gen_cx, out_y0)])
    arrow(draw, [((right_x0 + right_x1) // 2, branch_bottom), ((right_x0 + right_x1) // 2, out_y0 - 15), (gen_cx, out_y0 - 15), (gen_cx, out_y0)])

    out_path = Path(__file__).resolve().parent / "docs" / "architecture_diagram.png"
    img.save(out_path)
    print(f"Wrote {out_path} ({img.width}x{img.height})")


if __name__ == "__main__":
    main()
