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
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def home_view(request):
    items = MenuItem.objects.select_related("category").all()
    return render(request, "restaurant/index.html", {"items": items})

@csrf_exempt
def menu_page(request):
    """Displays all menu items and handles AJAX cart additions."""
    items = MenuItem.objects.select_related("category").all()
    return render(request, "restaurant/menu.html", {"items": items})





class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "price"]
    search_fields = ["name", "description"]
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


class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def create(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        menu_item_id = request.data.get("menu_item")
        quantity = request.data.get("quantity", 1)

        menu_item = MenuItem.objects.get(id=menu_item_id)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, menu_item=menu_item)

        if not created:
            cart_item.quantity += int(quantity)
        cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)




@login_required
def add_to_cart(request):

    if request.method == "POST":
        item_id = request.POST.get("item_id")
        menu_item = get_object_or_404(MenuItem, id=item_id)
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, menu_item=menu_item)

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return JsonResponse({
            "message": f"{menu_item.name} added to cart",
            "quantity": cart_item.quantity
        })

    return JsonResponse({"error": "Invalid request"}, status=400)
