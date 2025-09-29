"""
URL configuration for seafood_korner project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from restaurant.views import menu, CategoryViewSet, MenuItemViewSet, OrderViewSet, UserViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# ✅ Define router before urlpatterns
router = DefaultRouter()
router.register("categories", CategoryViewSet)
router.register("menu", MenuItemViewSet)
router.register("orders", OrderViewSet, basename="orders")
router.register("users", UserViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", menu, name="menu"),  # Home menu view
    path("api/", include(router.urls)),  # API endpoints
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
