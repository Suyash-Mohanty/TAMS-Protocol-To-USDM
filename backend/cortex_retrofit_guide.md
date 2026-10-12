# Retrofitting an Existing LLM Application to Use Cortex

## Purpose and scope

`cortex_implementation.md` in this same folder is the guide for **scaffolding a new
project from scratch** with Cortex as its LLM provider. This document is for the
different, more common case: an **existing application already has its own LLM
abstraction** (a `build_chat_model()`/`get_llm_client()`-style factory, usually built
around `langchain_openai.ChatOpenAI` or a raw OpenAI SDK client pointed at some
OpenAI-compatible `base_url`), and you want to add Cortex as one more provider option
alongside whatever it already supports (`openai`, `azure_openai`, a generic
`litellm`-style gateway, etc.) — without breaking that abstraction or the rest of the
app.

This is exactly what was done for `usdm-agent` (a FastAPI/LangGraph service). The
steps, code shapes, and gotchas below are generalized from that concrete
implementation. Use it as a checklist and a source of copy-pasteable patterns, not as
a rigid script — adapt file paths and framework specifics to the target app.

---

## The core problem this guide solves

Every other LLM provider a generic app supports (`openai`, `azure_openai`, a LiteLLM
gateway, etc.) authenticates with a **static API key** that's valid for the life of the
process. Cortex does not:

- Auth is **Azure AD device-code OAuth** (interactive, user-delegated) via Lilly's
  internal `light_client` (`LIGHTClient`), or AWS SigV4 for Lambda/serverless. There is
  **no service-principal / app-only path** in `light_client` today.
- Access tokens are short-lived (Cortex's own docs cite ~30 min TTL); `LIGHTClient`
  caches and auto-refreshes them, but only if something calls
  `get_auth_header()` / triggers the refresh check on a live client.
- Most non-trivial apps build their LLM client **once** and reuse it for the life of
  the process (a cached LangGraph app, a singleton service, a `@lru_cache`d factory).
  A provider branch that does `api_key=get_token_once()` at construction time will
  work for the first ~30–60 minutes, then silently start failing with 401/403s.

**The fix, in one sentence:** keep using the app's existing OpenAI-compatible client
class (so nothing downstream — `.with_structured_output()`, tool calling, streaming,
etc. — has to change), but inject the Authorization header **per HTTP request** via a
custom `httpx.Auth`, so the token is always fresh no matter how long the client has
been alive.

This works because Cortex exposes an **OpenAI-compatible surface**
(`/cortex-openai/chat/completions`, `/responses`, `/embeddings`) in addition to its
native one (`/model/ask/{model}`). Always prefer the OpenAI-compatible surface for this
kind of retrofit — the native surface's response shape isn't tool-calling compatible,
so `with_structured_output()` (or equivalent) would need a hand-rolled JSON-parsing
replacement instead of working unmodified.

---

## Preconditions

Before starting, confirm:

1. **The app has a single, identifiable LLM-client construction point** — a factory
   function or class (`build_chat_model()`, `get_llm()`, a provider-switch statement).
   If the app constructs LLM clients ad hoc in many places, consolidate that first;
   the Cortex branch should live in exactly one place.
2. **The app's LLM client is (or can be) an OpenAI-compatible client** — LangChain's
   `ChatOpenAI`, the raw `openai` SDK, or equivalent — that accepts a custom
   `base_url` and a way to inject a custom HTTP client (see below). If the app is
   hard-wired to a provider SDK with no escape hatch for custom auth/transport, this
   pattern doesn't apply cleanly and needs a different approach.
3. **`backend/light_client/`** (or wherever this org's vendored copy lives) is
   available to copy from.
4. **You know whether the app is a long-lived server or a short-lived CLI/batch job**
   — this changes how much the token-refresh problem matters (see "Deployment mode"
   below).

---

## Step-by-step

### 1. Vendor `light_client`

Copy `light_client/*.py` and `client_config.ini` verbatim into the target app (e.g.
`<app>/<package>/vendor/light_client/`). Skip `__pycache__` and `.buildinfo`.

- **Never modify these files** — treat as a read-only vendored dependency, matching
  the org's own documented convention (`cortex_implementation.md`).
- Prefer vendoring (copying into the app's own package) over a sibling-directory
  `sys.path` hack — it keeps the app deployable/installable on its own, without a
  runtime dependency on some other repo folder being present at a relative path.

### 2. Add Cortex settings to the app's config

Whatever the app's config mechanism (`pydantic_settings.BaseSettings`, plain
`os.environ.get`, etc.), add:

```python
cortex_base: str = "https://api.cortex.lilly.com"
cortex_env: Literal["DEV", "QA", "PRD"] = "PRD"   # controls which Azure AD app/scope light_client uses
```

Reuse whatever field already holds the model name/id for other providers (e.g.
`llm_model`) as the Cortex **model-config name** — don't add a separate field for it.
Include the new fields in any config snapshot/audit mechanism the app already has, for
provenance.

### 3. Write the per-request auth wrapper

This is the piece that makes token refresh transparent for a long-running process.

```python
# <package>/llm/cortex_auth.py
import httpx


class CortexAuth(httpx.Auth):
    """Injects a fresh Cortex Authorization header on every request."""

    def __init__(self, light_client: object) -> None:
        self._client = light_client

    def auth_flow(self, request: httpx.Request):
        request.headers["Authorization"] = self._client.get_auth_header()["Authorization"]
        yield request
```

The key property: `get_auth_header()` is called **inside `auth_flow`**, which
`httpx` invokes on every single request — not once at construction time. That's what
makes this different from (and safer than) grabbing a token once and holding onto it.

### 4. Add the `cortex` branch to the LLM factory

```python
if provider == "cortex":
    from langchain_openai import ChatOpenAI   # or the app's equivalent OpenAI-compatible client
    import httpx
    from ..vendor.light_client import LIGHTClient
    from .cortex_auth import CortexAuth

    # Constructing LIGHTClient does NOT make a network call or trigger the
    # Azure AD device-code login — that only happens on the first real request,
    # inside CortexAuth.auth_flow via get_auth_header().
    light_client = LIGHTClient(env=settings.cortex_env)
    http_client = httpx.Client(auth=CortexAuth(light_client))
    return ChatOpenAI(
        model=settings.llm_model,                       # the Cortex model-config name
        temperature=settings.llm_temperature,
        base_url=f"{settings.cortex_base}/cortex-openai",
        api_key="unused",                                # real auth is injected per-request by CortexAuth
        http_client=http_client,
    )
```

For a raw `openai.OpenAI(...)` client instead of `ChatOpenAI`, the same
`http_client=` parameter exists and works the same way.

**If the app has an async call path** (`.ainvoke()`, `AsyncOpenAI`, etc.), also wire
`http_async_client=httpx.AsyncClient(auth=CortexAuth(light_client))` — a sync-only
`http_client` will not be used for async calls, and you'll get an unauthenticated or
misconfigured async client silently.

### 5. Dependencies

Add (promote from dev-only to core deps if already present for tests):
`httpx`, `requests`, `pycryptodome` (for `light_client`'s `Crypto.Cipher.AES`),
`watchdog`. Do not add `boto3`/`botocore` unless the app also needs the AWS-SigV4 auth
path (Lambda/serverless targets).

### 6. `.env.example` documentation block

```dotenv
# --- Cortex provider (Lilly internal) ---
# USDM__LLM_PROVIDER=cortex
# USDM__LLM_MODEL=<your-cortex-model-config-name>
# USDM__CORTEX_BASE=https://api.cortex.lilly.com
# USDM__CORTEX_ENV=PRD                 # DEV | QA | PRD -- controls which Azure AD app/scope is used
# Auth is Azure AD device-code OAuth, not a static key: the first call to a
# Cortex-backed model prints a device-code login prompt in the server's terminal.
# Complete it once in a browser with Lilly credentials; the token is then cached
# and refreshed automatically. If the process runs on a host where
# ~/.LIGHTPythonClient* isn't persisted across restarts, login is needed again.
```

(Adjust the env-var prefix to match the app's actual config convention.)

### 7. Getting a real Cortex model name — never invent one

**Do not guess or hardcode a Cortex model-config name.** It's a Cortex-internal
identifier, distinct from the underlying LLM name, and only exists if someone
registered it via `POST /model`.

- If the developer already has one (check their equivalent of
  `PROJECT_OVERVIEW.md`, or just ask), use it directly.
- If not, **generate** `scripts/create_cortex_model.py` from the template in
  `cortex_implementation.md` (Cortex-model-configuration-Step), filled in with:
  - a unique `name` (lowercase alphanumeric + dashes)
  - `displayName`, `model_description`
  - `auth.owners` — at least one owner email/user ID (**the developer's**, not
    invented — either ask directly, or leave a `<owner-id>` placeholder in the
    generated script for them to fill in themselves before running it)
  - `chain[0].chain_class` — `model-only-chain` for plain structured-output/generation
    tasks with no retrieval, `doc-chain` for RAG, `agent-chain` for tool-use chains
  - `model_versions[0].model_class` + `model_iteration` — **only** from the
    allow-list table in `cortex_implementation.md` (it's periodically refreshed from
    `GET /models`; never suggest a combination not in that table)
- **Never execute this script yourself.** Generate it, then instruct the developer to
  run it manually from their terminal. It prints a device-code URL for them to
  authenticate, then prints the registered model name and the exact env vars to set.
  This is both a security/ownership boundary (the model's `auth.owners` should be the
  actual developer, not an agent) and matches this org's own documented convention.

### 8. Testing

**Unit test (no network, no real auth) — sanity-check the wiring:**

```python
def test_build_chat_model_cortex_builds_openai_compatible_client(monkeypatch):
    class _FakeLightClient:
        def __init__(self, env): self.env = env
        def get_auth_header(self): return {"Authorization": "Bearer fake-token"}

    monkeypatch.setattr("<package>.vendor.light_client.LIGHTClient", _FakeLightClient)

    llm = build_chat_model(Settings(llm_provider="cortex", llm_model="x", cortex_env="DEV"))
    assert llm.model_name == "x"
    assert str(llm.openai_api_base) == "https://api.cortex.lilly.com/cortex-openai"
```

**Live smoke test — the step that's easy to skip and shouldn't be:**

A job/request completing successfully through the app's full pipeline is **not**
proof that Cortex was actually called. Many apps have deterministic/rule-based
fallback paths that never reach the LLM at all for simple inputs — that was true for
`usdm-agent` (its fact-extraction skill resolved everything via regex on the sample
input, `self.llm` was checked truthy but never invoked). Don't declare the integration
verified just because an end-to-end request returned 200.

To actually exercise the network path, call the factory and a structured-output
invocation directly, bypassing the app's own business logic:

```python
from <package>.config import get_settings
from <package>.llm.client import build_chat_model, structured_call
from pydantic import BaseModel

class Probe(BaseModel):
    reply: str
    language: str

llm = build_chat_model(get_settings())
result = structured_call(llm, Probe, system="Respond only via the schema.", human="Say hello in French.")
print(result)   # e.g. Probe(reply='Bonjour!', language='French')
```

If this returns a correctly-typed object, you've confirmed: auth works end-to-end
(including token caching/refresh), Cortex's OpenAI-compatible endpoint is reachable,
and — the one thing that's genuinely provider-specific and worth verifying — Cortex's
structured/tool-calling output is compatible with whatever structured-output mechanism
the app's LLM abstraction relies on.

---

## Deployment mode changes the calculus

- **Long-lived server** (FastAPI/uvicorn, a daemon, anything with a cached/singleton
  LLM client): the `CortexAuth` per-request injection above is required. A static
  token grabbed at startup will expire mid-lifetime.
- **Short-lived CLI/batch job** that constructs the client and exits within the
  token's TTL: a simpler one-shot `client.get_auth_header()` at construction time
  would technically survive for that one run, but there's no real cost to using
  `CortexAuth` anyway — it's strictly safer and makes the code identical regardless of
  how long the process happens to live. Prefer it by default.

## Operational limitation worth flagging to whoever owns deployment

`light_client` has no non-interactive (service-principal/app-only) auth path today.
On a fresh host/container where `~/.LIGHTPythonClient*` isn't persisted, **a human
has to complete the device-code browser flow after every restart** before the first
Cortex call succeeds. This guide does not solve that — it's a real constraint to
surface, not a code problem to work around silently (e.g. don't be tempted to bake in
a static fallback token "just for now").

---

## Checklist

- [ ] `light_client` vendored into the target app's own package, unmodified
- [ ] Config gains `cortex_base` / `cortex_env` (or equivalent), reusing the existing
      model-name field for the Cortex model-config name
- [ ] `CortexAuth(httpx.Auth)` implemented, header fetched inside `auth_flow`
      (per-request), not at client construction
- [ ] LLM factory's `cortex` branch uses the app's existing OpenAI-compatible client
      class pointed at `{cortex_base}/cortex-openai`, `http_client=` wired to
      `CortexAuth` (`http_async_client=` too, if the app has an async path)
- [ ] Deps added: `httpx`, `requests`, `pycryptodome`, `watchdog` (no `boto3` unless
      AWS-SigV4 target)
- [ ] `.env.example` documents the new vars and the one-time device-code login
- [ ] Cortex model-config name came from the developer or a manually-run
      `create_cortex_model.py` — never invented, never executed by the assistant
- [ ] Unit test covers the `cortex` branch with a mocked `LIGHTClient` (no network)
- [ ] Live smoke test actually invoked `structured_call`/`with_structured_output`
      directly (not just "a job completed") and returned a correctly-typed result
- [ ] Whoever owns deployment has been told about the no-service-principal /
      re-auth-after-restart limitation
