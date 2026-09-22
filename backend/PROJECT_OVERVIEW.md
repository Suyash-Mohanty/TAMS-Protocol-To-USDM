# Project Context - Single Source of Truth

## Purpose

This is the **master reference document** and single source of truth containing all project information - business context, architecture, tech stack, features, integrations.

**Deployment Target (MANDATORY):** <FastAPI | AWS Lambda | FastMCP Server | FastAPI + FastMCP | AWS Lambda + FastMCP>

**MCP Transport (MANDATORY if Deployment Target includes FastMCP):** <stdio | streamable-http | sse>

**MCP Server Name (MANDATORY if Deployment Target includes FastMCP):** <e.g., `regulatory-md-server` — kebab-case, lowercase>

**FastMCP Version (OPTIONAL — defaults to 2.x):** <leave blank for 2.x | `1.x` only when the project explicitly pins the bundled `mcp` SDK>

**LLM Provider (MANDATORY if LLM is used):** <Cortex | Other | None>

**Cortex Model Name (MANDATORY if LLM Provider = Cortex):** <e.g., `agentic-test112114` | `NEW` to create one>