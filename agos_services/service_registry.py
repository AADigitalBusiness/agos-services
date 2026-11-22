"""Explicit, fail-closed registry for Django application MCP services."""
from dataclasses import dataclass
from functools import wraps
from inspect import iscoroutinefunction, signature
from importlib import import_module
import re

from django.apps import apps
from django.utils.module_loading import module_has_submodule

from agos_services.apps.mcp_server.middleware import PrivilegeGate

SERVICE_NAME = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*){2,}$")


@dataclass(frozen=True)
class ServiceDefinition:
    name: str
    handler: object
    description: str
    source: str


class ServiceRegistry:
    """Collect explicit definitions; discovery never creates permission grants."""

    def __init__(self):
        self._definitions = {}

    def register(self, *, name, handler, description, source="application"):
        if not SERVICE_NAME.fullmatch(name):
            raise ValueError(f"Invalid namespaced service identifier: {name!r}")
        if name in self._definitions:
            raise ValueError(f"Duplicate service identifier: {name}")
        if not iscoroutinefunction(handler):
            raise TypeError(f"Service {name} must have an async handler")
        params = signature(handler).parameters
        if "client_token" not in params:
            raise TypeError(f"Service {name} must declare client_token")
        if not isinstance(description, str) or not description.strip():
            raise ValueError(f"Service {name} needs a description")
        self._definitions[name] = ServiceDefinition(name, handler, description, source)

    @property
    def definitions(self):
        return tuple(self._definitions.values())

    def publish(self, server):
        """Register checked tools; every invocation authenticates and authorizes."""
        for definition in self.definitions:
            def make_guarded(item):
                @wraps(item.handler)
                async def guarded(*args, **kwargs):
                    # Bind against the public signature, including positional tokens.
                    bound = signature(item.handler).bind(*args, **kwargs)
                    token = bound.arguments.get("client_token")
                    client = await PrivilegeGate.authenticate_token(token)
                    await PrivilegeGate.verify_tool_permission(client, item.name)
                    return await item.handler(*args, **kwargs)

                return guarded

            server.tool(name=definition.name, description=definition.description)(
                make_guarded(definition)
            )


def discover_services(*, installed_apps=None):
    """Inspect only installed Django apps, importing an explicit services entry point."""
    registry = ServiceRegistry()
    for app in installed_apps if installed_apps is not None else apps.get_app_configs():
        if not module_has_submodule(app.module, "services"):
            continue
        module = import_module(f"{app.name}.services")
        register = getattr(module, "register_services", None)
        if register is None:
            continue
        if not callable(register):
            raise TypeError(f"{app.name}.services.register_services is not callable")
        register(registry)
    return registry
