"""Authentication regression for MCP SSE message transport."""
import pytest
from starlette.requests import Request

from agos_services.apps.mcp_server.middleware import AuthenticationRequiredError, PrivilegeGate
from agos_services.apps.mcp_server.transport import messages_endpoint


def make_request(headers=None):
    raw_headers = [
        (name.lower().encode("ascii"), value.encode("ascii"))
        for name, value in (headers or {}).items()
    ]
    scope = {
        "type": "http",
        "http_version": "1.1",
        "method": "POST",
        "scheme": "https",
        "path": "/mcp/messages/",
        "raw_path": b"/mcp/messages/",
        "query_string": b"",
        "root_path": "",
        "headers": raw_headers,
        "server": ("testserver", 443),
        "client": ("127.0.0.1", 1234),
    }
    return Request(scope)


@pytest.mark.asyncio
async def test_messages_without_token_rejected_before_transport(monkeypatch):
    calls = []

    async def authenticate(token):
        calls.append(("authenticate", token))
        raise AuthenticationRequiredError("No token")

    async def transport(*args):
        calls.append(("transport",))
        raise AssertionError("transport should never execute")

    monkeypatch.setattr(PrivilegeGate, "authenticate_token", authenticate)
    from agos_services.apps.mcp_server import transport as module
    monkeypatch.setattr(module.sse_transport, "handle_post_message", transport)

    response = await messages_endpoint(make_request())
    assert response.status_code == 401
    assert calls == [("authenticate", None)]


@pytest.mark.asyncio
async def test_invalid_bearer_rejected_before_transport(monkeypatch):
    async def authenticate(token):
        assert token == "Bearer invalid"
        raise AuthenticationRequiredError("Bad credentials")

    monkeypatch.setattr(PrivilegeGate, "authenticate_token", authenticate)
    response = await messages_endpoint(
        make_request({"authorization": "Bearer invalid"})
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_valid_bearer_reaches_transport(monkeypatch):
    from starlette.responses import Response
    from agos_services.apps.mcp_server import transport as module

    calls = []

    from types import SimpleNamespace

    async def authenticate(token):
        assert token == "Bearer test-token"
        calls.append("authorized")
        return SimpleNamespace(pk="8c7100f5-c997-4f49-93f6-1490616d5c82")

    async def transport(*args):
        calls.append("transport")
        return Response(status_code=202)

    monkeypatch.setattr(PrivilegeGate, "authenticate_token", authenticate)
    monkeypatch.setattr(module.sse_transport, "handle_post_message", transport)

    request = make_request({"authorization": "Bearer test-token"})
    response = await messages_endpoint(request)
    assert response.status_code == 202
    assert calls == ["authorized", "transport"]
    assert request.scope["user"].access_token.client_id == "8c7100f5-c997-4f49-93f6-1490616d5c82"
