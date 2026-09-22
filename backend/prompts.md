# Prompts - AI-First Backend Workflow

Quick-access prompts for each stage of the workflow. Copy and paste directly into GitHub Copilot (Agent Mode).

For full guidance and rules, refer to [QUICKSTART.md](QUICKSTART.md).

---

## Cortex-model-configuration-Step: Cortex Model Configuration Setup (Cortex projects only)

Run **once per project** when `LLM Provider: Cortex` and `Cortex Model Name` is `NEW`/blank in `PROJECT_OVERVIEW.md`.

```
Refer QUICKSTART.md and cortex_implementation.md and follow Cortex-model-configuration-Step: Cortex Model Configuration Setup. Create the Cortex model configuration via POST /model using the minimal required fields, then record the returned model name back into PROJECT_OVERVIEW.md under "Cortex Model Name".
```

> **After running this prompt:** Copilot will generate `scripts/create_cortex_model.py` but will **not** execute it. You must:
> 1. Run `python scripts/create_cortex_model.py` manually from the project root.
> 2. Copy the returned model name from the script output.
> 3. Paste it into `PROJECT_OVERVIEW.md` under `Cortex Model Name (MANDATORY if LLM Provider = Cortex)`.
> 4. **Do not proceed to Pre-Step or Level 1 until the model name is recorded in `PROJECT_OVERVIEW.md`.**

---

## Pre-Step: Populate Feature Implementation Template

```
Refer QUICKSTART.md and follow Pre-Step: Populate Feature Implementation Template. Use the rules defined in this section while populating the template.
```

---

## Level 1: Foundation / Project Kickoff

### Build Prompt

```
Refer QUICKSTART.md and follow Level 1: Foundation/Project Kickoff
```

### Evaluation Prompt

```
Refer EVALUATION_METRICS.md and evaluate the Level 1: Foundation output. Run the Section 2 (Level 1: Foundation Evaluation) structural completeness checklist, then complete Section 4 (Qualitative Scoring Rubric) and Section 5 (Scoring Summary Template) for Level 1. Provide the final verdict with scores and store it in evaluation_result_level_1.md file.
```

---

## Level 2: Sprint 1-N - Feature Implementation

### Build Prompt - Single User Story

```
Refer QUICKSTART.md and follow Level 2: Sprint 1-N- Feature Implementation
```

### Build Prompt - Multiple User Stories

```
Refer QUICKSTART.md and follow Level 2: Sprint 1-N- Feature Implementation. Implement all user stories sequentially, completing one user story fully before moving to the next. For each user story, list the backend tasks, implement them, and confirm completion before proceeding.
```

### Build Prompt - Specific User Stories

```
Refer QUICKSTART.md and follow Level 2: Sprint 1-N- Feature Implementation. Implement only user stories [US-001, US-002, US-003] in the specified order.
```

### Evaluation Prompt

```
Refer EVALUATION_METRICS.md and evaluate the Level 2: Feature Implementation output. Run Section 3 (Level 2: Feature Implementation Evaluation) for API contract fidelity and business logic correctness, then complete Section 4 (Qualitative Scoring Rubric) and Section 5 (Scoring Summary Template) for Level 2. Provide the final verdict with scores  and store it in evaluation_result_level_2.md file.
```

---

## Level 2 Post-Step: Explainability Artifacts

> **Note:** The five explainability artifacts (`change_summary.md`, `service_flow.md`, `architecture.md`, `traceability.md`, and inline `# why:` comments) are **auto-generated as part of every Level-2 run** — see `QUICKSTART.md` → "Level-2 Post-Generation Explainability Step". The standard Level-2 prompts above already trigger this step. **You do not need any of the prompts below in the normal workflow.**
>
> The prompts below exist **only for regenerating a single artifact later** — for example, after you hand-edit the service layer and want a fresh `service_flow.md`, or you delete an artifact by mistake. Pick the matching prompt and supply the user story ID.

### Regenerate - Change Summary only

```
Refer QUICKSTART.md, Level-2 Post-Generation Explainability Step, Section A (Change Summary). Regenerate docs/explainability/[US-001]/change_summary.md scoped only to files created or modified for user story [US-001].
```

### Regenerate - Service Flow Diagram only

```
Refer QUICKSTART.md, Level-2 Post-Generation Explainability Step, Section B (Service Flow Diagram). Regenerate docs/explainability/[US-001]/service_flow.md as a Mermaid sequenceDiagram, one diagram per endpoint in [US-001]. Read src/ to reflect actual generated code, not the spec. IMPORTANT: wrap every message label (text after ->> or -->>) in double quotes if it contains any of: + { } [ ] ( ) | ; * / — , — failure to do so causes a Mermaid parse error.
```

### Regenerate - Architecture Diagram only

```
Refer QUICKSTART.md, Level-2 Post-Generation Explainability Step, Section C (Architecture Diagram). Regenerate docs/explainability/[US-001]/architecture.md as a Mermaid flowchart, highlighting modules new to [US-001] with the :::new class. Include only modules wired into the new code path.
```

### Regenerate - Traceability Matrix only

```
Refer QUICKSTART.md, Level-2 Post-Generation Explainability Step, Section D (Traceability Matrix). Regenerate docs/explainability/[US-001]/traceability.md mapping each acceptance criterion from FEATURE_IMPLEMENTATION.md to the file and function that implements it. Copy AC text verbatim.
```

### Regenerate - Why-Comment Enrichment only

```
Refer QUICKSTART.md, Level-2 Post-Generation Explainability Step, Section E (Why-Comment Enrichment). Re-read the files generated for [US-001] and inject one-line `# why:` comments above non-trivial logic blocks only (conditionals with non-obvious intent, retry loops, data transforms, magic numbers, exception-mapping branches). Do not change runtime behavior — comment additions only. Verify with `python -m py_compile` on every modified file.
```
