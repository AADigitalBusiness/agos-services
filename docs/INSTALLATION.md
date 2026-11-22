# django-agos-services: install into an existing Django project

The pip distribution is `django-agos-services`. This is an initial installable package of the existing Django apps, not a published PyPI release.

## Install

```bash
python -m pip install "git+https://github.com/AADigitalBusiness/agos-services.git@feature/django-installable-package"
```

## Django settings

Append the following to the host project's `INSTALLED_APPS`:

```python
INSTALLED_APPS += [
    "rest_framework",
    "oauth2_provider",
    "apps.channels.apps.ChannelsConfig",
    "apps.mcp_server.apps.McpServerConfig",
    "apps.shopify_api.apps.ShopifyApiConfig",
    "apps.auth.apps.AuthConfig",
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

- **Namespace collision:** The existing modules still reside under the generic `apps.*` namespace. Hosts already using an `apps` package can conflict; a full package relocation is required before general-purpose publication.
- **Shopify is still coupled to the MCP tools.** It is not an independently optional provider yet.
- **Verification:** Successful runtime integration with third-party hosts and production deployment is not yet established. Validate the wheel and run CI before release.
- Never disable MCP authentication in production. Review token handling and client authorization before exposing the SSE endpoint.
