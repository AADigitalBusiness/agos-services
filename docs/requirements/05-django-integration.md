# Django integration module requirements

Define how AGOS operates as a reusable, independently installable component inside Django projects.

```mermaid
flowchart LR
  Host["Django host"] --> AGOS["AGOS installation"]
  AGOS --> Apps["Installed applications"]
  Apps --> Docs["Application documentation"]
```

## Approved compatibility direction

[Decision 0004](../07-decisions/0004-django-52-compatibility.md) approves Django **5.2 or newer** as the future supported baseline, with a verified upper bound. AAD-docs compatibility is a required acceptance outcome. The present distribution still declares its existing dependency range until a separate implementation and compatibility validation is completed.

## Functional requirements

| ID | Requirement |
|---|---|
| DJG-01 | AGOS shall install into an independent Django host without requiring the standalone development project. |
| DJG-02 | Existing client identity and permission data shall remain valid through supported upgrades or have an explicit migration outcome. |
| DJG-03 | The host shall control enabled providers, allowed access and deployment configuration. Installing AGOS shall not expose a provider by default without required authorization. |
| DJG-04 | Applications shall expose their available services through the shared discovery contract without replacing the host's application lifecycle. |
| DJG-05 | Administrative views shall make grant state and client activation understandable while protecting sensitive credential material. |
| DJG-06 | The supported Django and Python versions shall be declared and verified, including documentation compatibility. |
| DJG-07 | Application documentation shall be discoverable under the AAD-docs conventions without duplicating generated model or route metadata. |
| DJG-08 | The future compatibility release shall support Django 5.2 or newer within an explicitly tested version range and shall identify the unsupported legacy baseline. |

## Validation and acceptance

| Requirement | Observable acceptance criterion |
|---|---|
| DJG-01 | A clean Django host installs the distributed package, applies migrations and exposes an available permitted service. |
| DJG-02 | Upgrade fixtures preserve expected grant outcomes; denied grants do not become allowed. |
| DJG-03, DJG-04 | A disabled provider remains unavailable, and an enabled but ungranted provider remains nonexecutable. |
| DJG-05 | An operator can inspect status and grants without obtaining reusable stored credentials. |
| DJG-06 | Supported combinations pass the declared compatibility checks; unsupported combinations are stated. |
| DJG-07 | AAD-docs can navigate the package documentation in a compatible host, with no duplicate authoritative descriptions of models. |
| DJG-08 | A clean Django 5.2 host passes installation, migrations, service invocation and AAD-docs navigation; every additional advertised Django version is tested and an older unsupported host is clearly identified. |

## Existing applications

The current `channels`, `mcp_server`, `shopify_api` and `auth` Django apps remain existing product boundaries. This specification covers the **shared integration requirement**; individual current behavior remains documented in their respective app overviews.

## Python module responsibilities

| Existing or planned module | Functional obligation | Verification |
|---|---|---|
| `apps/channels/` | Make client and grant states available to authorized operators (DJG-02, DJG-05). | Migration preserves allow/deny outcomes and excludes secret disclosure. |
| `apps/mcp_server/` | Expose the configured MCP service in the Django host (DJG-03, DJG-04). | Disabled services remain unavailable and ungranted calls are refused. |
| `apps/shopify_api/` | Support the installed Shopify business capabilities without governing other providers (DJG-03). | Shopify operations do not modify unrelated provider settings or grants. |
| `apps/auth/` | Respect authentication boundaries of provider connections (DJG-03, DJG-05). | Unauthorized provider access is refused without exposing credentials. |
| `checks.py` | Report incompatible or unsafe host conditions (DJG-06). | An unsupported configuration produces an actionable diagnostic. |
| `conf.py` | Make supported host options and enabled capabilities distinguishable (DJG-03, DJG-06). | The host can determine its enabled and disabled capabilities. |

## Next

Read [Provider service requirements](06-provider-services.md) and [Validation matrix](09-validation-matrix.md).
