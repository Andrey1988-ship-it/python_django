from django.urls import path
from .views import (
    ShopIndexView,
    GroupslistView,
    OrdersListView,
    ProductsListView,
    ProductDetailsView,
    OrderDetailView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    ProductArchiveView,  # 👈 ДОБАВЛЕНО
    OrderCreateView,
    OrderUpdateView,
    OrderDeleteView,
)

app_name = "shopapp"

urlpatterns = [
    # Главная
    path("", ShopIndexView.as_view(), name="shop_index"),  # 👈 ИСПРАВЛЕНО (было index)

    # Группы
    path("groups/", GroupslistView.as_view(), name="groups_list"),

    # Продукты
    path("products/", ProductsListView.as_view(), name="products_list"),
    path("products/create/", ProductCreateView.as_view(), name="product_create"),
    path("products/<int:pk>/", ProductDetailsView.as_view(), name="product_detail"),  # 👈 ИСПРАВЛЕНО
    path("products/<int:pk>/update/", ProductUpdateView.as_view(), name="product_update"),
    path("products/<int:pk>/archive/", ProductArchiveView.as_view(), name="product_archive"),  # 👈 ДОБАВЛЕНО
    path("products/<int:pk>/delete/", ProductDeleteView.as_view(), name="product_delete"),  # 👈 ИСПРАВЛЕНО

    # Заказы
    path("orders/", OrdersListView.as_view(), name="orders_list"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order_detail"),  # 👈 ИСПРАВЛЕНО
    path("orders/create/", OrderCreateView.as_view(), name="order_create"),
    path("orders/<int:pk>/update/", OrderUpdateView.as_view(), name="order_update"),
    path("orders/<int:pk>/delete/", OrderDeleteView.as_view(), name="order_delete"),
]