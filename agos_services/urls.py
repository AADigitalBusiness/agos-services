"""Opt-in Django URL routes, separate from the MCP SSE transport."""
from django.urls import include, path

urlpatterns = [
    path("channels/", include("agos_services.apps.channels.urls")),
    path("auth/shopify/", include("agos_services.apps.auth.urls")),
    path("mcp/", include("agos_services.apps.mcp_server.urls")),
]
