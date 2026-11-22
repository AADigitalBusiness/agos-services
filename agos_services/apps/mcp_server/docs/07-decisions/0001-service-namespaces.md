# 0001 · Namespaced service identifiers

Understand why every exposed service uses a provider-qualified name.

```mermaid
flowchart LR
    B["Before: get_products"] --> A["After: shopify.products.list"]
    A --> P["Exact ToolPermission key"]
```

**Status:** Accepted · 2026-11-22

## Context

Generic MCP names such as `get_products` collide when several Django applications provide similar tools. Permission grants cannot then clearly identify which provider is authorized.

## Decision

Register and authorize services by `provider.resource.action`. Use stable lowercase dot-separated identifiers such as `shopify.products.list` and `github.issues.create`. The registered name and the authorization key must be identical. Do not infer permission from discovery, installation or an old alias.

## Consequences

Existing Shopify grants must be migrated with their allow/deny values. Clients using old names must update their calls. This is a breaking MCP API change; no implicit compatibility aliases are exposed.

## Next

Read [MCP overview](../01-overview.md).
