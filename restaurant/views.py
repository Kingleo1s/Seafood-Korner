from django.shortcuts import render
from .models import MenuItem
from rest_framework import viewsets, permissions
from django.contrib.auth.models import User
from .models import Category, Order
from .serializers import (
    CategorySerializer, MenuItemSerializer, OrderSerializer, UserSerializer
)
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend


def menu(request):
    items = MenuItem.objects.all()
    return render(request, "restaurant/menu.html", {"menu_items": items})



class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "price"]  # filter by category or price
    search_fields = ["name", "description"]  # search by name or description
    ordering_fields = ["price", "name"]

    def get_permissions(self):
        # Staff can edit, customers can only view
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]



class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer



