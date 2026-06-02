
from django.urls import path
from . import views

app_name = 'shopapp'

urlpatterns = [
    # Основные страницы
    path('', views.shop_index, name='shop_index'),
    path('products/', views.products_list, name='products_list'),
    path('orders/', views.orders_list, name='orders_list'),
    # Детали товара
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('order/create/', views.order_create, name='order_create'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),
    path('upload/', views.upload_file, name='upload_file'),
    path('upload/success/<int:file_id>/', views.upload_success, name='upload_success'),
    path('throttle-test/', views.throttle_test, name='throttle_test'),
]