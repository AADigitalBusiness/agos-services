"""Explicit example service entrypoint for discovery tests."""
async def ping(*, client_token=None):
    return "pong"


def register_services(registry):
    registry.register(
        name="example.health.ping",
        handler=ping,
        description="Diagnostic ping",
        source="tests.sample_service_app",
    )
