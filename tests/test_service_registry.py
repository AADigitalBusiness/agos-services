"""Explicit Django app discovery and permission-bound invocation."""
import asyncio
from importlib import import_module
from types import SimpleNamespace

import pytest

from agos_services.service_registry import ServiceRegistry, discover_services
from agos_services.apps.mcp_server.middleware import PrivilegeGate


def test_discover_only_explicit_app_entrypoints():
    app = SimpleNamespace(
        name="tests.sample_service_app",
        module=import_module("tests.sample_service_app"),
    )
    registry = discover_services(installed_apps=[app])
    assert [item.name for item in registry.definitions] == ["example.health.ping"]


def test_duplicate_and_invalid_names_fail_closed():
    registry = ServiceRegistry()

    async def handler(*, client_token=None):
        return "ok"

    registry.register(name="example.health.ping", handler=handler, description="Ping")
    with pytest.raises(ValueError, match="Duplicate"):
        registry.register(name="example.health.ping", handler=handler, description="Ping")
    with pytest.raises(ValueError, match="Invalid"):
        registry.register(name="ping", handler=handler, description="Ping")


def test_sync_and_missing_token_contract_rejected():
    registry = ServiceRegistry()

    def sync_handler(*, client_token=None):
        return "ok"

    async def no_token():
        return "ok"

    with pytest.raises(TypeError, match="async"):
        registry.register(name="example.health.sync", handler=sync_handler, description="Sync")
    with pytest.raises(TypeError, match="client_token"):
        registry.register(name="example.health.no_token", handler=no_token, description="Missing token")


@pytest.mark.asyncio
async def test_published_service_requires_exact_permission(monkeypatch):
    registry = ServiceRegistry()
    events = []

    async def ping(*, client_token=None):
        events.append("handler")
        return "pong"

    registry.register(name="example.health.ping", handler=ping, description="Ping")

    class FakeServer:
        def __init__(self):
            self.tools = {}

        def tool(self, *, name, description):
            def decorator(fn):
                self.tools[name] = fn
                return fn
            return decorator

    server = FakeServer()
    registry.publish(server)

    async def authenticate(token):
        events.append(("authenticate", token))
        if token != "valid":
            raise ValueError("invalid token")
        return "client"

    async def authorize(client, name):
        events.append(("authorize", client, name))
        if name != "example.health.ping":
            raise ValueError("unexpected service")

    monkeypatch.setattr(PrivilegeGate, "authenticate_token", authenticate)
    monkeypatch.setattr(PrivilegeGate, "verify_tool_permission", authorize)

    result = await server.tools["example.health.ping"](client_token="valid")
    assert result == "pong"
    assert events == [
        ("authenticate", "valid"),
        ("authorize", "client", "example.health.ping"),
        "handler",
    ]
    events.clear()
    with pytest.raises(ValueError, match="invalid token"):
        await server.tools["example.health.ping"](client_token="invalid")
    assert "handler" not in events
