from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

api_urlpatterns = [
    path("auth/", include("core.urls")),
    path("user/", include("user_profile.urls")),
]

urlpatterns = [
    path(f"api/v{settings.API_VERSION}/", include(api_urlpatterns)),
    path("admin/", admin.site.urls),
]