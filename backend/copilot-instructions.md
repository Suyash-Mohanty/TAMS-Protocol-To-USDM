# Copilot Instructions

## Purpose

This file configures GitHub Copilot and similar AI coding assistants to work effectively on this repository by enforcing organizational standards, project-specific context, and team preferences. All suggestions and implementations MUST align with the guidelines defined here and in referenced documentation.

## Sources of Truth & Precedence

When generating code or providing guidance, consult these sources in order of precedence:

1. **PROJECT_OVERVIEW.md** (primary source of truth)
   - Domain context, use cases, and business logic
   - Technology stack and architecture decisions
   - Non-functional requirements and constraints
   - Team preferences and deployment environments
   - Integration points and dependencies

2. **FEATURE_IMPLEMENTATION.md** (design spec — governs Level-2 feature code)
   - API contracts, request/response schemas, and validation rules
   - Business logic rules and workflows
   - Data access patterns and integration contracts
   - Service layer design decisions
   - Acceptance criteria that new code must satisfy
   - **Scope:** applies to Level-2 feature implementation only. Does not override #1 or #3 for architectural or style decisions outside the feature scope.

3. **PYTHON_CODING_STANDARDS.md** (mandatory for all Python code)
   - Style, formatting, and naming conventions
   - Type hints and documentation requirements
   - Error handling and logging patterns
   - Security and testing standards

4. **Repository code and tests** (authoritative for current behavior outside the feature spec)
   - Existing patterns, idioms, and conventions — followed unless #1 or #2 explicitly overrides them
   - Current API contracts and schemas
   - Test structure and fixture usage

5. **Version control history** (context for decisions)
   - Recent changes and their rationale
   - Evolution of patterns and practices

**Conflict Resolution**:
- If PROJECT_OVERVIEW.md conflicts with code, explain the discrepancy and ask for confirmation before proceeding.
- If FEATURE_IMPLEMENTATION.md conflicts with existing code patterns, apply the **Existing Code Override Justification Rule** (see "Implementation Rules") — do NOT silently follow either; surface the conflict and ask.
- If coding standards conflict with existing code, favor standards for new code and flag inconsistencies.
- If instructions are ambiguous, make assumptions explicit and request clarification.

## Deployment Target Reference

These tables describe the valid values for the `Deployment Target` and `MCP Transport` fields the developer fills into `PROJECT_OVERVIEW.md`. Use them when validating the developer's choice or when the developer asks which option fits their use case.

### Deployment Target — Combination Guide

Five valid combinations are supported. Exactly one is set per project:

| Combination | When to choose |
|-------------|----------------|
| `FastAPI` | REST API only; consumed by browsers, mobile, or other HTTP clients |
| `AWS Lambda` | Serverless REST/event-driven; consumed via API Gateway, EventBridge, etc. |
| `FastMCP Server` | MCP-only; consumed exclusively by AI clients (Claude Desktop, IDE extensions, agent frameworks) |
| `FastAPI + FastMCP` | Same project exposes a REST API **and** an MCP server, both wrapping the same service layer (`src/services/`) |
| `AWS Lambda + FastMCP` | Lambda functions for REST/events **plus** a long-lived MCP server process (the MCP server itself does NOT run inside Lambda — it runs as a hosted long-lived process) |

### MCP Transport — When to Pick Which

Required only when `Deployment Target` includes FastMCP:

| Transport | Use when |
|-----------|----------|
| `stdio` | Local AI clients (Claude Desktop, IDE extensions); simplest setup; no network |
| `streamable-http` | Remote/web AI clients; modern HTTP transport; preferred for production deployments |
| `sse` | Legacy Server-Sent Events; mostly superseded by `streamable-http` — choose only when integrating with a client that explicitly requires it |

### FastMCP Version

Default to **FastMCP 2.x** (`pip install fastmcp`, `from fastmcp import FastMCP`). Use FastMCP 1.x (the version bundled inside Anthropic's `mcp` SDK) only when the project explicitly pins it. Never install both packages or mix imports in one project.

## Before You Write or Change Code (Mandatory Checklist)

**MUST** complete this checklist before implementing any change:

- [ ] **Identify scope**: Determine which files, modules, or functions require changes
- [ ] **Confirm intent**: Verify understanding of the requested behavior and acceptance criteria
- [ ] **Check deployment target**: Read the **Deployment Target** field from `PROJECT_OVERVIEW.md` (Section 2 — Tech Stack Decisions). Generate only target-appropriate artifacts — FastAPI routes, Lambda handlers, FastMCP tools/resources/prompts, or the appropriate combination (`FastAPI + FastMCP`, `AWS Lambda + FastMCP`). When target includes FastMCP, also read **MCP Transport** and **MCP Server Name** from `PROJECT_OVERVIEW.md`; if either is missing, ask the developer before generating. **FastMCP Version** is optional — default to 2.x unless the developer has explicitly set it to 1.x.
- [ ] **Check MCP component type**: When generating MCP code, classify each capability as a **tool** (model-invoked action — mutates state, runs a query, hits an API), a **resource** (client-pulled read-only data exposed by URI), or a **prompt** (reusable user-invoked template). See the decision matrix in `FEATURE_IMPLEMENTATION.md` and the wiring example in `cortex_implementation.md`. If the classification is ambiguous, ask the developer.
- [ ] **Check LLM provider**: Read the **LLM Provider** field from `PROJECT_OVERVIEW.md`. If `Cortex`, consult `cortex_implementation.md` before generating any LLM integration code. If other provider, follow `FEATURE_IMPLEMENTATION.md`. If absent and LLM is needed, ask the user.
- [ ] **Check Cortex Model Name**: If `LLM Provider: Cortex`, read the **Cortex Model Name** field from `PROJECT_OVERVIEW.md`. If it is `NEW`, blank, or missing, run **Cortex-model-configuration-Step** from `cortex_implementation.md` before proceeding to Pre-Step or Level 1. If a valid model name is already present, skip the configuration step.
- [ ] **Check RAGAS requirement**: If `LLM Provider: Cortex`, scan `BRD.md`, `UserStories.md`, and `PROJECT_OVERVIEW.md` for AI output evaluation requirements (e.g., answer correctness, model benchmarking, RAG quality). If evaluation is required, follow the **RAGAS Evaluation Integration** section in `cortex_implementation.md`. If absent or ambiguous, ask the user before generating RAGAS files.
- [ ] **Consolidate endpoint logic**: MUST consolidate all logic for the same endpoint into a single route handler (FastAPI) or a single Lambda handler function (AWS Lambda)
- [ ] **Check PROJECT_OVERVIEW.md**: Review relevant sections (domain, constraints, NFRs, integrations)
- [ ] **Review existing patterns**: Examine similar functionality in the codebase for consistency
- [ ] **Identify impacts**: List affected tests, documentation, configuration, and dependent code
- [ ] **Plan backwards compatibility**: Determine if changes break existing APIs or contracts
- [ ] **Consider security**: Assess input validation, authentication, authorization, and data handling implications

If any checklist item cannot be completed with available information, ask targeted questions before proceeding.

## Implementation Rules (Always)

- **MUST** prefer minimal, reviewable diffs over large rewrites
- **MUST** maintain consistency with existing code patterns and conventions in the repository, **except** when `FEATURE_IMPLEMENTATION.md` or `PROJECT_OVERVIEW.md` explicitly prescribes a different pattern — in that case, apply the Existing Code Override Justification Rule below
- **MUST NOT** invent APIs, schemas, configuration keys, or data models—confirm from PROJECT_OVERVIEW.md or existing code
- **MUST** preserve backwards compatibility unless explicitly instructed otherwise
- **MUST** follow the principle of least surprise—favor conventional solutions over clever ones
- **SHOULD** extract common logic into reusable functions rather than duplicating code
- **SHOULD** use dependency injection and loose coupling to enable testability
- **MAY** suggest refactoring opportunities but implement them only when approved
- **MUST** include type hints for all new Python functions and methods
- **MUST** add or update tests for any functional change

### Existing Code Override Justification Rule (MANDATORY)

**Gate sequencing note:** Before Level-2 code generation, three gates must pass in this order:
1. **Confirm intent** (this checklist, item "Confirm intent") — verify understanding of requested behavior.
2. **Validate API Contract** (`QUICKSTART.md`, "Validate API Contract Before Code Generation") — confirm all endpoint/schema info is present.
3. **Design Decision Extraction** (`QUICKSTART.md`, "Design Decision Extraction Pre-Step") — extract design decisions from `FEATURE_IMPLEMENTATION.md`, append the checklist as a new section at the end of that file, send a short chat message pointing the developer there, and wait for their in-chat confirmation before proceeding. Do not reproduce the checklist in chat.

These three gates are complementary, not redundant: gate 1 checks behavioral understanding, gate 2 checks information completeness, gate 3 locks design intent. All three must pass before code generation starts.

---

When generating new code, the **design spec** (`FEATURE_IMPLEMENTATION.md`, `PROJECT_OVERVIEW.md`, acceptance criteria) takes precedence over patterns found in existing code or sample `.md` files — **excluding** files inside `light_client/`, which is a read-only vendored library that must never be modified regardless of any design spec instruction. If the AI detects a conflict between the design spec and an existing code pattern (including patterns demonstrated in sample files, `COMPLETE_EXAMPLE.md`, or previously generated code), it **MUST NOT** silently follow the existing pattern. Instead:

1. **STOP** code generation for the conflicting section.
2. **Name both approaches explicitly:**
   - "Design spec states: [exact spec requirement]"
   - "Existing code pattern does: [describe the conflicting pattern and where it was found]"
3. **Ask the developer** which approach to follow before proceeding.

**Examples of conflicts this rule catches:**
- Design spec says "retry with exponential backoff" but existing code uses a fixed-interval retry loop
- Design spec defines a response schema with `snake_case` fields but existing code returns `camelCase`
- Design spec requires pagination via cursor-based approach but existing endpoints use offset/limit
- Design spec calls for dependency injection but existing services instantiate clients inline
- Design spec defines a new data access pattern (e.g., repository pattern) but existing code queries the DB directly from the service layer

**This rule does NOT apply when:**
- The existing code pattern and design spec are compatible (no conflict)
- The developer has already acknowledged the divergence in a prior conversation turn
- The conflict is purely stylistic and covered by `PYTHON_CODING_STANDARDS.md` (coding standards always win for style)
- The conflicting file is inside `light_client/` (always read-only — never modify)

## Backend Only Implementation (Level-2)

**Scope Limitation:**
- **MUST** implement only backend tasks (API endpoints, service layer, database, integrations, data pipelines)
- **MUST NOT** implement frontend tasks (UI components, React/Angular components, CSS, JavaScript client-side code)
- **MUST** identify frontend tasks from FEATURE_IMPLEMENTATION.md and explicitly inform the user that frontend implementation is out of scope

**Frontend Task Identification:**
When a task or subtask involves any of the following, mark it as frontend and do not generate code:
- React/Angular/Vue components
- UI/UX implementation (buttons, forms, tables, modals, navigation, dashboards)
- CSS/styling
- Client-side JavaScript
- Browser-specific functionality (localStorage, cookies, DOM manipulation)
- Frontend routing and navigation
- Frontend state management (Redux, Vuex, etc.)
- Frontend testing (UI component tests, browser tests, E2E UI tests)

**Response Pattern for Frontend Tasks:**
When encountering a frontend task, respond with:

```
**Frontend Task Detected: [Task/Subtask Name]**

This task involves frontend implementation:
- [List frontend components/features mentioned]

I am configured to generate backend code only. Please assign this task to the frontend development team.

**Backend Dependencies (if any):**
- API Endpoint: [endpoint if backend support is needed]
- Request Schema: [expected request format]
- Response Schema: [data structure the frontend should expect]
```

**Backend Task Identification:**
Generate code only for tasks involving:
- FastAPI route handlers and endpoints (when target = FastAPI)
- AWS Lambda handler functions (`def lambda_handler(event, context):`) (when target = AWS Lambda)
- Pydantic request/response models
- Service layer business logic (framework-agnostic — shared by both targets)
- Database models (SQLAlchemy/ORM)
- Database migrations (Alembic)
- Integration clients (external APIs, AWS services, Azure services)
- **Cortex LLM integration** (`src/integrations/cortex_client.py`, `light_client/`) — **only when `LLM Provider: Cortex`**; follow `cortex_implementation.md` exclusively
- **Cortex RAGAS evaluation** (`src/services/ragas_evaluation_service.py`, RAGAS endpoints/handlers) — **only when `LLM Provider: Cortex` AND project requires AI output evaluation**; follow the RAGAS section in `cortex_implementation.md`
- Middleware (authentication, authorization, logging, CORS) (FastAPI target)
- Lambda response utilities (`src/utils/lambda_response.py`) (AWS Lambda target)
- **FastMCP server entry point** (`src/mcp_server/server.py`) — only when `Deployment Target` includes FastMCP; instantiates `FastMCP(name=...)`, configures lifespan, and starts the transport
- **FastMCP tools** (`src/mcp_server/tools/<feature>.py`, `@mcp.tool` decorators) — only when target includes FastMCP; thin wrappers over `src/services/`
- **FastMCP resources** (`src/mcp_server/resources/<feature>.py`, `@mcp.resource("uri://...")` decorators) — only when target includes FastMCP
- **FastMCP prompts** (`src/mcp_server/prompts/<feature>.py`, `@mcp.prompt` decorators) — only when target includes FastMCP
- **FastMCP lifespan / context-manager setup** — only when target includes FastMCP; initializes shared resources (Cortex client, DB pools) once at startup
- **FastMCP integration tests** (`tests/mcp/`, in-memory `fastmcp.Client` pattern) — only when target includes FastMCP
- Utilities and helpers
- Data pipelines and ETL processes
- Background jobs and task queues
- API documentation (OpenAPI/Swagger)
- Backend unit and integration tests (pytest)
- Deployment artifacts (`deployment/fastapi/`, `deployment/lambda/`, or `deployment/mcp/`, per target)

**Post-Generation Explainability (MANDATORY auto-final-phase of every Level-2 run):**
- After the Design Decision Extraction Pre-Step sign-off and Level-2 code generation completes for any user story, **automatically execute** the **Level-2 Post-Generation Explainability Step** (see `QUICKSTART.md`) as the final phase of the same Level-2 turn — **before** declaring the story done. This is **not** a separate developer prompt; once the developer issues the Level-2 prompt and confirms the design decision checklist, code generation and the Post-Step both run automatically without additional prompts.
- Produces four Markdown artifacts under `docs/explainability/<US-ID>/` (change summary, Mermaid service-flow sequence diagram, Mermaid architecture component diagram, AC-to-code traceability matrix) plus inline `# why:` comments on non-trivial blocks in the modified `.py` files.
- The implementation summary returned to the developer at the end of Level-2 MUST list the four artifact paths created and confirm the why-comment pass ran with verification.
- For multi-user-story sessions: run the Post-Step **after each user story**, not once at the end.
- The why-comment pass MUST NOT change runtime behavior — comment additions only.
- Per-section prompts in `prompts.md` exist only for regenerating a single artifact on demand; they are not the primary trigger.

## Security & Privacy Guardrails

**Authentication & Authorization**:
- **MUST** validate all user permissions before performing privileged operations
- **MUST NOT** bypass or weaken existing authentication or authorization mechanisms
- **MUST** verify user identity for sensitive operations

**Input Validation & Output Encoding**:
- **MUST** validate and sanitize all external input (API requests, user input, file uploads, environment variables)
- **MUST** encode output appropriately for the target context (HTML, SQL, shell, JSON)
- **MUST** use parameterized queries for database operations

**Secrets & Sensitive Data**:
- **MUST NOT** log, print, or expose secrets, API keys, passwords, tokens, or credentials
- **MUST NOT** log personally identifiable information (PII) without explicit redaction
- **MUST** load secrets from environment variables or secret management systems
- **MUST** check PROJECT_OVERVIEW.md for data classification requirements

**Resilience & Safe Defaults**:
- **MUST** add timeouts for all external calls (HTTP, database, message queues)
- **SHOULD** implement retry logic with exponential backoff for transient failures
- **MUST** handle exceptions gracefully and provide actionable error messages
- **MUST** use safe defaults when configuration is missing

## Python-Specific Rules

**MUST** follow all requirements in PYTHON_CODING_STANDARDS.md, including:

**Type Hints**:
- **MUST** add type hints to all function signatures
- **MUST** specify return types, including `None`
- **MUST NOT** use `Any` without justification documented in comments
- **SHOULD** use `Protocol` for structural subtyping and `TypeVar` for generics

**Error Handling**:
- **MUST** use specific exception types, not bare `Exception`
- **MUST** preserve exception context with `raise ... from ...` when wrapping
- **MUST NOT** catch exceptions silently without logging
- **MUST** log exceptions at appropriate levels before handling

**Logging**:
- **MUST** use appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **SHOULD** use structured logging with key-value pairs
- **MUST** redact PII and secrets from all log messages

**Code Style**:
- **MUST** format code with an automated formatter
- **MUST** organize imports in standard order (stdlib, third-party, local)
- **MUST** use descriptive names following conventions (snake_case for functions, PascalCase for classes)

## Testing Expectations

**When to Add Tests**:
- **MUST** write tests for all new functionality
- **MUST** add regression tests when fixing bugs
- **SHOULD** add tests when refactoring to prevent regressions

**Test Structure**:
- **MUST** follow existing test layout and organization in the repository
- **MUST** name tests descriptively: `test_<functionality>_<condition>_<expected_result>`
- **SHOULD** use fixtures for setup and teardown
- **SHOULD** mock external dependencies (databases, APIs, file systems) in unit tests
- **MUST** ensure tests are deterministic and repeatable

**Test Types**:
- **Unit tests**: Test individual functions or classes in isolation
- **Integration tests**: Test interactions between components
- **End-to-end tests**: Test complete user workflows

**Test Coverage**:
- **MUST** cover critical paths and edge cases
- **MUST** test error handling and boundary conditions
- **MUST NOT** change golden outputs or test assertions without explicit approval

## Documentation Expectations

**When to Update Documentation**:
- **MUST** update docstrings when changing function signatures or behavior
- **MUST** update README.md when adding new features or changing setup procedures
- **SHOULD** update PROJECT_OVERVIEW.md when architectural decisions or constraints change
- **SHOULD** update runbooks or operational documentation when deployment or monitoring changes

**Documentation Quality**:
- **MUST** include docstrings for all public modules, classes, and functions
- **MUST** document parameters, return values, and raised exceptions
- **SHOULD** provide usage examples for complex or non-obvious functionality
- **MUST** keep inline comments concise and focused on "why" rather than "what"

## Suggested Workflows

### Feature Implementation Workflow

1. **Plan**: Review PROJECT_OVERVIEW.md for domain context, NFRs, and constraints
2. **Design**: Identify affected modules, APIs, and data models; confirm design before coding
3. **Implement**: Write minimal code following repository patterns and PYTHON_CODING_STANDARDS.md
4. **Test**: Add unit and integration tests; verify edge cases and error paths
5. **Document**: Update docstrings, README, and PROJECT_OVERVIEW.md as needed
6. **Verify**: Run formatter, linter, type checker, and test suite

### Bugfix Workflow

1. **Reproduce**: Create a minimal test case that demonstrates the bug
2. **Root cause**: Trace the issue to its source; understand why it occurs
3. **Fix**: Implement the minimal fix that addresses the root cause
4. **Regression test**: Add a test that fails before the fix and passes after
5. **Verify**: Ensure no other tests break; check for similar issues elsewhere

### Refactoring Workflow

1. **Safety net**: Ensure comprehensive test coverage exists before refactoring
2. **Incremental changes**: Make small, verifiable changes rather than large rewrites
3. **Test continuously**: Run tests after each incremental change
4. **Preserve behavior**: Ensure external behavior remains unchanged
5. **Document intent**: Update comments and documentation to reflect new structure

## Response Style (When Returning an Answer)

**MUST** structure responses as follows:

1. **Brief plan**: Summarize what will be done in 1-3 sentences
2. **Explicit assumptions**: List any assumptions made due to missing information
3. **Implementation**: Provide code changes with clear explanations
4. **Change summary**: Highlight key modifications and their rationale
5. **Verification steps**: Describe how to verify the changes (e.g., "run the formatter", "execute tests", "check type hints")

**Guidelines**:
- **SHOULD** be concise but complete—avoid unnecessary verbosity
- **MUST** explain non-obvious design decisions
- **SHOULD** highlight potential risks or trade-offs
- **MAY** suggest alternatives when appropriate
- **MUST NOT** use emojis or overly casual language

## Questions to Ask When Ambiguous

When information is missing or unclear, ask a small number of targeted questions (3-5 maximum). Prioritize questions based on PROJECT_OVERVIEW.md structure:

**Domain & Use Cases**:
1. Who are the primary users of this feature?
2. What is the expected user workflow or interaction pattern?
3. Are there specific business rules or constraints that apply?

**Non-Functional Requirements**:
4. What are the performance expectations (latency, throughput, scale)?
5. What is the acceptable error rate or reliability target?
6. Are there specific availability or uptime requirements?

**Data & Privacy**:
7. What is the data classification level (public, internal, confidential, restricted)?
8. Are there retention, deletion, or anonymization requirements?
9. Does this involve PII or sensitive user data?

**Integrations & Dependencies**:
10. What external systems or services does this interact with?
11. Are there API contracts or schemas that must be followed?
12. What are the failure modes for external dependencies?

**Deployment & Operations**:
13. In which environments will this run (dev, staging, production)?
14. Are there specific deployment constraints or rollout requirements?
15. How will this be monitored or debugged in production?

If no response is provided to questions, proceed with safe defaults and explicit assumptions.

## Do Not Do

**MUST NOT** perform any of the following without explicit approval:

- **Configuration**: Do not hardcode configuration values; use environment variables or config files
- **Secrets**: Do not commit or log secrets, credentials, or API keys
- **Security**: Do not weaken authentication, authorization, or input validation
- **Breaking changes**: Do not introduce backwards-incompatible changes without confirmation
- **Large rewrites**: Do not refactor or rewrite large sections of code without approval
- **Dependencies**: Do not add new dependencies without justification and confirmation
- **Data deletion**: Do not delete or modify production data
- **Test changes**: Do not remove or skip tests without justification
- **Golden outputs**: Do not change test assertions or expected outputs without review
- **Complexity**: Do not introduce unnecessary abstractions or over-engineering
- **External calls**: Do not add calls to external services without timeout and error handling
- **Logging PII**: Do not log sensitive user data without redaction
- **Cortex model names**: Do not invent or hardcode Cortex model names; always read from `PROJECT_OVERVIEW.md` / environment variables
- **`light_client/` modification**: Do not modify any file inside the `light_client/` folder; treat it as a read-only vendored library
- **LIGHTClient in services**: Do not import `LIGHTClient` directly in service or route files; all Cortex access must go through `src/integrations/cortex_client.py`
- **RAGAS without requirement**: Do not generate RAGAS evaluation files (`ragas_evaluation_service.py`, evaluation routes/handlers, RAGAS Pydantic models) unless the project's BRD, User Stories, or `PROJECT_OVERVIEW.md` explicitly require AI output evaluation
- **RAGAS metric names**: Do not hardcode RAGAS metric names in source files; always read from `RAGAS_DEFAULT_METRICS` env var / config; only use metrics from the documented valid set (`answer_correctness`, `answer_relevancy`, `semantic_similarity`, `context_entity_recall`, `context_precision`, `context_recall`, `context_utilization`, `faithfulness`)
- **MCP version mixing**: Default to FastMCP 2.x (`from fastmcp import FastMCP`, `pip install fastmcp`). Use FastMCP 1.x (`from mcp.server.fastmcp import FastMCP`, `pip install mcp`) only when the project explicitly pins 1.x. Never mix both in the same project.
- **MCP decorator mixing**: Do not place `@mcp.tool` / `@mcp.resource` / `@mcp.prompt` decorators in the same module as FastAPI `@router` decorators; keep MCP modules under `src/mcp_server/` and FastAPI modules under `src/api/routes/`
- **MCP tool-to-tool calls**: Do not call one `@mcp.tool` function from inside another tool; extract shared logic to the service layer (`src/services/`) so REST and MCP behave identically
- **MCP service-layer bypass**: Do not call `cortex_client`, `LIGHTClient`, or external integrations directly from MCP tools/resources/prompts; route all such calls through `src/services/`
- **MCP transport hardcoding**: Do not hardcode the MCP transport (`stdio` / `streamable-http` / `sse`) in source files; read from env / config (e.g., `MCP_TRANSPORT`) so the value matches `PROJECT_OVERVIEW.md`
- **Silent design-spec overrides**: Do not follow an existing code pattern over the design spec (`FEATURE_IMPLEMENTATION.md`, `PROJECT_OVERVIEW.md`, acceptance criteria) without explicitly calling out the conflict, naming both approaches, and asking the developer which to follow (see "Existing Code Override Justification Rule")

---

**Enforcement**: These instructions are mandatory for all AI-assisted code generation and modification in this repository. Non-compliance should be flagged and corrected before code review.
