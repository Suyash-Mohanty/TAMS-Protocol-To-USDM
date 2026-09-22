# Running Protocol2USDM with Cortex

Lilly's internal LLM gateway (Cortex) can be used as a drop-in LLM backend
for the extraction pipeline instead of direct OpenAI/Anthropic/Google API
keys. This doc covers how the integration works and how to run a
conversion through it.

## How it works

1. **`light_client/`** (vendored at the project root) — `LIGHTClient`
   authenticates to Lilly-hosted services via Azure AD device-code OAuth
   (`light_client/oauth_login.py`). The first Cortex-backed LLM call opens
   a browser for a one-time login; the token is cached and auto-refreshed
   (~30 min TTL) for the rest of the process.
2. **`cortex_auth.py`** — `CortexAuth(httpx.Auth)` wraps the `LIGHTClient`
   and injects a fresh `Authorization` header on *every* HTTP request
   (not just once at startup), so long-running pipeline jobs don't hit
   expired-token errors mid-run.
3. **`llm_providers.py` → `CortexProvider`** — points an `OpenAI` SDK
   client at `https://api.cortex.lilly.com/cortex-openai` using the
   injected auth instead of a static API key. Because Cortex exposes an
   OpenAI-compatible surface (`/cortex-openai/chat/completions`, confirmed
   in `cortex_endpont.json`), JSON mode, vision input, and structured
   output all work unchanged.
4. **Routing** — `LLMProviderFactory.auto_detect()` routes any model name
   containing `"cortex"` to `CortexProvider`. Two things feed into this:
   - Names that literally contain the substring `"cortex"` (e.g.
     `claude-cortex-llm-config`) match automatically.
   - Any other Cortex model config — including personal/team-owned ones
     whose name doesn't contain "cortex" (e.g. `reforge-claude-opus-5`,
     which contains "claude" but not "cortex") — must be prefixed with
     `cortex/` on the CLI, e.g. `--model cortex/reforge-claude-opus-5`.
     `CortexProvider.__init__` strips the `cortex/` prefix before sending
     the model name to the API. **Without the prefix, a name like
     `reforge-claude-opus-5` would misroute to the direct-Anthropic
     `ClaudeProvider` instead of Cortex**, since it contains "claude".

## Available Cortex model configs

Cortex doesn't take raw model IDs — it takes a named **model config** that
someone has set up (admin-owned, or personal/team-owned), which maps to an
underlying LLM. A full account-authorized listing was pulled via
`GET /model/classes/list` (see `tools/cortex_discover_models.py`) and
dumped to `cortex_models_dump.json` (2,281 configs at last count). Across
all of them, the underlying LLM classes actually available on Cortex
include (non-exhaustive, counts = number of configs currently bound to it):

| Family | Notable classes seen |
| --- | --- |
| Anthropic | Claude 3.5/3.7 Sonnet, Claude 4/4.1/4.5/4.6/4.7/4.8 Opus, Claude 4/4.5/4.6 Sonnet, Claude 3.5/4.5 Haiku, **Claude 5 Opus**, **Claude 5 Sonnet** |
| OpenAI | GPT-4/4o/4.1, GPT-5/5.1/5.2/5.4/5.5, o1/o3/o4-mini reasoning models |
| Google | Gemini 1.5/2/2.5/3/3.1/3.5 (Flash and Pro variants) |
| Other | Grok-3/4, Llama 3.x/4, Nova, MedGemma/MedLM, DeepSeek R1 |

Most of the 2,281 configs are other people's project-specific bots (e.g.
`podcasts-sebas`, `genesys-chatbot`) — **having the underlying LLM class
exist on Cortex does not mean you're authorized to call it.** You need a
model config name your account can actually invoke. Confirmed, generally
usable configs as of this session:

| Model config name | Underlying LLM (resolved) | Vision-capable | Notes |
| --- | --- | --- | --- |
| `claude-cortex-llm-config` | Claude 4.6 Sonnet (`us.anthropic.claude-sonnet-4-6`) | ✅ confirmed | Official/admin config. Fast, reliable, cheapest of the confirmed options. |
| `cortex/reforge-claude-opus-5` | **Claude Opus 5** (`us.anthropic.claude-opus-5`) | ✅ confirmed (empirically tested against the SoA table image) | Team-owned config (`model-only-chain`, clean passthrough — no extra prompt injection). Requires the `cortex/` prefix (see Routing above). Rejects the `temperature` param outright (see Quirks below) and uses extended/hidden thinking tokens (see Quirks below). Owners at time of discovery: `sriharsha.chigurupati@lilly.com`, `dileepnagendra.guthula@lilly.com`, `navoneel.moitra@lilly.com`. |
| `gpt-cortex-llm-config` | GPT-4o | not confirmed | |
| `gemini-cortex-llm-config` | Gemini 2 Flash | not confirmed | |

**Recommended for maximum-accuracy extraction runs:** Opus 5
(`cortex/reforge-claude-opus-5`) for `--model` and `--vision-model`, Sonnet
(`claude-cortex-llm-config`) for `--fast-model`. In head-to-head testing on
the actual SoA table image, Opus 5 caught footnote superscript markers
that Sonnet's response omitted, at ~3x the token cost. Use plain Sonnet
everywhere if you want the fastest/cheapest run instead.

To (re-)discover the full list of models/configs your account is
authorized to access, run `python tools/cortex_discover_models.py`, or
call `GET /model/classes/list` directly once authenticated (see
`cortex_endpont.json` for the exact endpoint shape).

## Quirks discovered running Opus 5 through Cortex/Bedrock

These were all real failures hit while running the pipeline with
`cortex/reforge-claude-opus-5`, not hypothetical — each has a corresponding
fix already in the codebase:

1. **`temperature` is rejected outright.** Bedrock returns
   `BedrockException - "temperature" is deprecated for this model"` for
   Opus 5 (and possibly other newer Bedrock-hosted models), with no
   fallback model group configured on the Cortex side. Fixed generically
   in `CortexProvider.generate()` / `generate_with_image()`
   (`llm_providers.py`) and in `header_analyzer.py`'s
   `_analyze_with_cortex()` (which builds its own raw params dict and
   bypasses `CortexProvider`'s methods): on any error whose message
   mentions `temperature`, the code pops `temperature` from the request
   and retries once, non-model-specific.
2. **Extended/hidden thinking eats into the output token budget.**
   Opus 5 responses include `thinking_blocks` / `reasoning_content` in the
   raw API response even when not explicitly requested. On long-context
   narrative-style prompts (e.g. `scheduling_agent`'s ~17-page prompt),
   this hidden reasoning can consume the entire `max_tokens` budget,
   leaving **zero tokens for the visible answer** — the API call succeeds
   (`finish_reason: stop`, no error) but `message.content` comes back
   empty, which surfaces downstream as
   `Failed to parse LLM response: Expecting value: line 1 column 1 (char 0)`
   when the extractor tries `json.loads('')`. Fixed by bumping the
   Cortex-provider `narrative` task type's `max_tokens` to `32768` (see
   `provider_overrides.cortex.narrative` in `llm_config.yaml` and the
   matching default in `extraction/llm_task_config.py`) — see the next
   point for why this override wasn't taking effect until also fixed.
3. **Provider misdetection defeated the max_tokens override above.**
   `extraction/llm_task_config.py`'s `PROVIDER_PATTERNS` checked `"claude"`
   before `"cortex"`, so a model name like `reforge-claude-opus-5` (or any
   `cortex/reforge-claude-opus-5`) was classified as provider `"claude"`
   (direct Anthropic) instead of `"cortex"` — applying the tighter
   direct-Anthropic `narrative.max_tokens: 12288` override instead of the
   Cortex one. Fixed by reordering `PROVIDER_PATTERNS` so `"cortex"` is
   checked first. This is the same class of bug as the `auto_detect()`
   routing issue above — **any time a new pattern-matching table keys off
   substrings like `"claude"` vs `"cortex"`, cortex must win the tie**,
   since Cortex model config names are user-chosen and often contain
   another provider's name.
4. **A global `CORTEX_MODEL` env var used to silently override per-role
   models.** `.env` can set `CORTEX_MODEL=claude-cortex-llm-config` as a
   fallback default. The original code did
   `os.environ.get("CORTEX_MODEL", self.model)` — env-var-first — which
   meant an explicitly-passed `--model cortex/reforge-claude-opus-5` would
   silently get overridden back to whatever `.env` said. Fixed by flipping
   precedence to `self.model or os.environ.get("CORTEX_MODEL")` in both
   `CortexProvider.generate()`/`generate_with_image()` and
   `header_analyzer.py`.

## Setup

Add to `.env` (see `.env.example`):

```
CORTEX_MODEL=claude-cortex-llm-config
CORTEX_BASE=https://api.cortex.lilly.com
CORTEX_ENV=PRD   # DEV | QA | PRD — controls which Azure AD app/scope is used
```

`CORTEX_MODEL` is only a fallback now — an explicit `--model`/`--fast-model`/
`--vision-model` on the CLI always wins (see Quirk #4 above). Setting it
just pins a default for scripted runs that don't pass those flags.

No `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `GOOGLE_API_KEY` is needed when
running fully through Cortex. Note: a secondary, optional SoA-tick
validation step in `soa_text_agent` looks for `ANTHROPIC_API_KEY` /
`CLAUDE_API_KEY` directly (not via Cortex) and silently no-ops with a
`Validation failed: ANTHROPIC_API_KEY or CLAUDE_API_KEY not set` log line
if absent — this does not fail the run, it's just a skipped extra
cross-check.

## Running a conversion through Cortex

For maximum accuracy (Opus 5 for extraction + vision, Sonnet for the fast
role):

```bash
python run_extraction.py "input/test_trials/<protocol>.pdf" \
  --model cortex/reforge-claude-opus-5 \
  --fast-model claude-cortex-llm-config \
  --vision-model cortex/reforge-claude-opus-5 \
  --workers 4
```

For an all-Sonnet run (faster, cheaper, still solid quality):

```bash
python run_extraction.py "input/test_trials/<protocol>.pdf" \
  --model claude-cortex-llm-config \
  --fast-model claude-cortex-llm-config \
  --vision-model claude-cortex-llm-config \
  --workers 4
```

Leave vision (`--no-vision`) and enrichment (`--no-enrichment`) enabled —
both improve extraction fidelity, especially for protocols with a full SoA
table.

The first LLM call will open a browser window for Azure AD login; after
that it's silent for the rest of the run and for subsequent runs, until
the cached token needs re-authentication.

## CDISC CORE conformance validation

The pipeline runs CDISC CORE (v0.14.1) conformance validation
automatically as its final step and writes `conformance_report.json` +
`result.md` alongside the USDM output — no separate manual step needed.
A clean run should show 0 errors; warnings/info are typically about
optional attributes or code-system metadata, not structural problems.

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Browser doesn't open / hangs on first call | Running headless / over SSH | Complete device-code login manually using the URL+code printed to the terminal |
| `401`/`403` from Cortex mid-run | Token expired and refresh failed, or wrong `CORTEX_ENV` | Re-run; check `CORTEX_ENV` matches the environment your Azure AD app is registered in |
| `Cortex API call failed for model '...'` | Model config name typo, or account not authorized for that config | Verify against `GET /model/classes/list` output (`tools/cortex_discover_models.py`) |
| `ImportError: Cortex provider requires light_client and httpx` | `light_client/` missing or `httpx` not installed | Confirm `light_client/` exists at repo root; `pip install httpx` |
| 429 / rate limit errors | Cortex-side throttling | Handled automatically via exponential backoff in `llm_providers.py` (`_retry_with_backoff`); reduce `--workers` if persistent |
| `"temperature" is deprecated for this model` | Model (e.g. Opus 5) rejects `temperature` on Bedrock | Already handled — `CortexProvider` and `header_analyzer.py` retry once without `temperature` |
| `Failed to parse LLM response: Expecting value: line 1 column 1 (char 0)` on a narrative-type extractor with an Opus-class Cortex model | Hidden thinking tokens exhausted `max_tokens`, leaving an empty response | Already handled for the `cortex` provider's `narrative` task type (`max_tokens: 32768`); if it recurs on a different task type, raise that task type's `max_tokens` under `provider_overrides.cortex` in `llm_config.yaml` |
| A non-"cortex"-named Cortex model config routes to the wrong provider or gets the wrong `max_tokens`/param overrides | Substring pattern matching (`auto_detect()`, `PROVIDER_PATTERNS`) checked another provider's name (e.g. "claude") before "cortex" | Use the `cortex/<config-name>` prefix on the CLI; if you add a new pattern-matching table, make sure `"cortex"` is checked before other provider substrings |

## Notes

- `llm_config.yaml` has a `cortex` entry under `provider_overrides` that
  disables `top_k` (unsupported by Cortex's OpenAI-compatible surface) and
  raises `narrative.max_tokens` to `32768` for extended-thinking headroom
  — see Quirk #2/#3 above.
- Cortex routes through Bedrock for Claude models in some configs, which
  rejects `temperature` + `top_p` together; `CortexProvider` already
  handles this by omitting `top_p` whenever `temperature` is set, and by
  retrying without `temperature` at all if the model rejects it outright.
