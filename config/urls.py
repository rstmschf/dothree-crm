from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/accounts/", include("accounts.urls")),
    path("api/clients/", include("clients.urls")),
    path("api/docs/", SpectacularSwaggerView.as_view(), name = "docs"),
    path("api/schema/", SpectacularAPIView.as_view(), name = "schema"),
    path("api/sales/", include("sales.urls")),
]
