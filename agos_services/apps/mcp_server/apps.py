from django.apps import AppConfig

class McpServerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "agos_services.apps.mcp_server"
    label = "mcp_server"
    verbose_name = "Model Context Protocol (MCP) Server"
