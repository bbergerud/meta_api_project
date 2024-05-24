from django.urls import path

from . import views

urlpatterns = [
    path("categories", views.categories, name="categories"),
    path("cart/menu-items", views.CartView.as_view()),
    path("groups/delivery-crew/users", views.DeliveryCrewView.as_view()),
    path(
        "groups/delivery-crew/users/<str:username>",
        views.SingleDeliveryCrewView.as_view(),
    ),
    path("groups/manager/users", views.ManagerView.as_view()),
    path(
        "groups/manager/users/<str:username>",
        views.SingleManagerView.as_view(),
    ),
    path("menu-items/featured/<int:pk>", views.item_of_day),
    path("menu-items", views.MenuItemsView.as_view(), name="menu-items"),
    path("menu-items/<int:pk>", views.SingleMenuItemView.as_view()),
    path(
        "orders",
        views.OrderView.as_view(
            {
                "get": "list",
                "post": "create",
            }
        ),
    ),
    path(
        "orders/<int:orderId>",
        views.SingleOrderView.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "update",
                "delete": "destroy",
            }
        ),
    ),
]
