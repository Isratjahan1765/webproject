"""
SPHWMS URL Configuration

Root URL router that delegates to each Django app's URL configuration.
Follows clean separation of concerns — each app owns its own URL namespace.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # ── Frontend (Template-based) URLs ──────────────────────────────────
    path('', include('core.urls', namespace='core')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('products/', include('products.urls', namespace='products')),
    path('drivers/', include('drivers.urls', namespace='drivers')),
    path('arrivals/', include('arrivals.urls', namespace='arrivals')),
    path('inventory/', include('inventory.urls', namespace='inventory')),
    path('reports/', include('reports.urls', namespace='reports')),
    path('revenue/', include('revenue.urls', namespace='revenue')),
    path('pickups/', include('pickups.urls', namespace='pickups')),
    path('notifications/', include('notifications.urls', namespace='notifications')),

    # ── REST API URLs ───────────────────────────────────────────────────
    path('api/v1/products/', include('products.api_urls', namespace='api-products')),
    path('api/v1/drivers/', include('drivers.api_urls', namespace='api-drivers')),
    path('api/v1/arrivals/', include('arrivals.api_urls', namespace='api-arrivals')),
    path('api/v1/inventory/', include('inventory.api_urls', namespace='api-inventory')),
    path('api/v1/reports/', include('reports.api_urls', namespace='api-reports')),
    path('api/v1/revenue/', include('revenue.api_urls', namespace='api-revenue')),
    path('api/v1/pickups/', include('pickups.api_urls', namespace='api-pickups')),
    path('api/v1/notifications/', include('notifications.api_urls', namespace='api-notifications')),
    path('api/v1/accounts/', include('accounts.api_urls', namespace='api-accounts')),

    # DRF browsable API auth
    path('api-auth/', include('rest_framework.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
