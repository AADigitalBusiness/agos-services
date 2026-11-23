"""Resolve tool permissions from the verified MCP request principal.

Client-supplied tool arguments are never an authentication source.
"""
from uuid import UUID

from asgiref.sync import sync_to_async
from mcp.server.auth.middleware.bearer_auth import AuthenticatedUser

from agos_services.apps.channels.models import MCPClient
from agos_services.apps.mcp_server.middleware import AuthenticationRequiredError


async def client_from_context(context):
    """Return the active MCPClient bound by the authenticated transport.

    Only the SDK's verified ASGI principal is trusted. Missing context, non-HTTP
    invocations and inactive or removed clients fail closed.
    """
    try:
        request = context.request_context.request
        principal = request.scope.get("user")
    except (AttributeError, KeyError, TypeError, ValueError):
        raise AuthenticationRequiredError("Authenticated MCP request context is required.") from None
    if not isinstance(principal, AuthenticatedUser):
        raise AuthenticationRequiredError("Authenticated MCP principal is required.")
    try:
        identifier = UUID(principal.access_token.client_id)
    except (ValueError, TypeError, AttributeError):
        raise AuthenticationRequiredError("Invalid MCP principal.") from None

    client = await sync_to_async(
        lambda: MCPClient.objects.filter(pk=identifier, is_active=True).first()
    )()
    if client is None:
        raise AuthenticationRequiredError("MCP client is inactive or no longer exists.")
    return client
