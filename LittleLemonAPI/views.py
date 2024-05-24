import datetime as dt

from django.contrib.auth.models import Group, User
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from . import filters
from .models import Cart, Category, MenuItem, Order, OrderItem
from .permissions import IsManager, is_delivery_crew, is_manager
from .serializers import (
    CartSerializer,
    CategorySerializer,
    MenuItemSerializer,
    OrderItemSerializer,
    OrderSerializer,
    UserSerializer,
)


@api_view(["GET", "POST"])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def categories(request):
    if request.method == "GET":
        items = Category.objects.all()
        serialized_items = CategorySerializer(items, many=True)
        return Response(serialized_items.data, status=status.HTTP_200_OK)
    else:
        if not is_manager(request):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            serialized = CategorySerializer(
                data=dict(
                    slug=request.POST.get("slug"),
                    title=request.POST.get("title"),
                )
            )
            if serialized.is_valid(raise_exception=True):
                serialized.save()
            return Response(serialized.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message": e}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsManager])
def item_of_day(request, pk: int):
    # Set item to featured
    item = get_object_or_404(MenuItem, id=pk)
    item.featured = True
    item.save()

    # Undo any other featured
    try:
        items = MenuItem.objects.filter(featured=True).exclude(id=pk)
        for item in items:
            serialized = MenuItemSerializer(
                item,
                data={"featured": False},
                partial=True,
            )
            if serialized.is_valid(raise_exception=True):
                item.save()
        return Response(status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"message": e}, status=status.HTTP_400_BAD_REQUEST)


class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.select_related("category").order_by("id")
    serializer_class = MenuItemSerializer
    ordering_fields = ["title", "price", "category__title"]
    search_fields = ["title", "category__title"]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    filterset_class = filters.MenuItemFilter

    def get_permissions(self):
        permission_classes = []
        if self.request.method != "GET":
            permission_classes = [IsManager]
        return [permission() for permission in permission_classes]


class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_permissions(self):
        permission_classes = []
        if self.request.method != "GET":
            permission_classes = [IsManager]
        return [permission() for permission in permission_classes]


class ManagerView(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsManager]
    ordering_fields = ["username"]

    def get_queryset(self):
        if self.request.method == "GET":
            return User.objects.filter(groups__name="Manager").order_by("id")
        else:
            return User.objects.all()

    def post(self, request, *args, **kwargs):
        try:
            user = get_object_or_404(
                self.get_queryset(),
                username=request.POST.get("username"),
            )
            group = get_object_or_404(Group, name="Manager")
            user.groups.add(group)
            return Response(
                {"message": f"user {user.username} added to group {group.name}"},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {"message": e, "post": request.POST}, status=status.HTTP_400_BAD_REQUEST
            )


class SingleManagerView(generics.DestroyAPIView):
    queryset = User.objects.filter(groups__name="Manager")
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsManager]

    def delete(self, request, username: str, *args, **kwargs):
        try:
            user = get_object_or_404(self.queryset, username=username)
            group = get_object_or_404(Group, name="Manager")
            user.groups.remove(group)
            return Response(
                {"message": f"user {user.username} removed from group {group.name}"},
                status=status.HTTP_200_OK,
            )
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class DeliveryCrewView(generics.ListCreateAPIView):
    queryset = User.objects.filter(groups__name="Delivery Crew")
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsManager]
    ordering_fields = ["username"]

    def post(self, request, *args, **kwargs):
        try:
            user = get_object_or_404(User, username=request.POST.get("username"))
            group = get_object_or_404(Group, name="Delivery Crew")
            user.groups.add(group)
            return Response(
                {"message": f"user {user.username} added to group {group.name}"},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"message": e}, status=status.HTTP_400_BAD_REQUEST)


class SingleDeliveryCrewView(generics.DestroyAPIView):
    # TODO: maybe an error shouldn't be raised if the user is not in the delivery crew
    queryset = User.objects.filter(groups__name="Delivery Crew")
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsManager]

    def delete(self, request, username: str, *args, **kwargs):
        try:
            user = get_object_or_404(self.queryset, username=username)
            group = get_object_or_404(Group, name="Delivery Crew")
            user.groups.remove(group)
            return Response(
                {"message": f"user {user.username} removed from group {group.name}"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"message": e}, status=status.HTTP_400_BAD_REQUEST)


class CartView(generics.ListCreateAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    ordering_fields = ["user", "menuitem", "price"]
    search_fields = ["menuitem__title", "menuitem__category__name"]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_queryset(self):
        return (
            Cart.objects.select_related("menuitem")
            .filter(user__username=self.request.user)
            .order_by("id")
        )

    def delete(self, request, *args, **kwargs):
        try:
            for object in self.get_queryset():
                object.delete()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": e}, status=status.HTTP_400_BAD_REQUEST)


class OrderView(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_queryset(self, request, *args, **kwargs):
        return Order.objects.select_related("user").order_by("id")

    def list(self, request):
        queryset = self.get_queryset(request)

        if is_manager(request):
            queryset = queryset.all()
        elif is_delivery_crew(request):
            queryset = queryset.filter(delivery_crew__username=request.user)
        else:
            queryset = queryset.filter(user__username=request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serialized = self.get_serializer(page, many=True)
            return self.get_paginated_response(serialized.data)
        else:
            serialized = self.get_serializer(queryset, many=True)
            return Response(serialized.data, status=status.HTTP_200_OK)

    def create(self, request):
        try:
            user = get_object_or_404(User, username=request.user)
            cart = Cart.objects.filter(user=user)

            # Make sure there are items in the cart
            if not cart.exists():
                return Response(
                    {"message": "No items in cart"}, status=status.HTTP_400_BAD_REQUEST
                )

            # TODO: Figure out why the serializer fails
            # data = {
            #     "total": sum([item.price for item in cart])
            # }
            # serialized = self.get_serializer(data)
            # serialized.save()

            order = Order.objects.create(
                user=user,
                total=sum([item.price for item in cart]),
            )

            # Add Cart Items to OrderItem
            for item in cart:
                serialized = OrderItemSerializer(
                    data=dict(
                        order_id=order.id,
                        menuitem_id=item.menuitem.id,
                        quantity=item.quantity,
                        unit_price=item.unit_price,
                    )
                )
                if serialized.is_valid(raise_exception=True):
                    serialized.save()

            # Remove items from cart
            cart = Cart.objects.filter(user__username=request.user)
            cart.delete()

            return Response(status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"message": e}, status=status.HTTP_400_BAD_REQUEST)


class SingleOrderView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def retrieve(self, request, orderId: int):
        items = OrderItem.objects.filter(
            order__user__username=request.user,
            order__id=orderId,
        )
        if len(items) == 0:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            serialized = OrderItemSerializer(items, many=True)
            return Response(serialized.data, status=status.HTTP_200_OK)

    def destroy(self, request, orderId: int):
        if not is_manager(request):
            return Response(status=status.HTTP_403_FORBIDDEN)

        item = get_object_or_404(OrderItem, id=orderId)
        item.delete()
        return Response(status=status.HTTP_200_OK)

    def update(self, request, orderId: int):
        if is_delivery_crew(request) or is_manager(request):
            if is_delivery_crew(request):
                keys = ["status"]
            else:
                keys = ["status", "delivery_crew_id"]

            try:
                data = {k: v for k, v in request.POST.items() if k in keys}
                order = get_object_or_404(Order, id=orderId)
                serialized = OrderSerializer(order, data=data, partial=True)
                if serialized.is_valid(raise_exception=True):
                    serialized.save()
                return Response(data=serialized.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"message": e}, status=status.HTTP_400_BAD_REQUEST)
