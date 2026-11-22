from django.http import JsonResponse
from django.views import View

class MCPInfoView(View):
    """Informational endpoint explaining that external access is exclusively via MCP protocol."""
    def get(self, request):
        return JsonResponse({
            "service": "AGOS MCP Gateway",
            "protocol": "Model Context Protocol (MCP) 2024-11-05 / 2.x",
            "isolation_policy": "Strict MCP only - No direct external REST bypass",
            "transport_endpoints": {
                "sse": "/mcp/sse",
                "messages": "/mcp/messages/",
            },
            "authentication": "Bearer token or X-MCP-Client-Token header required",
            "available_tools": [
                "shopify.products.list",
                "shopify.products.get",
                "shopify.inventory.search",
                "shopify.orders.list",
                "shopify.orders.get",
                "shopify.draft_orders.create",
            ]
        })
