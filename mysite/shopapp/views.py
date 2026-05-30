from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Product, Order


def shop_index(request):
    """Главная страница со списком ссылок"""
    context = {
        'title': 'Магазин',
        'pages': [
            {'name': 'Товары', 'url': '/shop/products/', 'description': 'Список всех продуктов'},
            {'name': 'Заказы', 'url': '/shop/orders/', 'description': 'Список всех заказов'},
            {'name': 'Админ-панель', 'url': '/admin/', 'description': 'Управление данными'},
        ],
    }
    return render(request, 'shopapp/shop_index.html', context)


def products_list(request):
    """Список продуктов"""
    products = Product.objects.filter(is_active=True)
    context = {
        'title': 'Товары',
        'products': products,
        'total_products': products.count(),
    }
    return render(request, 'shopapp/products_list.html', context)


def orders_list(request):
    """Список заказов с загруженными пользователями и продуктами"""
    orders = Order.objects.select_related('user').prefetch_related('products').all()
    context = {
        'title': 'Заказы',
        'orders': orders,
        'total_orders': orders.count(),
    }
    return render(request, 'shopapp/orders_list.html', context)