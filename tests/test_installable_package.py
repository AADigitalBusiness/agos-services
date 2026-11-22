"""Smoke checks for the installable distribution integration."""
from importlib import import_module
from importlib.util import find_spec


def test_django_modules_and_migrations_are_importable():
    """The installed package must expose the existing apps and migrations."""
    modules = (
        "apps.channels",
        "apps.auth",
        "apps.mcp_server",
        "apps.shopify_api",
        "apps.channels.migrations",
        "apps.channels.migrations.0001_initial",
        "apps.auth.migrations",
        "apps.auth.migrations.0001_initial",
        "agos_services",
    )
    for name in modules:
        assert find_spec(name) is not None, f"Missing package module: {name}"


def test_host_integration_imports():
    from agos_services.asgi import mount_mcp
    from agos_services.urls import urlpatterns

    assert callable(mount_mcp)
    assert urlpatterns
