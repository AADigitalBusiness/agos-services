"""Exercise the MCP SDK's actual session-owner enforcement across clients."""
from types import SimpleNamespace
from uuid import uuid4
from urllib.parse import urlencode

import pytest
from mcp.server.auth.middleware.bearer_auth import authorization_context

from agos_services.apps.mcp_server.transport import (
    bind_session_principal,
    sse_transport,
)


def scope_for(client, session_id):
    scope = {
        "type": "http",
        "http_version": "1.1",
        "method": "POST",
        "scheme": "https",
        "path": "/mcp/messages/",
        "raw_path": b"/mcp/messages/",
        "query_string": urlencode({"session_id": session_id.hex}).encode(),
        "root_path": "",
        "headers": [(b"content-type", b"application/json")],
        "server": ("testserver", 443),
        "client": ("127.0.0.1", 12000),
    }
    bind_session_principal(scope, client)
    return scope


async def make_post(scope):
    sent = []

    async def receive():
        return {
            "type": "http.request",
            "body": b'{"jsonrpc":"2.0","id":1,"method":"ping"}',
            "more_body": False,
        }

    async def send(message):
        sent.append(message)

    await sse_transport._handle_post_message(scope, receive, send)
    statuses = [event["status"] for event in sent if event["type"] == "http.response.start"]
    assert len(statuses) == 1
    return statuses[0]


@pytest.mark.asyncio
async def test_other_client_cannot_post_to_an_existing_session(monkeypatch):
    session_id = uuid4()
    alice = SimpleNamespace(pk=uuid4())
    bob = SimpleNamespace(pk=uuid4())

    owner_scope = scope_for(alice, session_id)
    sse_transport._session_owners[session_id] = authorization_context(owner_scope["user"])
    # A writer exists, but it must not receive messages from Bob.
    sse_transport._read_stream_writers[session_id] = object()
    try:
        assert await make_post(scope_for(bob, session_id)) == 404
    finally:
        sse_transport._session_owners.pop(session_id, None)
        sse_transport._read_stream_writers.pop(session_id, None)


@pytest.mark.asyncio
async def test_session_owner_can_post_and_message_is_delivered():
    session_id = uuid4()
    alice = SimpleNamespace(pk=uuid4())
    owner_scope = scope_for(alice, session_id)
    delivered = []

    class Writer:
        async def send(self, message):
            delivered.append(message)

    sse_transport._session_owners[session_id] = authorization_context(owner_scope["user"])
    sse_transport._read_stream_writers[session_id] = Writer()
    try:
        assert await make_post(owner_scope) == 202
        assert len(delivered) == 1
    finally:
        sse_transport._session_owners.pop(session_id, None)
        sse_transport._read_stream_writers.pop(session_id, None)


@pytest.mark.asyncio
async def test_missing_principal_cannot_post_to_authenticated_session():
    session_id = uuid4()
    alice = SimpleNamespace(pk=uuid4())
    owner_scope = scope_for(alice, session_id)
    sse_transport._session_owners[session_id] = authorization_context(owner_scope["user"])
    sse_transport._read_stream_writers[session_id] = object()
    try:
        unauthenticated_scope = scope_for(alice, session_id)
        unauthenticated_scope.pop("user")
        assert await make_post(unauthenticated_scope) == 404
    finally:
        sse_transport._session_owners.pop(session_id, None)
        sse_transport._read_stream_writers.pop(session_id, None)
