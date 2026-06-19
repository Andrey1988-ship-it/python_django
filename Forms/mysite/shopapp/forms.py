from django.forms import ModelForm
from django.contrib.auth.models import Group
from .models import Product, Order


class GroupForm(ModelForm):
    """Форма для работы с группами пользователей"""

    class Meta:
        model = Group
        fields = ['name']


class ProductForm(ModelForm):
    """Форма для создания/обновления продукта"""

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'discount', 'archived']
        labels = {
            'name': 'Название',
            'description': 'Описание',
            'price': 'Цена',
            'discount': 'Скидка (%)',
            'archived': 'Архивирован',
        }


class OrderForm(ModelForm):
    """Форма для создания/обновления заказа"""

    class Meta:
        model = Order
        fields = ['user', 'delivery_address', 'promocode', 'products']
        labels = {
            'user': 'Пользователь',
            'delivery_address': 'Адрес доставки',
            'promocode': 'Промокод',
            'products': 'Товары',
        }