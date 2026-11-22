"""Regression tests for generic MCP hosting and authentication safety."""
import pytest
from django.test import override_settings
from apps.mcp_server.middleware import PrivilegeGate, AuthenticationRequiredError
from apps.mcp_server.server import create_mcp_server


@pytest.mark.asyncio
@override_settings(MCP_AUTH_REQUIRED=False)
async def test_authentication_bypass_rejected():
    with pytest.raises(AuthenticationRequiredError):
        await PrivilegeGate.authenticate_token(None)


def test_generic_host_initializes_without_shopify_tool_registration():
    with override_settings(AGOS_ENABLE_SHOPIFY_TOOLS=False):
        assert create_mcp_server() is not None


def test_standalone_shopify_tool_registration():
    with override_settings(AGOS_ENABLE_SHOPIFY_TOOLS=True):
        assert create_mcp_server() is not None
