from django.shortcuts import render
from datetime import datetime


def product_list(request):
    # Контекст с объектами
    context = {
        'shop_name': 'Супер Маркет',
        'products': [
            {'id': 1, 'name': 'Ноутбук', 'price': 50000, 'in_stock': True, 'discount': 10},
            {'id': 2, 'name': 'Мышь', 'price': 1500, 'in_stock': True, 'discount': 0},
            {'id': 3, 'name': 'Клавиатура', 'price': 3000, 'in_stock': False, 'discount': 5},
            {'id': 4, 'name': 'Монитор', 'price': 25000, 'in_stock': True, 'discount': 15},
            {'id': 5, 'name': 'Наушники', 'price': 4500, 'in_stock': True, 'discount': 0},
        ],
        'current_time': datetime.now(),
        'visitor_name': 'Гость',
        'total_products': 5,
    }
    
    return render(request, 'shopapp/product_list.html', context)
