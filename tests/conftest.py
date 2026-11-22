import pytest
import uuid
from agos_services.apps.channels.models import MCPClient, ToolPermission
from agos_services.apps.auth.models import ShopifyStoreSession

@pytest.fixture
def active_mcp_client(db):
    client = MCPClient.objects.create(
        name="Test Claude Client",
        is_active=True,
        rate_limit_rpm=120,
    )
    # Grant permissions for products
    ToolPermission.objects.create(client=client, tool_name="shopify.products.list", allowed=True)
    ToolPermission.objects.create(client=client, tool_name="shopify.products.get", allowed=True)
    # Explicitly deny / ungranted for create_draft_order
    ToolPermission.objects.create(client=client, tool_name="shopify.draft_orders.create", allowed=False)
    return client

@pytest.fixture
def inactive_mcp_client(db):
    client = MCPClient.objects.create(
        name="Deactivated Client",
        is_active=False,
    )
    ToolPermission.objects.create(client=client, tool_name="get_products", allowed=True)
    return client

@pytest.fixture
def active_store_session(db):
    return ShopifyStoreSession.objects.create(
        shop_url="test-store.myshopify.com",
        access_token="shpat_test_token_12345",
        scopes="read_products,write_products,read_orders",
        is_active=True,
    )
