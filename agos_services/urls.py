"""Opt-in Django URL routes, separate from the MCP SSE transport."""
from django.urls import include, path

urlpatterns = [
    path("channels/", include("apps.channels.urls")),
    path("auth/shopify/", include("apps.auth.urls")),
    path("mcp/", include("apps.mcp_server.urls")),
]
