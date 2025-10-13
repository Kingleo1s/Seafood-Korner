from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, MenuItem, Order, OrderItem, Cart, CartItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class MenuItemSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source="category.name")

    class Meta:
        model = MenuItem
        fields = [
            "id", "name", "description", "ingredients",
            "price", "image", "category", "category_name"
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "menu_item", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user", "status", "created_at", "items"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class CartItemSerializer(serializers.ModelSerializer):
    # Add nested item detail for richer API response
    menu_item_detail = MenuItemSerializer(source="menu_item", read_only=True)
    total_price = serializers.ReadOnlyField()  # Comes from model property

    class Meta:
        model = CartItem
        fields = ["id", "menu_item", "menu_item_detail", "quantity", "total_price"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "user", "items", "total_amount"]

    def get_total_amount(self, obj):
        return sum(item.total_price for item in obj.items.all())
