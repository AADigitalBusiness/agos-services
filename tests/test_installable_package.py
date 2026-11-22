"""Smoke checks for the installable distribution integration."""
from importlib import import_module
from importlib.util import find_spec


def test_django_modules_and_migrations_are_importable():
    """The installed package must expose the existing apps and migrations."""
    modules = (
        "agos_services.apps.channels",
        "agos_services.apps.auth",
        "agos_services.apps.mcp_server",
        "agos_services.apps.shopify_api",
        "agos_services.apps.channels.migrations",
        "agos_services.apps.channels.migrations.0001_initial",
        "agos_services.apps.auth.migrations",
        "agos_services.apps.auth.migrations.0001_initial",
        "agos_services",
    )
    for name in modules:
        assert find_spec(name) is not None, f"Missing package module: {name}"


def test_host_integration_imports():
    from agos_services.asgi import mount_mcp
    from agos_services.urls import urlpatterns

    assert callable(mount_mcp)
    assert urlpatterns
