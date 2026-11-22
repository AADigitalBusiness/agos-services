"""Tools use verified HTTP identity, not caller-controlled credentials."""
from types import SimpleNamespace

import pytest
from asgiref.sync import sync_to_async
from django.test import override_settings

from agos_services.apps.channels.models import MCPClient
from agos_services.apps.mcp_server.identity import client_from_context
from agos_services.apps.mcp_server.middleware import AuthenticationRequiredError
from agos_services.apps.mcp_server.server import create_mcp_server
from agos_services.apps.mcp_server.transport import bind_session_principal


def context_for(principal=None):
    request = SimpleNamespace(scope={})
    if principal is not None:
        request.scope["user"] = principal
    return SimpleNamespace(request_context=SimpleNamespace(request=request))


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_verified_context_resolves_only_active_client():
    alice = await sync_to_async(MCPClient.objects.create)(name="Alice")
    bob = await sync_to_async(MCPClient.objects.create)(name="Bob")
    scope = {}
    bind_session_principal(scope, alice)
    ctx = context_for(scope["user"])
    resolved = await client_from_context(ctx)
    assert resolved.pk == alice.pk
    assert resolved.pk != bob.pk

    alice.is_active = False
    await sync_to_async(alice.save)(update_fields=["is_active"])
    with pytest.raises(AuthenticationRequiredError):
        await client_from_context(ctx)


@pytest.mark.asyncio
async def test_missing_or_forged_context_fails_closed():
    from mcp.server.auth.middleware.bearer_auth import AuthenticatedUser
    from mcp.server.auth.provider import AccessToken

    with pytest.raises(AuthenticationRequiredError):
        await client_from_context(None)
    with pytest.raises(AuthenticationRequiredError):
        await client_from_context(context_for(SimpleNamespace(pk="forged")))
    with pytest.raises(AuthenticationRequiredError):
        await client_from_context(context_for(AuthenticatedUser(
            AccessToken(token="", client_id="not-a-uuid", scopes=[])
        )))


@pytest.mark.asyncio
async def test_shopify_tool_schema_never_exposes_client_token():
    with override_settings(
        AGOS_ENABLE_SHOPIFY_TOOLS=True,
        AGOS_ENABLE_SERVICE_DISCOVERY=False,
    ):
        server = create_mcp_server()
    tools = await server.list_tools()
    assert tools
    for tool in tools:
        schema = tool.input_schema
        assert "client_token" not in schema.get("properties", {})
        assert "ctx" not in schema.get("properties", {})
