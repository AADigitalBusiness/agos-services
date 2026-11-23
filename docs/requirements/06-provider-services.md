# Provider service requirements

Define the obligations of external integrations such as Shopify and future GitHub or Coder services.

```mermaid
flowchart LR
  Catalog["Published capability"] --> Provider["Provider service"]
  Provider --> External["External system"]
  External --> Outcome["Recorded outcome"]
```

## Functional requirements

| ID | Requirement |
|---|---|
| PRV-01 | A provider shall expose only capabilities explicitly enabled and named in the service catalog. |
| PRV-02 | Service descriptions shall represent actual available business operations and their potential side effects. |
| PRV-03 | Provider requests shall operate only within the authenticated client's authorized organization, account or resource scope. |
| PRV-04 | Provider unavailability and authorization rejection shall be distinguishable from a successful business result. |
| PRV-05 | Read-only capabilities shall not create or change remote resources. Operations that modify remote state shall be identifiable to consumers. |
| PRV-06 | Provider credentials shall remain protected and shall not become visible through tool results or logs. |
| PRV-07 | Adding or disabling an independent provider shall not change the authorization semantics of an unrelated provider. |
| PRV-08 | Capability availability and prerequisites shall be observable to operators without implying that an unimplemented integration exists. |

## Validation and acceptance

| Requirement | Observable acceptance criterion |
|---|---|
| PRV-01, PRV-08 | Disabled or absent providers are absent from the active catalog; advertised operations work under their documented prerequisites. |
| PRV-02, PRV-05 | For every declared read/write operation, tests confirm its observable business effect and no unintended side effect. |
| PRV-03 | Cross-account and cross-organization resource requests fail without accessing the other account. |
| PRV-04 | Provider outage, invalid provider authorization and valid empty results are distinguishable. |
| PRV-06 | Audit and error outputs contain no reusable provider credentials. |
| PRV-07 | Disabling one provider does not alter another provider's grants or behavior. |

## Current scope

Shopify is the implemented reference provider. GitHub, Coder and others are prospective integrations, not current AGOS capabilities merely because their names appear in planning documents. The current Shopify capability set has one authoritative catalog in the [MCP app overview](../../agos_services/apps/mcp_server/docs/01-overview.md).

## Next

Read [Operations requirements](07-operations.md) and [Core requirements](01-core.md).
