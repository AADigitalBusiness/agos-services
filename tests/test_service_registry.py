"""App discovery, collision checks and permission-scoped tool execution."""
from importlib import import_module
from types import SimpleNamespace

import pytest
from mcp.server.mcpserver.context import Context

from agos_services.service_registry import ServiceRegistry, discover_services
from agos_services.apps.mcp_server.middleware import PrivilegeGate
import agos_services.service_registry as registry_module


def test_discover_only_explicit_app_entrypoints():
    app = SimpleNamespace(
        name="tests.sample_service_app",
        module=import_module("tests.sample_service_app"),
    )
    registry = discover_services(installed_apps=[app])
    assert [item.name for item in registry.definitions] == ["example.health.ping"]


def test_duplicate_and_invalid_names_fail_closed():
    registry = ServiceRegistry()

    async def handler(*, ctx: Context = None):
        return "ok"

    registry.register(name="example.health.ping", handler=handler, description="Ping")
    with pytest.raises(ValueError, match="Duplicate"):
        registry.register(name="example.health.ping", handler=handler, description="Ping")
    with pytest.raises(ValueError, match="Invalid"):
        registry.register(name="ping", handler=handler, description="Ping")


def test_sync_and_missing_context_rejected():
    registry = ServiceRegistry()

    def sync_handler(*, ctx: Context = None):
        return "ok"

    async def no_context():
        return "ok"

    async def arbitrary_token(*, ctx: Context = None, client_token=None):
        return "ok"

    with pytest.raises(TypeError, match="async"):
        registry.register(name="example.health.sync", handler=sync_handler, description="Sync")
    with pytest.raises(TypeError, match="ctx: Context"):
        registry.register(name="example.health.no_context", handler=no_context, description="No context")
    with pytest.raises(TypeError, match="client_token"):
        registry.register(name="example.health.unsafe", handler=arbitrary_token, description="Unsafe")


class FakeServer:
    def __init__(self):
        self.tools = {}

    def tool(self, *, name, description):
        def decorator(fn):
            self.tools[name] = fn
            return fn
        return decorator


@pytest.mark.asyncio
async def test_published_service_requires_identity_and_exact_permission(monkeypatch):
    registry = ServiceRegistry()
    events = []

    async def ping(*, ctx: Context = None):
        events.append("handler")
        return "pong"

    registry.register(name="example.health.ping", handler=ping, description="Ping")
    server = FakeServer()
    registry.publish(server)

    async def resolve(ctx):
        events.append(("identity", ctx))
        if ctx != "verified-request":
            raise ValueError("missing verified identity")
        return "client"

    async def authorize(client, name):
        events.append(("authorize", client, name))

    monkeypatch.setattr(registry_module, "client_from_context", resolve)
    monkeypatch.setattr(PrivilegeGate, "verify_tool_permission", authorize)

    assert await server.tools["example.health.ping"](ctx="verified-request") == "pong"
    assert events == [
        ("identity", "verified-request"),
        ("authorize", "client", "example.health.ping"),
        "handler",
    ]
    events.clear()
    with pytest.raises(ValueError, match="missing verified identity"):
        await server.tools["example.health.ping"](ctx=None)
    assert events == [("identity", None)]


@pytest.mark.asyncio
async def test_each_registered_tool_keeps_its_own_permission(monkeypatch):
    registry = ServiceRegistry()
    seen = []

    async def alpha(*, ctx: Context = None):
        return "a"

    async def beta(*, ctx: Context = None):
        return "b"

    registry.register(name="sample.alpha.run", handler=alpha, description="Alpha")
    registry.register(name="sample.beta.run", handler=beta, description="Beta")
    server = FakeServer()

    async def resolve(ctx):
        return "client"

    async def authorize(client, name):
        seen.append(name)

    monkeypatch.setattr(registry_module, "client_from_context", resolve)
    monkeypatch.setattr(PrivilegeGate, "verify_tool_permission", authorize)

    registry.publish(server)
    assert await server.tools["sample.alpha.run"](ctx=None) == "a"
    assert await server.tools["sample.beta.run"](ctx=None) == "b"
    assert seen == ["sample.alpha.run", "sample.beta.run"]
