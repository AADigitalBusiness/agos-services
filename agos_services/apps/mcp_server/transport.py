import json
import logging
from typing import List
from starlette.routing import Route
from starlette.responses import JSONResponse, Response
from starlette.requests import Request
from mcp.server.sse import SseServerTransport
from mcp.server.auth.middleware.bearer_auth import AuthenticatedUser
from mcp.server.auth.provider import AccessToken
from agos_services.apps.mcp_server.server import mcp_server_instance
from agos_services.apps.mcp_server.middleware import PrivilegeGate, AuthenticationRequiredError, PermissionDeniedError

logger = logging.getLogger(__name__)

sse_transport = SseServerTransport("/mcp/messages/")


def bind_session_principal(scope, client):
    """Give the MCP SDK a verified principal, never an untrusted token string.

    The SDK records scope["user"] when SSE starts and compares the same
    principal for every message POST's session_id.
    """
    principal = AuthenticatedUser(
        AccessToken(
            token="",
            client_id=str(client.pk),
            scopes=[],
        )
    )
    scope["user"] = principal
    return principal


async def sse_endpoint(request: Request):
    """
    SSE Endpoint for external MCP clients (Cursor, Claude Desktop, Antigravity).
    Authenticates client token from Authorization or x-mcp-client-token header.
    """
    auth_header = request.headers.get("authorization")
    token_param = request.headers.get("x-mcp-client-token")
    token = auth_header or token_param

    try:
        client = await PrivilegeGate.authenticate_token(token)
    except AuthenticationRequiredError as auth_err:
        return JSONResponse(
            {"error": "Unauthorized", "detail": str(auth_err)},
            status_code=401,
        )

    bind_session_principal(request.scope, client)
    logger.info("MCP client connected via SSE: client_id=%s", client.pk)

    async with sse_transport.connect_sse(
        request.scope, request.receive, request._send
    ) as (read_stream, write_stream):
        await mcp_server_instance.run(
            read_stream,
            write_stream,
            mcp_server_instance.create_initialization_options(),
        )
    return Response()


async def messages_endpoint(request: Request):
    """
    Message endpoint for SSE transport messages (JSON-RPC requests from client).
    """
    token = request.headers.get("authorization") or request.headers.get("x-mcp-client-token")
    try:
        client = await PrivilegeGate.authenticate_token(token)
    except AuthenticationRequiredError:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    bind_session_principal(request.scope, client)
    return await sse_transport.handle_post_message(
        request.scope, request.receive, request._send
    )


def get_starlette_routes() -> List[Route]:
    return [
        Route("/mcp/sse", endpoint=sse_endpoint, methods=["GET"]),
        Route("/mcp/messages/", endpoint=messages_endpoint, methods=["POST"]),
        Route("/mcp/messages", endpoint=messages_endpoint, methods=["POST"]),
    ]
