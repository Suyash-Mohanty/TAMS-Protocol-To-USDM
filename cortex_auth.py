"""Per-request Azure AD token injection for Cortex API calls."""

import httpx


class CortexAuth(httpx.Auth):
    """Injects a fresh Cortex Authorization header on every HTTP request.

    LIGHTClient's get_auth_header() is called inside auth_flow(), which httpx
    invokes per-request — so the token is always current even in long-lived
    processes where Azure AD tokens expire (~30 min TTL).
    """

    def __init__(self, light_client) -> None:
        self._client = light_client

    def auth_flow(self, request: httpx.Request):
        request.headers["Authorization"] = self._client.get_auth_header()["Authorization"]
        yield request
