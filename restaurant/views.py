from django.shortcuts import render
from .models import MenuItem, OrderItem
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
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages

def home_view(request):
    items = MenuItem.objects.select_related("category").all()
    username = request.user.username if request.user.is_authenticated else None
    return render(request, "restaurant/index.html", {"items": items, "username": username})


@csrf_exempt
def menu_page(request):
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


def cart_view(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        items = CartItem.objects.filter(cart=cart).select_related("menu_item")
        total = sum(item.menu_item.price * item.quantity for item in items)
        return render(request, "restaurant/cart.html", {"cart_items": items, "total": total})
    else:
        messages.info(request, "Please login to view your cart.")
        return redirect("login")


@csrf_exempt
@login_required
def remove_from_cart(request):
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        cart = get_object_or_404(Cart, user=request.user)
        cart_item = get_object_or_404(CartItem, cart=cart, menu_item_id=item_id)
        cart_item.delete()
        return JsonResponse({"message": "Item removed from cart"})

    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
@login_required
def update_cart_quantity(request):
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        action = request.POST.get("action")  # 'increase' or 'decrease'

        cart = get_object_or_404(Cart, user=request.user)
        cart_item = get_object_or_404(CartItem, cart=cart, menu_item_id=item_id)

        if action == "increase":
            cart_item.quantity += 1
        elif action == "decrease" and cart_item.quantity > 1:
            cart_item.quantity -= 1
        cart_item.save()

        total_price = sum(i.menu_item.price * i.quantity for i in CartItem.objects.filter(cart=cart))

        return JsonResponse({
            "quantity": cart_item.quantity,
            "item_total": cart_item.menu_item.price * cart_item.quantity,
            "cart_total": total_price,
        })

    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def checkout_view(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = cart.items.all()

    if not cart_items:
        messages.warning(request, "Your cart is empty.")
        return redirect('menu')

    order = Order.objects.create(user=request.user, status="pending")

    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            menu_item=cart_item.menu_item,
            quantity=cart_item.quantity
        )

    cart.items.all().delete()

    messages.success(request, f"Order #{order.id} placed successfully!")
    return redirect('home')


def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome {user.username} to Seafood Korner! 🐟")
            return redirect("home")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserCreationForm()

    return render(request, "restaurant/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect("home")  # Make sure this matches your home view name
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "restaurant/login.html", {"form": form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect("login")



