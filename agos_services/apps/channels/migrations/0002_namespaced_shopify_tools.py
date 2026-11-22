"""Migrate existing Shopify grants to stable provider-scoped tool names.

Existing explicit allow/deny values are retained; any existing canonical grant
wins on conflict. No new permissions are granted by this migration.
"""
from django.db import migrations


RENAMES = {
    "get_products": "shopify.products.list",
    "get_product_by_id": "shopify.products.get",
    "search_inventory": "shopify.inventory.search",
    "get_orders": "shopify.orders.list",
    "get_order_by_id": "shopify.orders.get",
    "create_draft_order": "shopify.draft_orders.create",
}


def forward(apps, schema_editor):
    Permission = apps.get_model("channels", "ToolPermission")
    for old, new in RENAMES.items():
        for grant in Permission.objects.using(schema_editor.connection.alias).filter(tool_name=old).iterator():
            if Permission.objects.using(schema_editor.connection.alias).filter(
                client_id=grant.client_id, tool_name=new
            ).exists():
                # Do not override an existing canonical decision.
                grant.delete()
            else:
                grant.tool_name = new
                grant.save(update_fields=["tool_name"])


class Migration(migrations.Migration):
    dependencies = [("channels", "0001_initial")]
    operations = [migrations.RunPython(forward, migrations.RunPython.noop)]
