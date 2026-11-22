# django-agos-services: install into an existing Django project

The pip distribution is `django-agos-services`. This is an initial installable package of the existing Django apps, not a published PyPI release.

## Install

```bash
python -m pip install "git+https://github.com/AADigitalBusiness/agos-services.git@<pinned-commit>"
```

## Django settings

Append the following to the host project's `INSTALLED_APPS`:

```python
INSTALLED_APPS += [
    "rest_framework",
    "oauth2_provider",
    "agos_services.apps.channels.apps.ChannelsConfig",
    "agos_services.apps.mcp_server.apps.McpServerConfig",
    "agos_services.apps.shopify_api.apps.ShopifyApiConfig",
    "agos_services.apps.auth.apps.AuthConfig",
]
MCP_AUTH_REQUIRED = True
```

Retain your host's existing database, middleware, authentication and logging configurations. OAuth2 and DRF settings should be configured according to the host requirements. For Shopify usage, configure `SHOPIFY_API_KEY`, `SHOPIFY_API_SECRET`, `SHOPIFY_STORE_DOMAIN`, `SHOPIFY_API_VERSION`, `SHOPIFY_REDIRECT_URI`, `SHOPIFY_SCOPES` and `MCP_SERVER_NAME` as needed.

## Optional HTTP routes

```python
from django.urls import include, path
urlpatterns += [path("agos/", include("agos_services.urls"))]
```

## MCP SSE transport

In the host's `asgi.py`:

```python
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
from django.core.asgi import get_asgi_application
from agos_services.asgi import mount_mcp
application = mount_mcp(get_asgi_application())
```

This serves SSE at `/mcp/sse` and messages at `/mcp/messages/`; they are not under the Django `agos/` prefix. Apply CORS settings at the host/deployment layer. Run `python manage.py migrate` to create tables.

## Limitations

- **Namespaced modules:** Django application modules now live in `agos_services.apps.*`. Historical Django app labels (`channels`, `apps_auth`, `mcp_server`, `shopify_api`) are preserved to avoid resetting migrations and content types. Update existing host imports and `INSTALLED_APPS` together with the package revision.
- **Shopify MCP tools are optional at registration time**, but Shopify still ships with the distribution.
- **Verification:** Successful runtime integration with third-party hosts and production deployment is not yet established. Validate the wheel and run CI before release.
- Never disable MCP authentication in production. Review token handling and client authorization before exposing the SSE endpoint.

## Embedding without Shopify

A host Django project may register only `agos_services.apps.channels.apps.ChannelsConfig` and `agos_services.apps.mcp_server.apps.McpServerConfig` for a generic MCP gateway. Configure `AGOS_ENABLE_SHOPIFY_TOOLS = False` (the default when this setting is absent) to avoid importing or registering Shopify tool handlers during MCP server startup. In the standalone project `config.settings`, Shopify tools remain enabled by default for backward compatibility. Shopify-specific routes and dependencies should not be mounted or configured when unused.

## Authentication safety

`MCP_AUTH_REQUIRED` must remain enabled; the development bypass is removed. Send credentials using `Authorization: Bearer ...` or `x-mcp-client-token`, not query-string parameters. The legacy UUID token remains stored directly in the database; token hashing, rotation, resource-scoped GitHub authorization require follow-up migrations before production rollout as a general-purpose security service.
