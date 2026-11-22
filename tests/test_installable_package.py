"""Smoke checks for the installable distribution integration."""
from pathlib import Path
from setuptools import find_namespace_packages


def test_packaging_includes_django_apps_and_migrations():
    root = Path(__file__).resolve().parents[1]
    names = set(find_namespace_packages(where=str(root), include=["apps*", "agos_services*"]))
    assert {"apps", "apps.channels", "apps.auth", "apps.mcp_server", "apps.shopify_api", "agos_services"} <= names
    assert "apps.channels.migrations" in names
    assert "apps.auth.migrations" in names


def test_host_integration_imports():
    from agos_services.asgi import mount_mcp
    from agos_services.urls import urlpatterns
    assert callable(mount_mcp)
    assert urlpatterns
