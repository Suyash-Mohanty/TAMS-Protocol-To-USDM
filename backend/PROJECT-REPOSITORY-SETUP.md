# Project Repository Setup

## Purpose

This document serves as the blueprint for generating a complete backend project structure. It supports **two deployment targets** — a long‑running **FastAPI** service and a serverless **AWS Lambda** function — and dynamically adjusts the scaffolding based on the user's choice.

**References:** This guide uses information from `PROJECT_OVERVIEW.md` for project-specific configuration.

## Integration with PROJECT_OVERVIEW.md

This setup automatically reads from `PROJECT_OVERVIEW.md`:
- **Tech Stack Decisions** → Determines dependencies and configuration
- **Deployment Target** → Determines which runtime/scaffolding to generate (`FastAPI`, `AWS Lambda`)
- **LLM Provider** → Determines whether Cortex integration files are generated (see "Cortex Integration" section below)
- **Features List** → Generates corresponding API endpoints / Lambda handlers
- **Database Schema** → Creates SQLAlchemy models
- **Cloud Provider** → Includes provider-specific SDK and configuration
- **Business Requirements** → Shapes the API structure and data models

---

## Deployment Target Decision

Before generating the skeleton, **MUST** read the **Deployment Target** field from `PROJECT_OVERVIEW.md` (Section 2 — Tech Stack Decisions). Use the following decision logic:

| Value in `PROJECT_OVERVIEW.md` | Generate FastAPI artifacts | Generate Lambda artifacts |
|--------------------------------|----------------------------|---------------------------|
| `FastAPI`                      |     Yes                    |    No                     |
| `AWS Lambda`                   |     No                     |    Yes                    |
| _missing / unclear_            | STOP and ask the user      | STOP and ask the user     |

**Rules:**
- **MUST NOT** generate Lambda artifacts when the target is `FastAPI`, and vice versa.
- **MUST** keep `src/services/`, `src/models/`, `src/database/`, `src/integrations/`, `src/core/`, `src/utils/`, and `src/logger/` runtime‑agnostic so the same modules are reusable by either entry point.
- For `AWS Lambda`, the handler MUST be a pure Python function (`def lambda_handler(event, context): ...`) and MUST NOT depend on FastAPI, Starlette, Mangum, or any ASGI adapter.
- For `FastAPI`, the entry point is `src/main.py` (FastAPI app) + `src/server.py` (uvicorn runner).

---

Use the configurations and specifications from `PROJECT_OVERVIEW.md`. Create all folders, files, and implement basic routes / handlers for all features. The base project structure (always generated, regardless of deployment target) is:

```
{PROJECT_NAME}/
│
├── src/
│   ├── __init__.py
│   │
│   ├── api/                          # Generated when target = FastAPI
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── health.py
│   │
│   ├── lambda_handlers/              # Generated when target = AWS Lambda
│   │   ├── __init__.py
│   │   ├── health_handler.py
│   │   └── <feature>_handler.py      # one per feature/endpoint
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py
│   │   └── responses.py
│   │
│   ├── services/                     # Framework-agnostic business logic (shared)
│   │   └── __init__.py
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   └── repositories/
│   │       └── __init__.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── exceptions.py
│   │
│   ├── middleware/                   # Generated when target = FastAPI
│   │   └── __init__.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   └── lambda_response.py        # Generated when target = AWS Lambda
│   │
│   ├── logger/
│   │   ├── __init__.py
│   │   └── config.py
│   │
│   └── integrations/
│       └── __init__.py
│
├── src/main.py                       # Generated when target = FastAPI
├── src/server.py                     # Generated when target = FastAPI
│
├── deployment/                       # Deployment artifacts (target-specific)
│   ├── fastapi/                      # Generated when target = FastAPI
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   └── README.md
│   └── lambda/                       # Generated when target = AWS Lambda
│       ├── template.yaml             # AWS SAM template
│       ├── serverless.yml            # Serverless Framework config
│       ├── samconfig.toml            # Optional SAM CLI config
│       ├── build.sh                  # Packaging script (zip layer + function)
│       └── README.md
│
├── scripts/
│   └── __init__.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

### Target‑Specific File Generation Matrix

| Path / File                          | FastAPI | AWS Lambda |
|--------------------------------------|:-------:|:----------:|
| `src/main.py`, `src/server.py`       |   ✅    |     ❌     |
| `src/api/routes/*.py`                |   ✅    |     ❌     |
| `src/middleware/`                    |   ✅    |     ❌     |
| `src/lambda_handlers/*.py`           |   ❌    |     ✅     |
| `src/utils/lambda_response.py`       |   ❌    |     ✅     |
| `deployment/fastapi/Dockerfile`      |   ✅    |     ❌     |
| `deployment/fastapi/docker-compose`  |   ✅    |     ❌     |
| `deployment/lambda/template.yaml`    |   ❌    |     ✅     |
| `deployment/lambda/serverless.yml`   |   ❌    |     ✅     |
| `deployment/lambda/build.sh`         |   ❌    |     ✅     |
| `requirements.txt`                   |   ✅    |     ✅     |
| `src/services/`, `src/models/`, `src/database/`, `src/core/`, `src/integrations/`, `src/logger/`, `src/utils/`, `scripts/` |   ✅    |     ✅     |

---

### Cortex LLM Integration File Matrix

> **Applies only when `LLM Provider: Cortex` is set in `PROJECT_OVERVIEW.md`.**
> When this condition is true, generate the following files **in addition to** the deployment-target-specific files above.
> See `cortex_implementation.md` for detailed content and templates.

| Path / File | FastAPI | AWS Lambda | Notes |
|-------------|:-------:|:----------:|-------|
| `light_client/` (folder — all files) | ✅ | ✅ | Copy as-is from framework; never modify |
| `src/integrations/cortex_client.py` | ✅ | ✅ | Cortex API wrapper; use Azure AD auth for FastAPI, AWS auth for Lambda |
| `src/core/config.py` (update) | ✅ | ✅ | Add `CORTEX_BASE`, `CORTEX_PRIMARY_MODEL`, `CORTEX_AUTH_ENV`, etc. |
| `src/core/exceptions.py` (update) | ✅ | ✅ | Add `LLMServiceError` |
| `src/services/<feature>_service.py` (update) | ✅ | ✅ | Call `cortex_client.call_model()` instead of direct LLM SDK |
| `requirements.txt` (update) | ✅ | ✅ | Add `requests`; add `boto3`/`botocore` for Lambda target only |
| `.env.example` (update) | ✅ | ✅ | Add `CORTEX_BASE`, `CORTEX_PRIMARY_MODEL`, `CORTEX_AUTH_ENV` entries |

---

### Cortex RAGAS Evaluation File Matrix

> **Applies only when `LLM Provider: Cortex` is set AND the project requires AI output evaluation** (BRD / User Stories mention evaluating model quality, answer correctness, model benchmarking, or RAG pipeline quality).
> When both conditions are true, generate the following files **in addition to** the Cortex integration files above.
> See the **RAGAS Evaluation Integration** section in `cortex_implementation.md` for detailed content and templates.
> If evaluation intent is ambiguous, **STOP and ask the user** before generating.

| Path / File | FastAPI | AWS Lambda | Notes |
|-------------|:-------:|:----------:|-------|
| `src/integrations/cortex_client.py` (update) | ✅ | ✅ | Add `evaluate_with_ragas()` and `evaluate_with_ragas_bulk()` functions |
| `src/services/ragas_evaluation_service.py` | ✅ | ✅ | Framework-agnostic RAGAS evaluation service |
| `src/models/requests.py` (update) | ✅ | ✅ | Add `EvaluationPair`, `BulkEvaluationRequest` Pydantic models |
| `src/models/responses.py` (update) | ✅ | ✅ | Add `SingleEvaluationResponse`, `BulkEvaluationResponse` Pydantic models |
| `src/api/routes/evaluation.py` | ✅ | ❌ | FastAPI RAGAS evaluation endpoints (GET /ragas, POST /ragas/bulk) |
| `src/lambda_handlers/evaluation_handler.py` | ❌ | ✅ | Lambda handler for single and bulk RAGAS evaluation |
| `src/core/config.py` (update) | ✅ | ✅ | Add `RAGAS_DEFAULT_METRICS`, `RAGAS_BATCH_SIZE`, `RAGAS_WORKFLOW_TIMEOUT` |
| `src/core/exceptions.py` (update) | ✅ | ✅ | Add `RAGASEvaluationError` |
| `deployment/lambda/template.yaml` (update) | ❌ | ✅ | Register `EvaluationFunction` with GET and POST events |
| `deployment/lambda/serverless.yml` (update) | ❌ | ✅ | Register evaluation function and events |
| `.env.example` (update) | ✅ | ✅ | Add `RAGAS_DEFAULT_METRICS`, `RAGAS_BATCH_SIZE`, `RAGAS_WORKFLOW_TIMEOUT` |

The automation will create:
- Complete folder structure for a professional Python backend project (deployment-target aware).
- For **FastAPI** target: FastAPI application (`src/main.py`), uvicorn runner (`src/server.py`), routers under `src/api/routes/`, middleware, and a container-based deployment under `deployment/fastapi/`.
- For **AWS Lambda** target: standalone Python Lambda handlers under `src/lambda_handlers/` (one per endpoint/feature), a shared `src/utils/lambda_response.py` helper for building API Gateway responses, and serverless deployment artifacts (`template.yaml`, `serverless.yml`, `build.sh`) under `deployment/lambda/`.
- Configuration files (`.env.example`, `.gitignore`).
- Database models based on your schema.
- Utility modules (logging, helpers, authentication, security).
- `requirements.txt` with dependencies appropriate for the chosen deployment target (FastAPI + uvicorn for FastAPI; `boto3` + lightweight deps for Lambda — no FastAPI/uvicorn).

## Output

A fully functional skeleton application that:
- For **FastAPI**: runs immediately with `uvicorn src.main:app --reload` (or `python -m src.server`).
- For **AWS Lambda**: can be invoked locally with `sam local invoke <FunctionName>` or `serverless invoke local -f <function>`, and deployed with `sam deploy --guided` or `serverless deploy`.
- Includes all integrations specified in `PROJECT_OVERVIEW.md`.
- Contains placeholder implementations for all features.
- Is ready for development and customization.
- Follows Python and AWS best practices.

---

## Generated Files Content

### A. Common (always generated)

#### A.1 `requirements.txt`

Auto-generated based on:
- Database drivers (per selected database)
- Authentication libraries (if specified)
- Cloud SDK (per cloud provider; `boto3` for AWS)
- Other integrations from `PROJECT_OVERVIEW.md`
- **FastAPI target only:** `fastapi`, `uvicorn[standard]`, `pydantic`
- **AWS Lambda target only:** `pydantic` (for model validation), `boto3` (already provided by Lambda runtime — pin only if a newer version is required)

#### A.2 `src/core/config.py`

Environment-based configuration with:
- Database connection strings
- API keys and secrets (loaded from env / AWS Secrets Manager / SSM)
- Cloud service configurations
- Application settings

#### A.3 `src/services/`

Framework‑agnostic business logic. **MUST** be importable and callable from both FastAPI route handlers and Lambda handler functions without modification.

---

### B. FastAPI Target Files (generated when target = `FastAPI`)

#### B.1 `src/main.py` — FastAPI Application Entry Point

Includes:
- FastAPI app initialization
- CORS middleware configuration
- Exception handlers
- Health check endpoint
- All API routers from features in `PROJECT_OVERVIEW.md`
- Startup/shutdown events for database connections

#### B.2 `src/server.py`

Uvicorn runner that loads `src.main:app`, reads host/port from `src/core/config.py`, and supports `--reload` in development.

#### B.3 Sample Routes

For each feature in `PROJECT_OVERVIEW.md`:
- `GET    /health`
- `GET    /api/v1/{feature}` — list resources
- `POST   /api/v1/{feature}` — create resource
- `GET    /api/v1/{feature}/{id}` — get by ID
- `PUT    /api/v1/{feature}/{id}` — update
- `DELETE /api/v1/{feature}/{id}` — delete

#### B.4 `deployment/fastapi/Dockerfile`

Multi-stage Python image (slim base), installs `requirements.txt`, copies `src/`, exposes the configured port, and runs `uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}`.

#### B.5 `deployment/fastapi/docker-compose.yml`

Local development compose file wiring the API container to a database container (per `PROJECT_OVERVIEW.md`), with `.env` file mounted.

---

### C. AWS Lambda Target Files (generated when target = `AWS Lambda`)

#### C.1 `src/lambda_handlers/<feature>_handler.py` — Pure Lambda Handlers

**Rules:**
- **MUST** define `def lambda_handler(event, context):` as the entry point.
- **MUST NOT** import `fastapi`, `starlette`, or `mangum`.
- **MUST** parse and validate inputs from `event` (API Gateway / Function URL / EventBridge / SQS shape, per the trigger).
- **MUST** delegate business logic to `src/services/`.
- **MUST** return a response built via `src/utils/lambda_response.py` (correct `statusCode`, `headers`, JSON-serialized `body`).
- **MUST** catch domain exceptions from `src/core/exceptions.py` and map them to appropriate HTTP status codes.

Skeleton example (illustrative — actual code is generated):

```python
"""Health check Lambda handler."""
import json
import logging
from src.utils.lambda_response import build_response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """Pure AWS Lambda handler — no FastAPI dependency."""
    logger.info("health check invoked", extra={"request_id": context.aws_request_id})
    return build_response(200, {"status": "ok"})
```

One handler file is generated per endpoint/feature defined in `PROJECT_OVERVIEW.md`.

#### C.2 `src/utils/lambda_response.py`

Shared helper to build API Gateway proxy responses (status code, CORS headers, JSON body, error envelope).

#### C.3 `deployment/lambda/template.yaml` — AWS SAM

- Defines one `AWS::Serverless::Function` per handler in `src/lambda_handlers/`.
- `Runtime: python3.11`, `Handler: src.lambda_handlers.<feature>_handler.lambda_handler`.
- API Gateway HTTP API events wired to each function based on the routes from `PROJECT_OVERVIEW.md`.
- IAM policies scoped per function (least privilege) for required AWS services (S3, Secrets Manager, SSM, Bedrock, etc.).
- Environment variables sourced from SSM Parameter Store / Secrets Manager.

#### C.4 `deployment/lambda/serverless.yml` — Serverless Framework

Equivalent definition to `template.yaml` for teams using the Serverless Framework instead of SAM. Both are generated so the project can pick whichever tool the team prefers (or delete the unused one).

#### C.5 `deployment/lambda/build.sh`

Packaging script that:
1. Creates a clean `build/` directory.
2. Installs `requirements.txt` into `build/python/` for a Lambda layer.
3. Copies `src/` into the function package.
4. Produces a deployable zip (or relies on `sam build` / `serverless package`).

#### C.6 `deployment/lambda/README.md`

Quick commands:
```
# AWS SAM
sam build
sam local invoke HealthFunction
sam deploy --guided

# Serverless Framework
serverless package
serverless invoke local -f health
serverless deploy
```

---

## Checklist:
- ✅ Read **Deployment Target** from `PROJECT_OVERVIEW.md` and apply the Target‑Specific File Generation Matrix
- ✅ Read **LLM Provider** from `PROJECT_OVERVIEW.md`; if `Cortex`, apply the Cortex LLM Integration File Matrix and follow `cortex_implementation.md`
- ✅ Check project documents (BRD, UserStories) for AI evaluation requirements; if found AND LLM Provider is Cortex, apply the Cortex RAGAS Evaluation File Matrix
- ✅ Root Structure creation
- ✅ Source Directory creation
- ✅ Scripts Directory creation
- ✅ `__init__.py` Files creation
- ✅ Core Application Files creation (FastAPI `main.py`/`server.py` or Lambda handlers, per target)
- ✅ Configuration Module creation
- ✅ Custom Exceptions creation
- ✅ Logger Configuration creation
- ✅ Sample Request/Response Models creation
- ✅ `deployment/fastapi/` artifacts (Dockerfile, docker-compose) — when target includes FastAPI
- ✅ `deployment/lambda/` artifacts (`template.yaml`, `serverless.yml`, `build.sh`) — when target includes AWS Lambda
- ✅ `src/utils/lambda_response.py` — when target includes AWS Lambda
- ✅ Configuration Files creation (`requirements.txt` tailored to target, `.env.example`, `.gitignore`)
- ✅ `light_client/` folder present at project root — when LLM Provider is Cortex
- ✅ `src/integrations/cortex_client.py` created with correct auth method — when LLM Provider is Cortex
- ✅ `src/services/ragas_evaluation_service.py` created — when LLM Provider is Cortex AND project requires AI output evaluation
- ✅ RAGAS evaluation endpoints/handlers created and registered — when LLM Provider is Cortex AND project requires AI output evaluation
