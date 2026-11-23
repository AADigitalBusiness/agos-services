# Core module requirements

Specify the outcomes required of the service registry, discovery and service contract.

```mermaid
flowchart LR
  Installed["Installed applications"] --> Discover["Discover explicit services"]
  Discover --> Catalog["Validated catalog"]
  Catalog --> Execute["Authorized execution"]
```

## Functional requirements

| ID | Requirement |
|---|---|
| CORE-01 | The system shall discover only services deliberately published by installed and enabled applications. Merely installing a package shall never grant execution permission. |
| CORE-02 | Every published service shall have one stable and unique `provider.resource.action` identifier. Duplicate or malformed names shall be rejected without ambiguous selection. |
| CORE-03 | The catalog shall provide sufficient business-facing metadata to distinguish the service's purpose, permitted operations and availability. |
| CORE-04 | Service availability shall be deterministic for the same installed applications and configuration. A failing provider shall not silently replace another service. |
| CORE-05 | The core shall remain independent of individual external providers and of any particular agent or transport. |
| CORE-06 | Service changes shall have an explicit compatibility outcome so clients can detect removed or renamed capabilities. |
| CORE-07 | No service shall become executable solely because it appears in discovery results. |

## Validation and acceptance

| Requirement | Observable acceptance criterion |
|---|---|
| CORE-01, CORE-07 | An installed but unpublished service is absent; a published service without a grant cannot execute. |
| CORE-02 | Duplicate and malformed identifiers produce a visible registration failure and neither can be invoked ambiguously. |
| CORE-03 | A consumer can retrieve a catalog entry with a purpose and stable identifier. |
| CORE-04 | Repeat discovery under unchanged conditions produces the same usable catalog; a failing entry is reported explicitly. |
| CORE-05 | Two independent providers can be registered without provider-specific changes to the core contract. |
| CORE-06 | A changed or removed service is reported to consumers rather than silently accepting the previous identifier. |

## Exclusions

Core does not own credential storage, decide user permissions, maintain transport sessions or implement business operations.

## Python module responsibilities

| Planned module | Functional obligation | Verification |
|---|---|---|
| `core/registry.py` | Maintain a unique, inspectable catalog of active services (CORE-02, CORE-03). | Duplicate names fail and each active identifier is discoverable. |
| `core/discovery.py` | Find only explicitly available services from enabled installations (CORE-01, CORE-04). | Disabled and unpublished services remain unavailable across repeated discovery. |
| `core/contracts.py` | Establish consistent service identity and capability information for consumers (CORE-03, CORE-06). | Independent providers present comparable, nonambiguous service descriptions. |
| `core/exceptions.py` | Distinguish invalid catalog entries from unavailable services (CORE-04, CORE-06). | Operators and clients can identify the reason for each rejection. |
| `core/lifecycle.py` | Make enabling, disabling and withdrawing a service observable (CORE-06, CORE-07). | A withdrawn service cannot be executed or silently substituted. |

## Next

Read [Security requirements](02-security.md) and the [module scope](00-scope.md).
