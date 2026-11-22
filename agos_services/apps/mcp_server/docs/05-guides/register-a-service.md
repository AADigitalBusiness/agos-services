# Register an application service

Use this guide to expose an explicitly registered, permission-controlled MCP tool from a Django application.

```mermaid
flowchart LR
  A["INSTALLED_APPS"] --> S["app/services/__init__.py"]
  S --> R["ServiceRegistry"]
  R --> G["PrivilegeGate"]
  G --> H["Async handler"]
```

## Before you start

Install AGOS in a Django host. The host must opt into discovery; adding a Python module does not grant permission.

## Steps

1. In `your_app/services/__init__.py` create an explicit registration entrypoint:

   ```python
   from mcp.server.mcpserver.context import Context

   async def ping(*, ctx: Context = None):
       return "pong"

   def register_services(registry):
       registry.register(
           name="example.health.ping",
           handler=ping,
           description="Diagnostic ping",
       )
   ```

2. Add `your_app` to `INSTALLED_APPS` and set `AGOS_ENABLE_SERVICE_DISCOVERY = True`. Retain `MCP_AUTH_REQUIRED = True`.

3. Create an active `MCPClient` and an allowed `ToolPermission` for `example.health.ping` in Django Admin. Without the explicit grant, calls fail.

4. Verify:

   ```bash
   python manage.py check
   python -m pytest tests/test_service_registry.py
   ```

## Result

The service is registered at MCP server creation only when discovery is enabled. The MCP SDK injects the per-request `Context`. AGOS resolves the active client from the verified HTTP principal and authorizes each invocation. The service must not request or accept `client_token` as a tool argument. Duplicate names, invalid identifiers and synchronous handlers raise errors rather than silently registering.

## Next

Read [decision 0002](../07-decisions/0002-explicit-app-service-discovery.md) for lifecycle and security limitations.
