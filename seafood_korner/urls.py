"""
URL configuration for a seafood_korner project.

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
from restaurant import views
from restaurant.views import (
    home_view,
    CategoryViewSet,
    MenuItemViewSet,
    OrderViewSet,
    UserViewSet,
    CartViewSet,
    add_to_cart,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import views as auth_views

router = DefaultRouter()
router.register("categories", CategoryViewSet)
router.register("menu", MenuItemViewSet)
router.register("orders", OrderViewSet, basename="orders")
router.register("users", UserViewSet)
router.register("cart", CartViewSet, basename="cart")

urlpatterns = [
    path("admin/", admin.site.urls),

    # HTML pages
    path("", home_view, name="home"),
    path("menu/", views.menu_page, name="menu"),
    path("add-to-cart/", add_to_cart, name="add_to_cart"),
    path("cart/", views.cart_view, name="cart"),
    path("remove-from-cart/", views.remove_from_cart, name="remove_from_cart"),
    path("update-cart/", views.update_cart_quantity, name="update_cart_quantity"),
    path("checkout/", views.checkout_view, name="checkout"),



    # API endpoints
    path("api/", include(router.urls)),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("login/", auth_views.LoginView.as_view(template_name="restaurant/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
