from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


class Product(models.Model):
    """Модель продукта/товара"""
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание', blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    quantity = models.PositiveSmallIntegerField(default=0, verbose_name='Количество на складе')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.price} ₽"


class Order(models.Model):
    """Модель заказа"""
    comment = models.TextField(verbose_name='Комментарий к заказу', blank=True)
    status = models.CharField(
        max_length=50,
        default='new',
        choices=[
            ('new', 'Новый'),
            ('processing', 'В обработке'),
            ('completed', 'Выполнен'),
            ('cancelled', 'Отменён'),
        ],
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='Пользователь')
    products = models.ManyToManyField(Product, related_name='orders', verbose_name='Товары')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ #{self.id} от {self.user.username} - {self.created_at.strftime('%d.%m.%Y')}"

    def get_total_price(self):
        return sum(product.price for product in self.products.all())