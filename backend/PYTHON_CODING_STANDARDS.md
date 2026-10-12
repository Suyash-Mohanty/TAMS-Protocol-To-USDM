# Python Coding Standards

## Purpose and Scope

This document defines organizational Python coding standards and best practices applicable to all Python projects, regardless of domain or framework. These standards ensure consistency, maintainability, security, and quality across the Python codebase.

**Applicability**: All Python code written for production, internal tooling, APIs, data pipelines, CLIs, web applications, and automation scripts.

## Guiding Principles

- **Readability**: Code is read far more often than written. Optimize for clarity.
- **Consistency**: Uniform style and patterns reduce cognitive load.
- **Maintainability**: Code should be easy to understand, modify, and extend.
- **Security**: Security must be considered at every layer.
- **Testability**: Code should be designed to be easily testable.

## Python Version and Compatibility

- **MUST** use Python 3.11 or later for all new projects.
- **SHOULD** target the latest stable Python version for new development.
- **MUST** declare the minimum supported Python version in project metadata.
- **SHOULD** avoid deprecated features and plan migration paths when deprecations are announced.
- **MAY** support multiple Python versions if required by deployment constraints.

## Style Guide and Linter

- **Style Guide:** [PEP 8](https://peps.python.org/pep-0008/)
- **Linter:** Pylint

All Python code must conform to PEP 8 standards and pass Pylint checks.

## Style and Formatting

- **MUST** adhere to PEP 8 as the baseline style guide.
- **MUST** use a code formatter (e.g., Black, Ruff formatter) and run it on all code.
- **MUST** configure the formatter to run automatically in CI/CD pipelines.
- **SHOULD** use a line length of 88-100 characters.
- **MUST** organize imports in the following order, separated by blank lines:
  1. Standard library imports
  2. Third-party library imports
  3. Local application/library imports
- **SHOULD** use an import sorter (e.g., isort) to enforce ordering.
- **SHOULD** use trailing commas in multi-line data structures.
- **SHOULD** use double quotes for strings unless single quotes improve readability.
- **MUST** avoid extraneous whitespace and inconsistent indentation.

*Rationale*: Automated formatting eliminates style debates and ensures consistency.

## Naming Conventions

### General Guidelines

1. **Be Descriptive:** Names should clearly convey the purpose
2. **Consistency:** Stick to a consistent naming convention throughout the codebase
3. **Avoid Abbreviations:** Use full words for clarity
4. **Do not shorten words** when naming functions

### Variable Names

- **Convention:** Use `snake_case`
- **Be Meaningful:** Clearly indicate the variable's purpose
- **Avoid single character names** except for loop counters

### Function Names

- **Convention:** Use `snake_case`
- **Pattern:** Use verb-noun pairs to indicate the action performed
- **Do not shorten words** when naming functions

### Class Names

- **Convention:** Use `PascalCase`
- **Be Descriptive:** Class names should be nouns describing what the class represents

### Module Names

- **Convention:** Use `snake_case`
- **Be Descriptive:** Module names should clearly indicate their contents

### Constants

- **Convention:** Use `UPPER_CASE` with underscores
- **Location:** Define at module level

### Additional Tips

- **Use underscores to improve readability** especially in long names
  ```python
  max_user_connections_per_hour = 1000
  database_connection_retry_interval = 5
  ```

---

## Documentation Standards

- **MUST** include docstrings for all public modules, classes, and functions.
- **SHOULD** include docstrings for non-trivial private functions.
- **MUST** use a consistent docstring style (Google, NumPy, or reStructuredText).
- **Docstring content MUST include**:
  - Brief summary (one line)
  - Detailed description (if needed)
  - Parameters with types and descriptions
  - Return value with type and description
  - Raised exceptions
  - Examples (where helpful)
- **SHOULD** keep inline comments concise and focused on "why" rather than "what".
- **MUST** support the post-generation Why-Comment Enrichment pass — write code so non-trivial conditionals, retry loops, data transforms, and magic numbers can have a `# why:` comment added without ambiguity. See `QUICKSTART.md` → "Level-2 Post-Generation Explainability Step", Section E.
- **MUST NOT** leave commented-out code in production.
- **SHOULD** update documentation when code changes.

*Rationale*: Documentation is essential for onboarding, maintenance, and API usability.

### Module Documentation

Every module must start with a docstring describing its purpose:

```python
"""
User authentication module.

This module provides authentication and authorization functionality
for the application, including token validation and user session management.

Author: [Author Name]
Date: [Creation Date]
Revision History:
    - YYYY-MM-DD: [Description of changes] [JIRA-XXX] - [Author Name]
"""
```

### Function Documentation

- **Include a brief description** of the function's purpose
- **Description should optionally contain argument types and return types**
- **Document all parameters** with their types and meanings
- **Document return values** with their types and meanings
- **Document exceptions** that may be raised
- **Use multi-line comments for long-form annotations**

**Example:**
```python
def process_user_data(user_id: str, options: Dict[str, Any]) -> ProcessingResult:
    """
    Process user data with specified options.
    
    This function validates, transforms, and stores user data according
    to the provided processing options.
    
    Args:
        user_id (str): Unique identifier for the user
        options (Dict[str, Any]): Processing options including:
            - priority (int): Processing priority (1-10)
            - async_mode (bool): Whether to process asynchronously
            - notification (bool): Send notification on completion
            
    Returns:
        ProcessingResult: Object containing:
            - status (str): Processing status ('completed', 'failed', 'pending')
            - data (Dict): Processed user data
            - timestamp (datetime): Processing timestamp
            - errors (List[str]): Any errors encountered
            
    Raises:
        ValidationError: If user_id is invalid or options are malformed
        ProcessingError: If processing fails due to data issues
        DatabaseError: If database operation fails
        
    Example:
        >>> result = process_user_data("USER-123", {"priority": 8, "async_mode": True})
        >>> print(result.status)
        "completed"
        
    Note:
        - User IDs must be pre-validated before calling this function
        - Processing time varies based on priority and data size
        - Async mode requires proper queue configuration
        
    Revision History:
        - 2026-02-02: Fixed validation logic [JIRA-456] - John Doe
        - 2026-01-15: Added async processing support [JIRA-789] - Jane Smith
    """
    pass
```

### Class Documentation

```python
class DataProcessor:
    """
    Processor for transforming and validating data.
    
    This class handles data processing operations including validation,
    transformation, enrichment, and quality checks.
    
    Attributes:
        config (Dict[str, Any]): Configuration settings
        validator (DataValidator): Validator instance
        transformer (DataTransformer): Transformer instance
        
    Example:
        >>> processor = DataProcessor(config)
        >>> result = processor.process(data)
        >>> print(result.quality_score)
        
    Note:
        - Processor is stateless and thread-safe
        - Configuration cannot be changed after initialization
        
    Revision History:
        - 2026-02-02: Initial implementation [JIRA-100] - Jane Smith
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the data processor.
        
        Args:
            config: Configuration dictionary containing processing rules
            
        Raises:
            ConfigurationError: If config is invalid or incomplete
        """
        pass
```

### Comments

- **Use comments to explain code and make programs easier to understand**
- **Use multi-line comments for long-form annotations**
- Focus on the "why" not the "what"
- Keep comments up-to-date with code changes

```python
# Good ✅
# Calculate total with discount applied to handle promotional pricing
# This uses the store-wide discount rate from the configuration
total_with_discount = base_price * (1 - discount_rate)

# The following complex regex validates email formats according to RFC 5322
# We use this instead of a simple check to catch edge cases
email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

# Bad ❌
# Set x to 5
x = 5

# Loop through items
for item in items:
    process(item)
```

---

## FastMCP-Specific Rules

**Applicability:** These rules apply only to projects whose `Deployment Target` (in `PROJECT_OVERVIEW.md`) includes `FastMCP Server`, `FastAPI + FastMCP`, or `AWS Lambda + FastMCP`. Skip when the target is `FastAPI` or `AWS Lambda` only.

**Why these rules are stricter than the rest of the file:** FastMCP auto-generates the JSON schema that the AI client and underlying model see — directly from your function signature and docstring. Sloppy type hints or missing docstrings produce a tool the model cannot use correctly.

### Type Hints

- **MUST** add type hints to every parameter and return value of any `@mcp.tool`, `@mcp.resource`, or `@mcp.prompt` function — FastMCP uses them to generate the schema surfaced to the AI model.
- **MUST NOT** use bare `Any` in MCP signatures; if a value is genuinely free-form, wrap it in a Pydantic model with a documented schema.
- **SHOULD** use `Annotated[T, Field(description="...")]` from `pydantic` to attach human-readable parameter descriptions; these are shown to the model alongside the type.

```python
# Good ✅
from typing import Annotated
from pydantic import Field

@mcp.tool
async def search_regulations(
    query: Annotated[str, Field(description="Free-text search query.")],
    limit: Annotated[int, Field(ge=1, le=100, description="Max results to return.")] = 20,
) -> list[dict]:
    """Search the regulation index and return matching documents."""
    return regulation_service.search(query=query, limit=limit)
```

### Docstrings

- **MUST** include a one-line summary docstring for every MCP tool / resource / prompt — it becomes the description shown to the AI model.
- **SHOULD** include an `Args:` block with one line per parameter when the parameter purpose is not obvious from its name and type.
- **MUST** describe what the function does in terms of behavior, not implementation (the model sees the description; the code is invisible to it).

### Pydantic Models

- **MUST** use Pydantic models for tool inputs/outputs that have more than 3 fields or any nesting — this keeps the generated schema clean and validated.
- **SHOULD** reuse existing classes from `src/models/` rather than redefining; this guarantees REST and MCP transports surface identical shapes.

### Error Handling in MCP Components

- **MUST** raise `fastmcp.exceptions.ToolError` for user-visible failures — its message is surfaced to the AI model.
- **MUST** log the underlying exception via the standard `logging` logger before raising `ToolError`; never let stack traces or secrets leak into the `ToolError` message.
- **MUST** preserve exception context with `raise ToolError(...) from exc` so server-side logs retain the cause.

```python
# Good ✅
try:
    return regulation_service.summarize(reg_id)
except RegulationNotFoundError as exc:
    logger.error("Regulation not found: %s", reg_id, exc_info=True)
    raise ToolError(f"No regulation found with id={reg_id}.") from exc
```

### Architecture

- **MUST NOT** call one MCP tool from another MCP tool — extract shared logic into `src/services/` and call the service from each tool.
- **MUST NOT** import `LIGHTClient` or call `cortex_client` directly from any module under `src/mcp_server/`; route every external call through `src/services/`. This keeps REST and MCP behavior identical and is enforced by the framework's "MCP service-layer bypass" guardrail in `copilot-instructions.md`.
- **SHOULD** default to FastMCP 2.x (`from fastmcp import FastMCP`); use 1.x imports only when the project explicitly pins 1.x.

### Logging via Context

- **SHOULD** use `ctx.info` / `ctx.warning` / `ctx.error` (async on FastMCP 2.x) inside tools for client-visible progress messages.
- **MUST** also log to the standard `logging` logger for server-side observability — `Context` messages reach the client, not your log aggregator.

### Testing

- **MUST** use `fastmcp.Client` for MCP integration tests. It runs in-process — no transport setup, no subprocess. (Projects pinned to FastMCP 1.x use `mcp.client` instead.)
- **SHOULD** assert on the tool list, the generated schema, and at least one round-trip call/response per tool.
- **SHOULD** mock service-layer functions in tool tests (since the tool is a thin wrapper) and test the service layer separately at the unit level.

```python
# tests/mcp/test_cortex_tools.py
import pytest
from fastmcp import Client
from src.mcp_server.server import mcp

@pytest.mark.asyncio
async def test_ask_cortex_tool_returns_response(monkeypatch):
    monkeypatch.setattr(
        "src.services.regulation_service.generate_response",
        lambda user_prompt: "stub response",
    )
    async with Client(mcp) as client:
        tools = await client.list_tools()
        assert any(t.name == "ask_cortex" for t in tools)
        result = await client.call_tool("ask_cortex", {"prompt": "hi"})
        assert "stub response" in str(result)
```

---

## Configuration

### No Hard-Coded Values

- **Refrain from hard coding values - make them configurable**
- Use environment variables or configuration files
- Define constants at module level

**Examples:**
```python
# Bad ❌
def connect_to_database():
    connection = create_connection(
        host="localhost",
        port=5432,
        database="mydb",
        user="admin",
        password="secret123"
    )
    return connection

# Good ✅
import os
from src.core.config import settings

DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = int(os.getenv("DATABASE_PORT", "5432"))
DATABASE_NAME = os.getenv("DATABASE_NAME", "mydb")

def connect_to_database():
    """Connect to database using environment configuration."""
    connection = create_connection(
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        database=DATABASE_NAME,
        user=settings.database_user,
        password=settings.get_secret("database_password")
    )
    return connection
```

### No Secrets in Code

- **DO NOT STORE SECRETS IN CODE**
- **Ensure keys are not hard-coded and committed to GitHub**
- Use environment variables, secret managers, or secure vaults
- Never commit `.env` files with real secrets

**Examples:**
```python
# Bad ❌ - NEVER DO THIS
API_KEY = "sk-1234567890abcdef"
AWS_SECRET = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
DATABASE_PASSWORD = "MySecretPassword123"

# Good ✅
import os
from src.utils.secrets import SecretsManager

# Use environment variables
API_KEY = os.getenv("API_KEY")

# Or use a secrets manager
secrets = SecretsManager()
AWS_SECRET = secrets.get("aws_secret_access_key")
DATABASE_PASSWORD = secrets.get("database_password")
```
## Error Handling

- **MUST** prefer exceptions over return codes for error signaling.
- **MUST** use specific exception types, not bare `Exception` or `BaseException`.
- **SHOULD** define custom exception classes for domain-specific errors:
  ```python
  class DomainError(Exception):
      """Base exception for domain errors."""
  ```
- **MUST** preserve exception context using `raise ... from ...` when wrapping:
  ```python
  except LibraryError as e:
      raise CustomError("Context") from e
  ```
- **MUST NOT** catch exceptions silently (bare `except: pass`).
- **SHOULD** catch the narrowest exception type possible.
- **MUST** log exceptions before re-raising or handling.
- **SHOULD** provide actionable error messages.

*Rationale*: Proper exception handling improves debuggability and prevents silent failures.

## Logging

- **MUST** use the standard library `logging` module or a compatible structured logging library.
- **MUST** configure logging at the application entry point, not in libraries.
- **MUST** use appropriate log levels:
  - `DEBUG`: Detailed diagnostic information
  - `INFO`: General informational messages
  - `WARNING`: Unexpected but handled situations
  - `ERROR`: Error events that may allow continued execution
  - `CRITICAL`: Severe errors that may cause shutdown
- **SHOULD** use structured logging (key-value pairs) for machine readability.
- **MUST** redact sensitive information (passwords, tokens, PII) from logs.
- **MUST NOT** log secrets, credentials, or authentication tokens.
- **SHOULD** include request IDs or correlation IDs in distributed systems.

*Rationale*: Proper logging enables observability and incident investigation.

## Security Standards

### Input Validation
- **MUST** validate and sanitize all external input (user input, API requests, file uploads).
- **MUST** use allowlists over denylists for validation.
- **SHOULD** define schemas for structured input validation.

### Injection Prevention
- **MUST** use parameterized queries for all database operations.
- **MUST NOT** construct SQL, shell commands, or code dynamically from untrusted input.
- **MUST** escape or sanitize data when used in external systems.

### Secrets Management
- **MUST NOT** hardcode secrets, API keys, or credentials in source code.
- **MUST** load secrets from environment variables, secret management systems, or secure vaults.
- **MUST** exclude secrets from version control (use `.gitignore`).
- **SHOULD** rotate secrets regularly.

### Serialization and Deserialization
- **MUST NOT** use `pickle` or `eval()` on untrusted data.
- **SHOULD** use safe serialization formats (JSON, Protocol Buffers).
- **MUST** validate schema and content after deserialization.

### Dependency Hygiene
- **MUST** pin dependency versions in production.
- **SHOULD** regularly update dependencies and monitor for vulnerabilities.
- **MUST** review dependencies for license compliance and security advisories.

*Rationale*: Security vulnerabilities often originate from improper input handling and secrets management.

## Testing Standards

- **MUST** write automated tests for all non-trivial code.
- **SHOULD** aim for high test coverage while prioritizing meaningful tests over coverage metrics.
- **MUST** distinguish between:
  - **Unit tests**: Test individual functions/classes in isolation
  - **Integration tests**: Test interactions between components
  - **End-to-end tests**: Test complete workflows
- **MUST** run tests automatically in CI/CD pipelines.
- **MUST** name test functions descriptively: `test_<functionality>_<condition>_<expected_result>`
  ```python
  def test_parse_config_missing_required_field_raises_error():
  ```
- **SHOULD** use fixtures for test setup and teardown.
- **SHOULD** mock external dependencies (databases, APIs) in unit tests.
- **MUST** ensure tests are deterministic and repeatable.
- **MUST NOT** commit tests that are skipped or marked as expected failures without justification.

*Rationale*: Automated testing prevents regressions and enables confident refactoring.

## Data Handling and Privacy

- **MUST** classify data according to sensitivity (public, internal, confidential, restricted).
- **MUST** apply appropriate access controls based on data classification.
- **MUST** encrypt sensitive data at rest and in transit.
- **SHOULD** implement data retention and deletion policies.
- **MUST** anonymize or pseudonymize PII when possible.
- **MUST** obtain proper authorization before collecting or processing personal data.

*Rationale*: Data privacy is a legal and ethical requirement.

## Performance and Reliability

### Async vs Sync
- **SHOULD** use asynchronous I/O (`asyncio`) for I/O-bound operations in high-concurrency scenarios.
- **MUST** avoid mixing blocking calls in async code.
- **SHOULD** use synchronous code for CPU-bound tasks or when concurrency is not required.

### Timeouts and Retries
- **MUST** configure timeouts for all external calls (HTTP, database, message queue).
- **SHOULD** implement retry logic with exponential backoff for transient failures.
- **MUST** define maximum retry limits.

### Resource Management
- **MUST** use context managers (`with` statement) for resource cleanup:
  ```python
  with open(filename) as f:
      data = f.read()
  ```
- **MUST** ensure files, sockets, and database connections are properly closed.
- **SHOULD** use connection pooling for database and HTTP clients.

*Rationale*: Proper resource management prevents leaks and improves reliability.

## Concurrency and Asyncio

- **MUST** understand the Global Interpreter Lock (GIL) limitations for CPU-bound parallelism.
- **SHOULD** use `multiprocessing` or external workers for CPU-intensive tasks.
- **MUST** use thread-safe data structures when using threading.
- **MUST NOT** share mutable state between threads without synchronization.
- **MUST** use `asyncio.create_task()` for concurrent async operations.
- **MUST** handle `CancelledError` appropriately in async functions.
- **SHOULD** use async context managers (`async with`) for async resource management.

*Rationale*: Concurrency bugs are difficult to reproduce and debug.

## APIs and I/O Boundaries

- **MUST** define clear interfaces for external dependencies (databases, APIs, file systems).
- **SHOULD** use the adapter or repository pattern to abstract I/O operations.
- **MUST** validate data at system boundaries.
- **SHOULD** version APIs and maintain backward compatibility.
- **MUST** document API contracts (inputs, outputs, errors).
- **SHOULD** use dependency injection to decouple components.

*Rationale*: Clear boundaries improve testability and enable component substitution.
---

## Summary Checklist

When writing Python code, ensure:

- ✅ Follow PEP 8 style guide
- ✅ Use Pylint for linting
- ✅ Variable names: `snake_case`
- ✅ Function names: `snake_case` with verb-noun pairs
- ✅ Class names: `PascalCase`
- ✅ Constants: `UPPER_CASE`
- ✅ Module names: `snake_case`
- ✅ Do not shorten words in function names
- ✅ Every module/function has docstrings
- ✅ Include type hints for all functions
- ✅ No hard-coded values
- ✅ No secrets in code
- ✅ Remove dead code
- ✅ Use meaningful comments
- ✅ Proper import organization
- ✅ Specific exception handling
- ✅ Appropriate logging with context
- ✅ Minimum 70% test coverage
- ✅ Optional: Include revision history
- ✅ FastMCP (when target includes FastMCP): tools/resources/prompts have full type hints, one-line docstrings, raise `ToolError` for failures, and route all external calls through `src/services/`

---

## References

- [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [Pylint Documentation](https://pylint.pycqa.org/)
- [Python Type Hints (PEP 484)](https://peps.python.org/pep-0484/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
