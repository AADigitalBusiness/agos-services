# Client channels and permissions

Learn how AGOS stores client identities and tool grants.

```mermaid
flowchart LR
    C["MCPClient"] --> P["ToolPermission"]
    P --> T["MCP tool key"]
```

An active `MCPClient` has a UUID token. `ToolPermission` stores an explicit allow/deny decision per client and canonical tool key. No grant means denial. Use Django Admin or the protected management API for provisioning.

For tool names, use `provider.resource.action`, such as `shopify.products.list`. These values must match the server registration exactly. Existing Shopify grant rows are renamed by migration `0002_namespaced_shopify_tools`; if both old and new names exist, the canonical record is preserved.

## Next

Review [architecture](../../../../docs/03-architecture.md) and [MCP service policy](../../mcp_server/docs/01-overview.md).
