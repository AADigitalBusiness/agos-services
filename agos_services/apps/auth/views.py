import uuid
import hmac
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.views import View
from django.conf import settings
from asgiref.sync import sync_to_async
from .models import ShopifyStoreSession
from .services import ShopifyAuthService

class ShopifyInstallView(View):
    def get(self, request):
        shop = request.GET.get("shop") or settings.SHOPIFY_STORE_DOMAIN
        if not shop:
            return HttpResponseBadRequest("Missing required 'shop' parameter.")
        state = str(uuid.uuid4())
        request.session["shopify_oauth_state"] = state
        install_url = ShopifyAuthService.build_install_url(shop, state)
        return HttpResponseRedirect(install_url)


class ShopifyCallbackView(View):
    async def get(self, request):
        params = dict(request.GET.items())
        shop = params.get("shop")
        code = params.get("code")
        state = params.get("state")
        
        if not shop or not code or not state:
            return HttpResponseBadRequest("Missing Shopify OAuth callback parameters.")
        
        # Verify signature and consume the one-time session state before exchanging tokens.
        if not ShopifyAuthService.verify_hmac(params):
            return HttpResponseBadRequest("HMAC validation failed.")
        expected_state = await sync_to_async(request.session.pop)("shopify_oauth_state", None)
        if not expected_state or not hmac.compare_digest(str(expected_state), str(state)):
            return HttpResponseBadRequest("Invalid Shopify OAuth state.")
        
        try:
            token_data = await ShopifyAuthService.exchange_code_for_token(shop, code)
            access_token = token_data.get("access_token")
            scopes = token_data.get("scope", "")
            
            session_obj, _ = await sync_to_async(ShopifyStoreSession.objects.update_or_create)(
                shop_url=shop,
                defaults={
                    "access_token": access_token,
                    "scopes": scopes,
                    "is_active": True,
                }
            )
            
            return JsonResponse({
                "status": "success",
                "message": f"Shopify store {shop} successfully connected to hi-bel MCP gateway.",
                "scopes": scopes,
            })
        except Exception as exc:
            return JsonResponse({"error": str(exc)}, status=500)


class ShopifyStatusView(View):
    def get(self, request):
        sessions = list(ShopifyStoreSession.objects.filter(is_active=True).values("shop_url", "scopes", "installed_at", "updated_at"))
        return JsonResponse({
            "active_stores_count": len(sessions),
            "stores": sessions,
        })
