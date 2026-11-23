"""Explicit example service entrypoint for discovery tests."""
from mcp.server.mcpserver.context import Context


async def ping(*, ctx: Context = None):
    return "pong"


def register_services(registry):
    registry.register(
        name="example.health.ping",
        handler=ping,
        description="Diagnostic ping",
        source="tests.sample_service_app",
    )
