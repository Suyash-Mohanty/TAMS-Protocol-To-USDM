# TAMS-Protocol-To-USDM

An agentic pipeline that extracts structured clinical trial data from protocol PDF documents and produces [CDISC USDM v4.0](https://www.cdisc.org/ddf) JSON output.

The system uses a wave-based multi-agent architecture. Specialized extraction agents run in parallel (within dependency-ordered waves) and write entities into a shared in-memory context store. A USDM generator then assembles the final JSON, followed by terminology enrichment, schema validation, and optional CDISC CORE conformance checking.

This is my fourth attempt at extracting clinical protocol files into standardized format.

## What It Does

- Parses clinical trial protocol PDFs (text + vision)
- Extracts USDM entity types across 14 extraction agents: metadata, eligibility criteria, objectives, endpoints, study design, interventions, Schedule of Assessments (SoA), procedures, scheduling, execution model, biomedical concepts, narrative, document structure, amendments/geography, and more
- Produces USDM v4.0 JSON aligned with the official CDISC schema
- Enriches entities with NCI EVS terminology codes
- Tracks provenance (which PDF pages each entity came from, which agent extracted it)
- Validates output against the USDM schema and (optionally) CDISC CORE rules
- Provides a web UI for reviewing results with provenance
- Writes a `result.md` / `result.json` per run documenting what each agent did (time, tokens, API calls)

## Quick Start

```bash
# Clone
git clone https://github.com/Suyash-Mohanty/TAMS-Protocol-To-USDM.git
cd TAMS-Protocol-To-USDM

# Install
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Configure (Vertex AI recommended for clinical content)
cp .env.example .env
# Edit .env with your credentials

# Run
python run_extraction.py your_protocol.pdf
```

Output lands in `output/<protocol_name>_<timestamp>/`, with the primary file being `<protocol_name>_usdm.json`.

> Note: pip packages at Lilly should be pulled through JFrog Artifactory rather than public PyPI. Configure your pip index accordingly before running `pip install`.

## Requirements

- Python 3.13 (used by the Dockerfile and by existing local runs; other versions are untested)
- Credentials for at least one LLM provider: Google Vertex AI / AI Studio, Anthropic (direct or AWS Bedrock), OpenAI, or Lilly's Cortex gateway
- Internet connection for LLM API calls and NCI EVS enrichment

## Configuration

Copy `.env.example` to `.env` and fill in what you need:

```bash
# Google Cloud Vertex AI (recommended for Gemini - avoids safety filter issues with clinical text)
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1

# Alternative: Google AI Studio (may block medical content due to safety filters)
# GOOGLE_API_KEY=...

# Anthropic - direct API
# CLAUDE_API_KEY=...

# Anthropic via AWS Bedrock (alternative to the direct API)
# CLAUDE_PROVIDER=...
# AWS_REGION=...
# AWS_ACCESS_KEY_ID=...
# AWS_SECRET_ACCESS_KEY=...

# OpenAI
# OPENAI_API_KEY=...

# CDISC (optional, for CORE conformance validation)
# CDISC_API_KEY=...

# Cortex (Lilly internal LLM gateway, Azure AD device-code auth)
# CORTEX_MODEL=...
# CORTEX_BASE=...
# CORTEX_ENV=...
```

See [.env.example](.env.example) for the authoritative list and [docs/configuration-guide.md](docs/configuration-guide.md) for details. Per-task LLM parameters live in `llm_config.yaml`.

### Using Cortex (Lilly's LLM gateway)

Cortex needs no static API key. The first LLM call opens a browser for Azure AD device-code login (via `light_client/`), and the token is cached and refreshed automatically (`cortex_auth.py`). A model name routes to Cortex if it contains `cortex`, or if you prefix it with `cortex/`:

```bash
python run_extraction.py protocol.pdf \
  --model cortex/reforge-claude-opus-5 \
  --vision-model cortex/reforge-claude-opus-5 \
  --fast-model claude-cortex-llm-config
```

See [docs/cortex-guide.md](docs/cortex-guide.md) for available model configs and known quirks.

## Usage

```bash
# Default: full extraction with gemini-2.5-pro
python run_extraction.py protocol.pdf

# Specify model
python run_extraction.py protocol.pdf --model claude-opus-4-6

# Use separate models for different tasks
python run_extraction.py protocol.pdf --model gemini-2.5-pro --fast-model gemini-2.5-flash --vision-model gemini-2.5-flash

# Several PDFs / glob patterns in one run
python run_extraction.py input/test_trials/*.pdf --workers 2

# Parallel workers (default: 4) and custom output directory (default: output)
python run_extraction.py protocol.pdf --workers 4 --output-dir results

# Disable optional features
python run_extraction.py protocol.pdf --no-vision --no-enrichment

# Skip specific agents (use the agent IDs shown in result.md)
python run_extraction.py protocol.pdf --skip scheduling_agent execution_agent

# Checkpoints
python run_extraction.py --list-checkpoints
python run_extraction.py --clean-checkpoints

# Verbose logging
python run_extraction.py protocol.pdf --verbose
```

Notes:

- `--no-vision` disables **both** SoA agents (`soa_vision_agent` and `soa_text_agent`), because the text agent depends on the vision agent's table structure.
- `--fast-model` is used by most extraction agents (metadata, eligibility, objectives, study design, interventions, procedures, execution, narrative, document structure, advanced, biomedical concepts, SoA text). `--model` is used by `scheduling_agent`, which needs reliable parsing of a complex JSON structure. `--vision-model` is used by `soa_vision_agent`. Any of the three that you leave unset falls back to `--model`.
- **Resume is not implemented yet.** The orchestrator writes a checkpoint after every wave, and `--resume-from-checkpoint <file>` will load one, but it does not re-run the remaining waves (the CLI says so). Checkpoints are deleted automatically after a fully successful run. If a run fails, re-run it from scratch.

## Supported Models

The provider is chosen from the model name (`LLMProviderFactory.auto_detect()` in [llm_providers.py](llm_providers.py)).

| Model | Provider | Notes |
|-------|----------|-------|
| `gemini-2.5-pro` | Google | Default. Fast, good accuracy. |
| `gemini-2.5-flash` | Google | Lighter, good for fast-model tasks. |
| `claude-opus-4-7`, `claude-opus-4-6`, `claude-opus-4-5`, `claude-opus-4-1`, `claude-opus-4` | Anthropic (direct or Bedrock) | High accuracy, higher cost. |
| `claude-sonnet-4-5`, `claude-sonnet-4` | Anthropic (direct or Bedrock) | Good balance of speed and accuracy. |
| `gpt-4o`, `gpt-4o-mini`, `gpt-4`, `gpt-4-turbo` | OpenAI | Alternative provider. |
| `claude-cortex-llm-config`, `cortex/<config-name>` | Lilly Cortex | Internal gateway; see above. |

Use Vertex AI (not AI Studio) for Gemini models when processing clinical content to avoid safety filter blocks. The exact list of accepted model names is defined in `llm_providers.py`.

## Pipeline Architecture

```
run_extraction.py
  └─ ExtractionPipeline  (agents/pipeline.py)
       ├─ Orchestrator builds waves from each agent's declared dependencies
       │    Wave 0: PDF Parser, Metadata, Narrative, Doc Structure, SoA Vision
       │    Wave 1: Eligibility, Objectives, Study Design, Advanced, SoA Text, Procedures
       │    Wave 2: Interventions, Scheduling, Execution Model, Biomedical Concepts
       │    Wave 3: Post-Processing, Reconciliation, Validation, Enrichment
       ├─ USDM Generator   (assembles all entities into USDM v4.0 JSON)
       ├─ Provenance Generator
       ├─ Schema / semantic validation (usdm package, when installed)
       └─ CDISC CORE conformance check (optional, needs the CORE engine)
```

Waves are **computed at runtime** from each agent's `dependencies` (see `OrchestratorAgent.create_execution_plan()`), not read from a fixed table. The layout above is what a normal full run produces. Agents inside a wave run in parallel (up to `--workers`). A wave starts only after the previous one finishes, and a checkpoint is written after each wave.

Two quirks worth knowing: the `usdm-generator` and `provenance` agents declare no dependencies, so they are also scheduled in Wave 0 where they have nothing to work with. The pipeline then runs both again after all waves finish, which produces the real USDM and provenance files. Also, `WAVE_CONFIG` in `agents/pipeline.py` is not used for scheduling (only by tests).

See [docs/extraction-pipeline.md](docs/extraction-pipeline.md) for the agent-by-agent breakdown and entity-to-USDM mapping, and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the design document. The architecture document describes a more extensive target design (distributed deployment, external message queue, etc.). The current implementation runs in a single Python process with an in-memory context store.

## Output

Each run writes to `output/<protocol_name>_<timestamp>/`:

```
output/<protocol_name>_<timestamp>/
├── <protocol_name>_usdm.json           # Primary USDM v4.0 output
├── <protocol_name>_provenance.json     # Entity-level provenance
├── 9_final_soa_provenance.json         # SoA cell-level provenance
├── id_mapping.json                     # Simple ID -> UUID mapping
├── conformance_report.json             # CDISC CORE results (success:false if the engine is not installed)
├── usdm_validation.json                # Schema + semantic validation (only if the `usdm` package ran validation)
├── result.md                           # Human-readable run summary
├── result.json                         # Machine-readable run summary (used by the UI)
├── 01_extraction_metadata.json         # Per-agent outputs, numbered by step:
├── 02_extraction_soa_vision.json       #   01-14 extraction agents
├── ...                                 #   15-18 quality agents
├── 14_extraction_biomedical_concepts.json
├── 15_quality_postprocessing.json
├── 16_quality_reconciliation.json
├── 17_quality_validation.json
├── 18_quality_enrichment.json
├── 19_support_usdm_generator.json      #   19-20 support agents
├── 20_support_provenance.json
├── soa_page_NNN.png                    # Rendered SoA page images used by the vision agent
└── <protocol_name>.pdf                 # Copy of the input PDF (used by the web UI)
```

Files for agents that were skipped or failed will be missing.

## CDISC CORE Conformance (optional)

The conformance check uses the CDISC CORE engine executable at `tools/core/core/core/core.exe`. Download it with:

```bash
python tools/core/download_core.py
```

The engine also needs a CDISC Library API key (`CDISC_API_KEY` or `CDISC_LIBRARY_API_KEY`) to build its rules cache. If the engine is not installed, the run still succeeds and `conformance_report.json` records that the engine is unavailable. A standalone validator is also available in [usdm-validator/](usdm-validator/README.md).

## Web UI

A React/Next.js viewer for reviewing extraction results. It reads run folders from `../output` by default (override with the `PROTOCOL_OUTPUT_DIR` environment variable):

```bash
cd web-ui
npm install
npm run dev
# Open http://localhost:3000
```

(Install npm packages through the approved internal Artifactory registry.)

Features include:
- SoA table with provenance filters (Confirmed in green, Text Only in blue, Needs Review in orange, Orphaned in red)
- Views for Metadata, Eligibility, Objectives and Endpoints, Study Design, Interventions, Procedures and Devices, Schedule Timeline, Footnotes, Amendment History, Study Sites, Narrative and Advanced Entities
- Source page preview with PDF page rendering
- Validation and conformance results
- Raw USDM JSON viewer

See [web-ui/README.md](web-ui/README.md) for the web UI's own documentation.

## Testing and Evaluation

```bash
# Unit tests
pytest tests/ -q

# Pipeline / benchmarking scripts
python -m pytest testing/

# Agent evals against golden outputs (runs pytest on evals/)
python evals/run_evals.py
python evals/run_evals.py --protocol Alexion_NCT04573309_Wilsons
```

## Other Tools

| Tool | Purpose |
|------|---------|
| `python -m fidelity_validator.cli protocol.pdf study_usdm.json` | Fidelity validator: checks how faithfully a USDM file reflects the source PDF (`fidelity_validator/`) |
| `python usdm_deviation_report.py golden.json test.json [out.xlsx]` | Compares a USDM extraction to a golden reference and writes a colour-coded Excel deviation report |
| `python -m converter.cli` | Standalone Prodigy-to-USDM 4.0 converter (`converter/`), separate from the PDF pipeline |
| `python usdm-validator/validate.py` | Standalone CDISC CORE validation of a USDM JSON file |

## Documentation

- [Extraction Pipeline](docs/extraction-pipeline.md) - agent execution order, entity-to-USDM mapping, quality pipeline, gaps
- [Architecture](docs/ARCHITECTURE.md) - system design and component overview
- [User Guide](USER_GUIDE.md) - detailed usage instructions, model selection, troubleshooting
- [API Reference](docs/api-reference.md) - module and function reference
- [Configuration Guide](docs/configuration-guide.md) - LLM config, environment variables
- [Cortex Guide](docs/cortex-guide.md) - running through Lilly's Cortex gateway
- [Deployment Guide](docs/deployment-guide.md) - Docker, infrastructure

## Project Structure

```
TAMS-Protocol-To-USDM/
├── run_extraction.py         # CLI entry point
├── llm_providers.py          # LLM provider abstraction (Google, Anthropic, OpenAI, Cortex)
├── llm_config.yaml           # LLM task-specific parameters
├── cortex_auth.py            # Per-request Azure AD auth for Cortex
├── light_client/             # Vendored Lilly auth client (Azure AD device-code OAuth)
├── agents/                   # Agent framework
│   ├── orchestrator.py       # Wave-based execution planner and runner
│   ├── pipeline.py           # Pipeline config, agent creation, final outputs
│   ├── context_store.py      # Shared in-memory entity store
│   ├── extraction/           # 14 extraction agents
│   ├── quality/              # Post-processing, validation, reconciliation, enrichment
│   └── support/              # PDF parser, USDM generator, provenance, checkpoint, error handler
├── extraction/               # Domain extractors with prompts and schemas (called by agents)
├── core/                     # USDM types, schema, LLM client, validation, provenance, reconciliation
├── enrichment/               # NCI EVS terminology enrichment
├── validation/               # USDM and CDISC CORE validation
├── converter/                # Standalone Prodigy-to-USDM converter
├── fidelity_validator/       # Protocol-vs-USDM fidelity checks
├── usdm-validator/           # Standalone CDISC CORE validator
├── evals/                    # Agent evals against golden outputs
├── web-ui/                   # React/Next.js protocol viewer
├── tools/                    # CDISC CORE engine download
├── infra/                    # Grafana, Prometheus, nginx configs
├── testing/                  # Benchmarking and integration tests
├── tests/                    # Unit tests
├── input/                    # Sample protocol PDFs and golden reference
├── output/                   # Run outputs (one folder per run)
├── checkpoints/              # Per-wave checkpoints (removed after a successful run)
└── docs/                     # Documentation
```

## Known Issues

- `--resume-from-checkpoint` loads a checkpoint but does not resume execution (see Usage).
- The `Dockerfile` is out of date: it copies `pipeline/`, `utilities/` and `main_v3.py`, none of which exist in this repository, and its entrypoint is `main_v3.py` instead of `run_extraction.py`. It will not build as-is.
- `docs/cortex-guide.md` refers to `tools/cortex_discover_models.py`, which is not in `tools/`.

## License

Contact author for permission to use.
