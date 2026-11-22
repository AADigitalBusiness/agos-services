"""Mount the MCP transport into an existing Django project's ASGI application."""
from starlette.applications import Starlette
from starlette.routing import Mount


def mount_mcp(django_application):
    """Expose MCP SSE transport while preserving the host's Django ASGI application."""
    from apps.mcp_server.transport import get_starlette_routes

    return Starlette(routes=[*get_starlette_routes(), Mount("/", django_application)])
