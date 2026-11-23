# Repository instructions

AGOS is a reusable Django package for governed MCP tools. Follow the documentation conventions from [AAD-docs](https://github.com/AADigitalBusiness/AAD-docs/blob/main/docs/HOW-DOCS-WORK.md).

## Read first

- [Documentation map](docs/00-map.md) — authoritative navigation.
- [Architecture](docs/03-architecture.md) — cross-app boundaries.
- [Operations](docs/08-operations.md) — local checks and packaging.
- [MCP overview](agos_services/apps/mcp_server/docs/01-overview.md) — canonical service keys.
- [Accepted decision 0001](agos_services/apps/mcp_server/docs/07-decisions/0001-service-namespaces.md).
- [Approved modular architecture](docs/07-decisions/0001-modular-python-boundaries.md), [execution](docs/07-decisions/0002-transport-independent-execution.md), [initial deployment](docs/07-decisions/0003-single-process-sse-deployment.md), and [Django target](docs/07-decisions/0004-django-52-compatibility.md).

## Rules

- Write technical docs and code in English. An optional Spanish page is named `name.es.md` next to the English source.
- Keep cross-app documents in root `docs/`; place app-specific pages in `<app>/docs/`. Every documentation folder has `__init__.py`.
- Write every Markdown page with a one-line purpose, a Mermaid diagram and a Next section.
- Keep one source of truth for each fact. Link instead of copying, and never hand-edit generated reference tables.
- Functional requirements for planned Python modules live exclusively in `docs/requirements/`. State the outcome and observable acceptance criterion, not code structure, algorithms, programming instructions, or implementation examples. Do not label proposed functionality as implemented.
- Commit names use `type(area): summary`. Only mark a design decision Accepted after owner approval.
- MCP tool IDs follow `provider.resource.action`. Registration, authorization and persisted grants must agree; never silently grant aliases. Resolve tool identity exclusively from the authenticated transport principal.
- Publish only explicitly registered callables from installed Django apps. App-level discovery is opt-in with `AGOS_ENABLE_SERVICE_DISCOVERY`; handlers require an injected `ctx: Context` and may not expose `client_token`.
- Do not add `aad_docs` to runtime dependencies until the Django 5.2 version requirement is reconciled. The accepted target is Django 5.2+; do not modify dependencies or claim migration completion from an ADR alone.
- Maintain the approved independent execution engine and single-process initial SSE hosting as target requirements. Documentation changes must not imply these have already been implemented.

## Checks

```bash
python -m pip install -e ".[test]"
python manage.py check
python manage.py makemigrations --check --dry-run
python -m pytest
python -m pip install build
python -m build
```

Check that the wheel contains per-app `docs/` pages and the grant migration before release.
