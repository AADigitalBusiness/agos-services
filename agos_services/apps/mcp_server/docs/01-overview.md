# MCP tools and service identifiers

Learn which service names are exposed by the gateway and how permissions are checked.

```mermaid
flowchart LR
    N["Canonical identifier"] --> M["MCP server registration"]
    M --> A["PrivilegeGate"]
    A --> H["Provider handler"]
```

The `server.py` registration name and `tools.py` authorization name must be identical. `PrivilegeGate.verify_tool_permission` denies absent grants.

| Canonical identifier | Provider action |
|---|---|
| `shopify.products.list` | List products |
| `shopify.products.get` | Get product |
| `shopify.inventory.search` | Search inventory |
| `shopify.orders.list` | List orders |
| `shopify.orders.get` | Get order |
| `shopify.draft_orders.create` | Create draft order |

These names replace the pre-namespace MCP identifiers. Grant migration is performed by the channels app. A naming key does not imply that other providers are installed: `github.issues.create` remains an example only.

## Application services

Hosts may enable explicit app-local discovery with `AGOS_ENABLE_SERVICE_DISCOVERY=True`. Only installed Django applications with a `services.register_services(registry)` entrypoint are considered; registration never creates permissions. See [register a service](05-guides/register-a-service.md).

## Next

Read [decision 0001](07-decisions/0001-service-namespaces.md) and the [application discovery proposal](07-decisions/0002-explicit-app-service-discovery.md).
