# Feature Implementation Guide

## Purpose

This is your **primary development guide** for implementing features. It combines Technical task and subtasks, execution plan, API routes, service layer, business logic, data models, and integrations in ONE place. Use this document to build the features on generated skeleton.

**References:** This guide uses patterns from `PYTHON_CODING_STANDARDS.md` and context from `PROJECT_OVERVIEW.md`.

---

## Section-1: Technical Tasks/Subtasks

<!-- FILL: Break down user stories into technical tasks and subtasks, similar to JIRA board structure -->

### Task 1: {TASK_NAME}

**Related User Story:** {STORY_ID} - {STORY_TITLE}

**Task Description:** {DETAILED_TASK_DESCRIPTION}

**Priority:** {HIGH / MEDIUM / LOW}

**Estimated Effort:** {HOURS / STORY_POINTS}

**Dependencies:** {LIST_TASK_DEPENDENCIES}

**Subtasks:**

#### Subtask 1.1: {SUBTASK_NAME}

**Description:** {SUBTASK_DESCRIPTION}

**Technical Components Involved:**
- [ ] API Route (FastAPI): {ROUTE_PATH}
- [ ] Lambda Handler (AWS Lambda): {HANDLER_FILE}
- [ ] MCP Tool (FastMCP): {TOOL_NAME} in `src/mcp_server/tools/{module}.py` — model-invoked action
- [ ] MCP Resource (FastMCP): {URI_TEMPLATE} in `src/mcp_server/resources/{module}.py` — client-pulled data
- [ ] MCP Prompt (FastMCP): {PROMPT_NAME} in `src/mcp_server/prompts/{module}.py` — user-invoked template
- [ ] Service Layer: {SERVICE_NAME}
- [ ] Data Model: {MODEL_NAME}
- [ ] Integration: {INTEGRATION_NAME}
- [ ] Tests: {TEST_TYPE}

**Acceptance Criteria:**
- [ ] {CRITERIA_1}
- [ ] {CRITERIA_2}

**Implementation Notes:** {NOTES_OR_CONSIDERATIONS}

---

#### Subtask 1.2: {SUBTASK_NAME}

**Description:** {SUBTASK_DESCRIPTION}

**Technical Components Involved:**
- [ ] {COMPONENT_1}
- [ ] {COMPONENT_2}

**Acceptance Criteria:**
- [ ] {CRITERIA_1}
- [ ] {CRITERIA_2}

---

### Task 2: {TASK_NAME}

**Related User Story:** {STORY_ID} - {STORY_TITLE}

**Task Description:** {DETAILED_TASK_DESCRIPTION}

**Priority:** {HIGH / MEDIUM / LOW}

**Estimated Effort:** {HOURS / STORY_POINTS}

**Dependencies:** {LIST_TASK_DEPENDENCIES}

**Subtasks:**

#### Subtask 2.1: {SUBTASK_NAME}

**Description:** {SUBTASK_DESCRIPTION}

**Technical Components Involved:**
- [ ] {COMPONENT_1}
- [ ] {COMPONENT_2}

**Acceptance Criteria:**
- [ ] {CRITERIA_1}
- [ ] {CRITERIA_2}

---

### Task Summary

| Task ID | Task Name | Related Story | Priority | Estimated Effort | Status |
|---------|-----------|---------------|----------|------------------|--------|
| Task 1  | {NAME}    | {STORY_ID}    | {PRIORITY} | {EFFORT}       | {STATUS} |
| Task 2  | {NAME}    | {STORY_ID}    | {PRIORITY} | {EFFORT}       | {STATUS} |
| Task 3  | {NAME}    | {STORY_ID}    | {PRIORITY} | {EFFORT}       | {STATUS} |

---

## Section-2: Execution Plan

<!-- FILL: Provide detailed execution plan based on Section-1 tasks/subtasks with best possible approach -->

### Overview

**Sprint/Iteration:** {SPRINT_NUMBER}

**Duration:** {START_DATE} to {END_DATE}

**Team Members:** {LIST_TEAM_MEMBERS_AND_ROLES}

**Goals:** 
- {GOAL_1}
- {GOAL_2}
- {GOAL_3}

---

### Phase 1: {PHASE_NAME}

**Objective:** {PHASE_OBJECTIVE}

**Duration:** {ESTIMATED_DAYS}

**Tasks Included:** {TASK_IDS_FROM_SECTION_1}

#### Step-by-Step Execution

**Step 1: {STEP_NAME}**

**Action:** {DETAILED_ACTION_DESCRIPTION}

**Tasks/Subtasks Involved:** 
- Task {ID}: Subtask {ID} - {NAME}
- Task {ID}: Subtask {ID} - {NAME}

**Technical Approach:**
```
{DESCRIBE_TECHNICAL_APPROACH_OR_METHODOLOGY}
Example:
1. Set up database schema
2. Create SQLAlchemy models
3. Generate migration scripts
4. Test database connectivity
```

**Expected Deliverables:**
- {DELIVERABLE_1}
- {DELIVERABLE_2}

**Validation/Testing:**
- {TEST_APPROACH_1}
- {TEST_APPROACH_2}

**Risks & Mitigations:**
- Risk: {RISK_DESCRIPTION}
  - Mitigation: {MITIGATION_STRATEGY}

---

**Step 2: {STEP_NAME}**

**Action:** {DETAILED_ACTION_DESCRIPTION}

**Tasks/Subtasks Involved:** 
- Task {ID}: Subtask {ID} - {NAME}

**Technical Approach:**
```
{DESCRIBE_TECHNICAL_APPROACH}
```

**Expected Deliverables:**
- {DELIVERABLE_1}

**Validation/Testing:**
- {TEST_APPROACH}

---

### Phase 2: {PHASE_NAME}

**Objective:** {PHASE_OBJECTIVE}

**Duration:** {ESTIMATED_DAYS}

**Tasks Included:** {TASK_IDS_FROM_SECTION_1}

#### Step-by-Step Execution

**Step 1: {STEP_NAME}**

**Action:** {DETAILED_ACTION_DESCRIPTION}

**Tasks/Subtasks Involved:** 
- Task {ID}: Subtask {ID} - {NAME}

**Technical Approach:**
```
{DESCRIBE_TECHNICAL_APPROACH}
```

**Expected Deliverables:**
- {DELIVERABLE_1}

**Validation/Testing:**
- {TEST_APPROACH}

---

### Phase 3: {PHASE_NAME} (if applicable)

**Objective:** {PHASE_OBJECTIVE}

**Duration:** {ESTIMATED_DAYS}

**Tasks Included:** {TASK_IDS_FROM_SECTION_1}

---

### Integration & Testing Strategy

**Unit Testing:**
- {UNIT_TEST_APPROACH}
- Coverage Target: {PERCENTAGE}%

**Integration Testing:**
- {INTEGRATION_TEST_APPROACH}
- Test Scenarios: {LIST_KEY_SCENARIOS}

**End-to-End Testing:**
- {E2E_TEST_APPROACH}
- Critical User Flows: {LIST_FLOWS}

**Performance Testing:**
- {PERFORMANCE_TEST_APPROACH}
- Benchmarks: {LIST_BENCHMARKS}

---

### Deployment Strategy

**Environment Progression:**
1. Development → {DESCRIPTION}
2. Testing/QA → {DESCRIPTION}
3. Staging → {DESCRIPTION}
4. Production → {DESCRIPTION}

**Deployment Checklist:**
- [ ] Database migrations prepared and tested
- [ ] Environment variables configured
- [ ] API documentation updated
- [ ] Integration endpoints tested
- [ ] Security review completed
- [ ] Performance benchmarks met
- [ ] Rollback plan documented

---

### Monitoring & Success Metrics

**Key Performance Indicators (KPIs):**
- {KPI_1}: {TARGET_VALUE}
- {KPI_2}: {TARGET_VALUE}
- {KPI_3}: {TARGET_VALUE}

**Monitoring Approach:**
- {MONITORING_TOOL}: {WHAT_TO_MONITOR}
- Alert Thresholds: {DEFINE_THRESHOLDS}

**Success Criteria:**
- [ ] All acceptance criteria met
- [ ] Test coverage ≥ {PERCENTAGE}%
- [ ] Performance benchmarks achieved
- [ ] Zero critical bugs
- [ ] Documentation complete

---

### Risk Management

| Risk ID | Risk Description | Probability | Impact | Mitigation Strategy | Owner |
|---------|------------------|-------------|--------|---------------------|-------|
| R1      | {RISK}           | {H/M/L}     | {H/M/L}| {MITIGATION}        | {NAME}|
| R2      | {RISK}           | {H/M/L}     | {H/M/L}| {MITIGATION}        | {NAME}|
| R3      | {RISK}           | {H/M/L}     | {H/M/L}| {MITIGATION}        | {NAME}|

---

### Dependencies & Prerequisites

**Technical Dependencies:**
- {DEPENDENCY_1}: {VERSION / STATUS}
- {DEPENDENCY_2}: {VERSION / STATUS}

**External Dependencies:**
- {EXTERNAL_SYSTEM_1}: {STATUS / AVAILABILITY}
- {EXTERNAL_SYSTEM_2}: {STATUS / AVAILABILITY}

**Team Dependencies:**
- {DEPENDENCY_ON_OTHER_TEAM}: {DESCRIPTION}

**Prerequisite Tasks:**
- [ ] {PREREQUISITE_1}
- [ ] {PREREQUISITE_2}

---

### Communication & Reporting

**Daily Standups:**
- Time: {TIME}
- Focus: {FOCUS_AREAS}

**Progress Reports:**
- Frequency: {DAILY / WEEKLY}
- Format: {FORMAT}
- Recipients: {STAKEHOLDERS}

**Issue Escalation:**
- Blocker: {ESCALATION_PATH}
- Timeline: {RESPONSE_TIME}

---

## Common/Shared Components

<!-- FILL: Document components that are used across MULTIPLE features/stories -->

### Shared Data Models

**Entity: {SHARED_ENTITY_NAME}**
<!-- FILL: Define data models used by multiple features -->

**Description:** {ENTITY_DESCRIPTION}

**Database Table:** `{TABLE_NAME}`

| Field      | Type         | Constraints   | Description          |
|------------|--------------|---------------|----------------------|
| id         | UUID         | PK, NOT NULL  | Primary key          |
| {FIELD_1}  | {TYPE}       | {CONSTRAINTS} | {DESCRIPTION}        |
| created_at | TIMESTAMP    | NOT NULL      | Record creation time |
| updated_at | TIMESTAMP    | NOT NULL      | Last update time     |

**Relationships:**
- {RELATIONSHIP_DESCRIPTION}

---

### Shared Integrations

**Integration: {INTEGRATION_NAME}**
<!-- FILL: Define external integrations used by multiple features -->

**Service:** {SERVICE_NAME}

**Purpose:** {PURPOSE}

**Base URL:** `{BASE_URL}` or Config Variable: `{CONFIG_VAR_NAME}`

**Authentication Method:** {API_KEY / OAUTH2 / BASIC_AUTH / OTHER}

**Common Endpoints:**

| Method | Endpoint        | Purpose      |
|--------|-----------------|--------------|
| GET    | `/api/resource` | {PURPOSE}    |
| POST   | `/api/resource` | {PURPOSE}    |

---

### Common Business Rules

**Rule: {COMMON_RULE_NAME}**
<!-- FILL: Define business rules that apply to multiple features -->

**Description:** {RULE_DESCRIPTION}

**Applies To:** {LIST_OF_FEATURES_OR_ENTITIES}

**Trigger:** {TRIGGER_CONDITION}

**Action:** {ACTION_TO_TAKE}

---

## Feature 1: {STORY_TITLE}

<!-- FILL: Complete all sections for this feature -->

### User Story

**Story ID:** {JIRA_ID}

**As a** {USER_ROLE}  
**I want to** {ACTION}  
**So that** {BENEFIT}

**Acceptance Criteria:**
- [ ] {CRITERIA_1}
- [ ] {CRITERIA_2}
- [ ] {CRITERIA_3}

**Dependencies:** {LIST_ANY_DEPENDENCIES}

---

### API Endpoints

**Endpoint: {ENDPOINT_NAME}**

| Field         | Value                          |
|---------------|--------------------------------|
| Method        | {GET \| POST \| PUT \| DELETE} |
| Path          | `/api/v1/{resource}`           |
| Auth Required | Yes / No                       |
| Description   | {DESCRIPTION}                  |

**Request Fields:**

| Field      | Type    | Required | Description   | Validation Rules     |
|------------|---------|----------|---------------|----------------------|
| {FIELD_1}  | {TYPE}  | Yes/No   | {DESCRIPTION} | {RULES}              |
| {FIELD_2}  | {TYPE}  | Yes/No   | {DESCRIPTION} | {RULES}              |

**Response Fields:**

| Field      | Type    | Description   |
|------------|---------|---------------|
| {FIELD_1}  | {TYPE}  | {DESCRIPTION} |
| {FIELD_2}  | {TYPE}  | {DESCRIPTION} |

**Expected Status Codes:** 200 (Success), 400 (Bad Request), 401 (Unauthorized), 404 (Not Found), 500 (Server Error)

---

### MCP Component Decision (fill only when `Deployment Target` includes FastMCP)

For each capability this feature exposes, classify it as a tool, resource, or prompt using the matrix below. Any capability that calls a service-layer function should be exposed once per active transport — once as a FastAPI route or Lambda handler (when applicable) and once as the chosen MCP component type.

| If the capability is... | Use | Example |
|---|---|---|
| An action the AI model should call (mutate state, run a query, hit an API, call Cortex) | `@mcp.tool` | `ask_cortex(prompt)`, `search_regulations(query)`, `submit_evaluation(...)` |
| Read-only data the client pulls by URI (config, document content, job status, reference data) | `@mcp.resource("uri://...")` | `regulation://{regulation_id}`, `config://current`, `job-status://{job_id}` |
| A reusable prompt template the user picks from a menu (parameterized prompts shown in the client UI) | `@mcp.prompt` | `summarize_regulation(reg_id)`, `compare_documents(doc_a, doc_b)` |

**Components for this feature:**

| Capability | MCP Type | Name / URI | Service-layer function | Notes |
|------------|----------|------------|-----------------------|-------|
| {CAPABILITY_1} | {tool \| resource \| prompt} | {NAME_OR_URI} | {SERVICE_FUNCTION} | {NOTES} |
| {CAPABILITY_2} | {tool \| resource \| prompt} | {NAME_OR_URI} | {SERVICE_FUNCTION} | {NOTES} |

**Rules** (enforced by `copilot-instructions.md` "Do Not Do"):
- MCP components must call `src/services/`, never `cortex_client` or external integrations directly
- One `@mcp.tool` must NOT call another `@mcp.tool`; share logic in the service layer
- Keep MCP modules under `src/mcp_server/`; do not place them next to FastAPI routes

---

### Data Models (Feature-Specific)

**Entity: {ENTITY_NAME}**
<!-- FILL: Define data models specific to THIS feature only -->

**Description:** {ENTITY_DESCRIPTION}

**Database Table:** `{TABLE_NAME}`

| Field      | Type         | Constraints   | Description          |
|------------|--------------|---------------|----------------------|
| id         | UUID         | PK, NOT NULL  | Primary key          |
| {FIELD_1}  | {TYPE}       | {CONSTRAINTS} | {DESCRIPTION}        |
| {FIELD_2}  | {TYPE}       | {CONSTRAINTS} | {DESCRIPTION}        |
| created_at | TIMESTAMP    | NOT NULL      | Record creation time |
| updated_at | TIMESTAMP    | NOT NULL      | Last update time     |
| created_by | VARCHAR(255) | NOT NULL      | User who created     |

**Relationships:**
- `{ENTITY_NAME}` has many `{RELATED_ENTITY}`
- `{ENTITY_NAME}` belongs to `{PARENT_ENTITY}`

**Indexes:**
- `idx_{table}_{field}` on `{field}`

---

### Business Logic Rules

**Rule 1: {RULE_NAME}**

**Description:** {RULE_DESCRIPTION}

**Trigger:** {TRIGGER_CONDITION}

**Action:** {ACTION_TO_TAKE}

**Validation Requirements:** {LIST_VALIDATION_REQUIREMENTS}

**Error Handling:** {HOW_TO_HANDLE_FAILURES}

---

**Rule 2: {RULE_NAME}**
<!-- FILL: Add more rules specific to this feature -->

---

### Integrations (Feature-Specific)

**Integration: {INTEGRATION_NAME}**
<!-- FILL: Only if this feature needs a SPECIFIC integration. Skip if using shared integrations -->

**Service:** {SERVICE_NAME}

**Purpose:** {PURPOSE}

**Base URL:** `{BASE_URL}` or Config Variable: `{CONFIG_VAR_NAME}`

**Authentication Method:** {API_KEY / OAUTH2 / BASIC_AUTH / OTHER}

**Required Configuration:**
- {CONFIG_1}: {DESCRIPTION}
- {CONFIG_2}: {DESCRIPTION}

**Endpoints Used:**

| Method | Endpoint        | Purpose      | When to Call          |
|--------|-----------------|--------------|----------------------|
| GET    | `/api/resource` | {PURPOSE}    | {TRIGGER_CONDITION}  |
| POST   | `/api/resource` | {PURPOSE}    | {TRIGGER_CONDITION}  |

**Data Mapping:**
- Our `{FIELD}` → External `{FIELD}`
- External `{FIELD}` → Our `{FIELD}`

**Error Handling:**
- Retry logic: {YES/NO}
- Timeout: {SECONDS}
- Fallback behavior: {DESCRIPTION}

---

### Workflow

**Process Flow:**

```
{DESCRIBE_THE_WORKFLOW_IN_TEXT_OR_DIAGRAM}

Example:
User Request → Validate Input → Check Business Rules → Call External API
     ↓              ↓                    ↓                      ↓
  (if valid)   (if passes)         (if success)          (store data)
                                                               ↓
                                                        Return Response
```

**Steps:**
1. {STEP_1_DESCRIPTION}
2. {STEP_2_DESCRIPTION}
3. {STEP_3_DESCRIPTION}
4. {STEP_4_DESCRIPTION}

---

### Testing Requirements

**Test Scenarios:**

| Scenario                     | Type        | Description                        | Expected Result          | Priority |
|------------------------------|-------------|------------------------------------|--------------------------|----------|
| {SCENARIO_1}                 | Unit        | {DESCRIPTION}                      | {EXPECTED_RESULT}        | High     |
| {SCENARIO_2}                 | Integration | {DESCRIPTION}                      | {EXPECTED_RESULT}        | High     |
| Invalid input handling       | Unit        | Test with missing/invalid fields   | 400 Bad Request          | High     |
| Authentication failure       | Integration | Request without valid token        | 401 Unauthorized         | High     |
| {EDGE_CASE_1}                | Unit        | {DESCRIPTION}                      | {EXPECTED_RESULT}        | Medium   |

**Business Logic Tests:**
- {BUSINESS_RULE_1}: {TEST_DESCRIPTION}
- {BUSINESS_RULE_2}: {TEST_DESCRIPTION}

---

### Implementation Checklist

**Backend Components:**
- [ ] API routes implemented (FastAPI) OR Lambda handlers implemented (AWS Lambda)
- [ ] Service layer with business logic (framework-agnostic)
- [ ] Request/Response models (Pydantic)
- [ ] Database models/entities (if needed)
- [ ] Integration clients (if needed)
- [ ] Deployment artifacts updated (`deployment/fastapi/`, `deployment/lambda/`, or `deployment/mcp/`, per target)

**FastMCP Components (only when target includes FastMCP):**
- [ ] `src/mcp_server/server.py` registers `FastMCP(name=MCP_SERVER_NAME)` and starts the transport read from `MCP_TRANSPORT`
- [ ] Tools / resources / prompts implemented under `src/mcp_server/{tools,resources,prompts}/` per the MCP Component Decision matrix above
- [ ] Each MCP component calls `src/services/` — never `cortex_client` / `LIGHTClient` / external integrations directly
- [ ] Type hints + one-line docstrings on every `@mcp.tool` / `@mcp.resource` / `@mcp.prompt` (FastMCP uses these for the model-facing schema)
- [ ] In-memory tests using `fastmcp.Client` (or `mcp.client` for 1.x) under `tests/mcp/`

**Testing:**
- [ ] Unit tests (service layer)
- [ ] Integration tests (API routes or Lambda handlers)
- [ ] Business logic validation tests

**Documentation & Deployment:**
- [ ] API documentation updated
- [ ] Code reviewed
- [ ] Deployed to dev/test environment

---

## Feature 2: {STORY_TITLE}

<!-- FILL: Complete all sections for this feature -->

### User Story

**Story ID:** {JIRA_ID}

**As a** {USER_ROLE}  
**I want to** {ACTION}  
**So that** {BENEFIT}

**Acceptance Criteria:**
- [ ] {CRITERIA_1}
- [ ] {CRITERIA_2}
- [ ] {CRITERIA_3}

**Dependencies:** {LIST_ANY_DEPENDENCIES}

---

### API Endpoints

<!-- NOTE: The deployment target (FastAPI or AWS Lambda) determines how these endpoints are implemented.
     - FastAPI: Each endpoint becomes a route in `src/api/routes/<feature>.py`
     - AWS Lambda: Each endpoint becomes a handler in `src/lambda_handlers/<feature>_handler.py`
     Service layer logic under `src/services/` MUST remain framework-agnostic and shared by both targets. -->

**Endpoint: {ENDPOINT_NAME}**

| Field         | Value                          |
|---------------|--------------------------------|
| Method        | {GET \| POST \| PUT \| DELETE} |
| Path          | `/api/v1/{resource}`           |
| Auth Required | Yes / No                       |
| Description   | {DESCRIPTION}                  |
| FastAPI Route | `src/api/routes/{resource}.py` (when target = FastAPI) |
| Lambda Handler | `src/lambda_handlers/{resource}_handler.py` (when target = AWS Lambda) |
| FastMCP Component | `src/mcp_server/{tools\|resources\|prompts}/{resource}.py` (when target includes FastMCP — see MCP Component Decision below) |

**Request Fields:**

| Field      | Type    | Required | Description   | Validation Rules     |
|------------|---------|----------|---------------|----------------------|
| {FIELD_1}  | {TYPE}  | Yes/No   | {DESCRIPTION} | {RULES}              |
| {FIELD_2}  | {TYPE}  | Yes/No   | {DESCRIPTION} | {RULES}              |

**Response Fields:**

| Field      | Type    | Description   |
|------------|---------|---------------|
| {FIELD_1}  | {TYPE}  | {DESCRIPTION} |
| {FIELD_2}  | {TYPE}  | {DESCRIPTION} |

**Expected Status Codes:** 200 (Success), 400 (Bad Request), 401 (Unauthorized), 404 (Not Found), 500 (Server Error)

---

### Data Models (Feature-Specific)

**Entity: {ENTITY_NAME}**

**Description:** {ENTITY_DESCRIPTION}

**Database Table:** `{TABLE_NAME}`

| Field      | Type         | Constraints   | Description          |
|------------|--------------|---------------|----------------------|
| id         | UUID         | PK, NOT NULL  | Primary key          |
| {FIELD_1}  | {TYPE}       | {CONSTRAINTS} | {DESCRIPTION}        |
| created_at | TIMESTAMP    | NOT NULL      | Record creation time |
| updated_at | TIMESTAMP    | NOT NULL      | Last update time     |

**Relationships:**
- {RELATIONSHIP_DESCRIPTION}

---

### Business Logic Rules

**Rule: {RULE_NAME}**

**Description:** {RULE_DESCRIPTION}

**Trigger:** {TRIGGER_CONDITION}

**Action:** {ACTION_TO_TAKE}

**Validation Requirements:** {LIST_VALIDATION_REQUIREMENTS}

---

### Integrations (Feature-Specific)

<!-- FILL: Only if this feature needs a specific integration, otherwise reference shared integrations -->

**Uses Shared Integration:** {INTEGRATION_NAME} (see Common/Shared Components)

---

### Workflow

**Process Flow:**

```
{DESCRIBE_THE_WORKFLOW}
```

**Steps:**
1. {STEP_1_DESCRIPTION}
2. {STEP_2_DESCRIPTION}

---

### Testing Requirements

**Test Scenarios:**

| Scenario           | Type | Description       | Expected Result   | Priority |
|--------------------|------|-------------------|-------------------|----------|
| {SCENARIO_1}       | Unit | {DESCRIPTION}     | {EXPECTED_RESULT} | High     |

---

### Implementation Checklist

**Backend Components:**
- [ ] API routes implemented (FastAPI) OR Lambda handlers implemented (AWS Lambda)
- [ ] Service layer with business logic (framework-agnostic)
- [ ] Request/Response models (Pydantic)

**FastMCP Components (only when target includes FastMCP):**
- [ ] MCP tool / resource / prompt implemented under `src/mcp_server/`, calling `src/services/` (see Feature 1 for the full checklist)

**Testing:**
- [ ] Unit tests
- [ ] Integration tests

**Documentation & Deployment:**
- [ ] API documentation updated
- [ ] Code reviewed
- [ ] Deployed

---

## Feature 3: {STORY_TITLE}

<!-- FILL: Duplicate Feature 2 structure for additional features -->

---

## Implementation Notes & Decisions

<!-- FILL: Document any architectural decisions or important notes made during implementation -->

| Feature/Story | Decision   | Rationale   | Impact                      |
|---------------|------------|-------------|-----------------------------|
| {JIRA_ID}     | {DECISION} | {RATIONALE} | {WHICH_COMPONENTS_IMPACTED} |

---

## Dependencies Between Features (Optional)

<!-- FILL: Document if Feature X must be completed before Feature Y -->

| Feature       | Depends On    | Reason                         |
|---------------|---------------|--------------------------------|
| {FEATURE_2}   | {FEATURE_1}   | {REASON_FOR_DEPENDENCY}        |
| {FEATURE_3}   | {FEATURE_1,2} | {REASON_FOR_DEPENDENCY}        |