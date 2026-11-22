# 0002 · Explicit service discovery inside Django apps

Evaluate how AGOS could discover provider-owned service definitions.

```mermaid
flowchart LR
    A["INSTALLED_APPS"] --> D["Find optional services package"]
    D --> R["Explicit registration"]
    R --> G["Permission gate"]
```

**Status:** Proposed · not implemented

## Context

A reusable gateway should not import every Python function as an executable MCP tool. A conventional `<app>/services/` package would let each installed Django application own its business logic.

## Proposed decision

After Django app initialization, inspect only installed applications for an optional `services` module with an explicit registration entry point. Validate unique `provider.resource.action` names, schemas and handlers before publishing them. Discovery must not grant permissions or perform database/network operations in `AppConfig.ready()`.

## Alternatives

A monolithic tool catalog prevents extension. Scanning and publishing arbitrary callables creates an unacceptable execution surface.

## Consequences

Requires a service registry API, collision handling, registration lifecycle tests and authorization integration. The current code still registers Shopify tools explicitly in `mcp_server/server.py`.

## Next

Follow [MCP overview](../01-overview.md) and implement this only with tests and an explicit approval for its runtime contract.
