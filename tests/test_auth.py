import pytest
from agos_services.apps.auth.models import ShopifyStoreSession
from agos_services.apps.auth.services import ShopifyAuthService

@pytest.mark.django_db
class TestShopifyAuth:
    def test_store_session_creation(self, active_store_session):
        assert active_store_session.shop_url == "test-store.myshopify.com"
        assert active_store_session.is_active is True

    def test_build_install_url(self, settings):
        settings.SHOPIFY_API_KEY = "test_api_key"
        settings.SHOPIFY_SCOPES = "read_products"
        settings.SHOPIFY_REDIRECT_URI = "https://example.com/callback"

        url = ShopifyAuthService.build_install_url("demo.myshopify.com", "state123")
        assert "https://demo.myshopify.com/admin/oauth/authorize?" in url
        assert "client_id=test_api_key" in url
        assert "state=state123" in url

    def test_verify_hmac_validation(self, settings):
        settings.SHOPIFY_API_SECRET = "secret_key"
        import hmac
        import hashlib

        query = {"shop": "demo.myshopify.com", "timestamp": "123456"}
        sorted_str = "shop=demo.myshopify.com&timestamp=123456"
        computed = hmac.new(b"secret_key", sorted_str.encode("utf-8"), hashlib.sha256).hexdigest()
        
        valid_params = dict(query, hmac=computed)
        assert ShopifyAuthService.verify_hmac(valid_params) is True

        invalid_params = dict(query, hmac="wrong_signature")
        assert ShopifyAuthService.verify_hmac(invalid_params) is False

    def test_missing_hmac_secret_is_denied(self, settings):
        settings.SHOPIFY_API_SECRET = ""
        assert ShopifyAuthService.verify_hmac({
            "shop": "demo.myshopify.com",
            "timestamp": "123456",
            "hmac": "arbitrary",
        }) is False

    @pytest.mark.asyncio
    async def test_callback_rejects_invalid_state_before_token_exchange(self, settings):
        import hashlib
        import hmac
        from django.test import RequestFactory
        from agos_services.apps.auth.views import ShopifyCallbackView

        settings.SHOPIFY_API_SECRET = "secret_key"
        params = {
            "shop": "demo.myshopify.com",
            "code": "fake-code",
            "state": "unexpected-state",
        }
        signed = "&".join(f"{key}={value}" for key, value in sorted(params.items()))
        params["hmac"] = hmac.new(
            b"secret_key", signed.encode(), hashlib.sha256
        ).hexdigest()

        request = RequestFactory().get("/api/auth/shopify/callback/", data=params)
        request.session = {"shopify_oauth_state": "expected-state"}
        response = await ShopifyCallbackView.as_view()(request)

        assert response.status_code == 400
        assert b"Invalid Shopify OAuth state" in response.content
        assert "shopify_oauth_state" not in request.session
