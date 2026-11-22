"""Regressions for canonical MCP service IDs and migrated grants."""
from importlib import import_module

import pytest
from django.db import connection
from django.test import override_settings

from agos_services.apps.channels.models import MCPClient, ToolPermission


NAMES = {
    "shopify.products.list",
    "shopify.products.get",
    "shopify.inventory.search",
    "shopify.orders.list",
    "shopify.orders.get",
    "shopify.draft_orders.create",
}


def test_mcp_server_registers_namespaced_tools():
    from agos_services.apps.mcp_server.server import create_mcp_server
    with override_settings(AGOS_ENABLE_SHOPIFY_TOOLS=True):
        server = create_mcp_server()
    # Assert registration names without relying on private MCP SDK attributes.
    import inspect
    source = inspect.getsource(create_mcp_server)
    assert server is not None
    for name in NAMES:
        assert 'name="' + name + '"' in source
    assert 'name="get_products"' not in source


@pytest.mark.django_db
def test_migration_preserves_grants_and_canonical_conflicts():
    migration = import_module(
        "agos_services.apps.channels.migrations.0002_namespaced_shopify_tools"
    )
    client = MCPClient.objects.create(name="Namespace migration fixture")
    legacy = ToolPermission.objects.create(
        client=client, tool_name="get_products", allowed=True
    )
    canonical = ToolPermission.objects.create(
        client=client, tool_name="shopify.products.get", allowed=False
    )
    ToolPermission.objects.create(
        client=client, tool_name="get_product_by_id", allowed=True
    )
    class SchemaEditor:
        connection = connection

    from django.apps import apps
    migration.forward(apps, SchemaEditor())
    assert ToolPermission.objects.filter(
        client=client, tool_name="shopify.products.list", allowed=True
    ).exists()
    canonical.refresh_from_db()
    assert canonical.allowed is False
    assert not ToolPermission.objects.filter(
        client=client, tool_name__in=["get_products", "get_product_by_id"]
    ).exists()
