import bleach
from django.contrib.auth.models import User
from rest_framework import serializers

from . import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]

    def validate(self, attrs):
        for k in ["username"]:
            attrs[k] = bleach.clean(attrs[k])
        return attrs


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ["id", "slug", "title"]

    def validate(self, attrs):
        for k in ["slug", "title"]:
            attrs[k] = bleach.clean(attrs[k])
        return attrs


class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = models.MenuItem
        fields = ["id", "title", "price", "featured", "category", "category_id"]

    def validate(self, attrs):
        for k in ["title"]:
            attrs[k] = bleach.clean(attrs[k])
        return attrs


class CartSerializer(serializers.ModelSerializer):
    user = UserSerializer(default=serializers.CurrentUserDefault())
    menuitem = MenuItemSerializer(read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)
    price = serializers.SerializerMethodField("calculate_price")

    class Meta:
        model = models.Cart
        fields = ["user", "menuitem", "menuitem_id", "quantity", "unit_price", "price"]

    def calculate_price(self, cart: models.Cart):
        return cart.quantity * cart.unit_price


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(default=serializers.CurrentUserDefault())
    delivery_crew = UserSerializer(read_only=True)
    delivery_crew_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = models.Order
        fields = [
            "user",
            "delivery_crew",
            "delivery_crew_id",
            "status",
            "total",
            "date",
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    order_id = serializers.IntegerField(write_only=True)
    menuitem = MenuItemSerializer(read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)
    price = serializers.SerializerMethodField("calculate_price")

    class Meta:
        model = models.OrderItem
        fields = [
            "order",
            "order_id",
            "menuitem",
            "menuitem_id",
            "quantity",
            "unit_price",
            "price",
        ]

    def calculate_price(self):
        return self.unit_price * self.quantity
