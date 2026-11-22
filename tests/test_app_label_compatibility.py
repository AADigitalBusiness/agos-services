"""App labels and migration identities must survive a namespace relocation."""
from django.apps import apps


def test_historical_app_labels_remain_stable():
    expected = {
        "channels": "agos_services.apps.channels",
        "apps_auth": "agos_services.apps.auth",
        "mcp_server": "agos_services.apps.mcp_server",
        "shopify_api": "agos_services.apps.shopify_api",
    }
    for label, module in expected.items():
        assert apps.get_app_config(label).name == module


def test_existing_migration_dependencies_remain_resolvable():
    from django.db.migrations.loader import MigrationLoader

    loader = MigrationLoader(None)
    assert ("channels", "0001_initial") in loader.disk_migrations
    assert ("apps_auth", "0001_initial") in loader.disk_migrations
