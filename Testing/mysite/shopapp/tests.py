from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from shopapp.models import Product, Order
import json


# ==================== ТЕСТ ДЛЯ OrderDetailView ====================

class OrderDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаём пользователя
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        # Добавляем разрешение на просмотр заказов
        content_type = ContentType.objects.get_for_model(Order)
        permission = Permission.objects.get(
            content_type=content_type,
            codename='view_order'
        )
        cls.user.user_permissions.add(permission)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().tearDownClass()

    def setUp(self):
        # Вход пользователя
        self.client.login(username='testuser', password='testpass123')
        # Создаём заказ
        self.order = Order.objects.create(
            user=self.user,
            delivery_address='ул. Пушкина, д. 10',
            promocode='TEST123'
        )

    def tearDown(self):
        self.order.delete()

    def test_order_details(self):
        url = reverse('shopapp:order_details', kwargs={'pk': self.order.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        # Проверяем, что в теле есть адрес и промокод
        content = response.content.decode()
        self.assertIn(self.order.delivery_address, content)
        self.assertIn(self.order.promocode, content)

        # Проверяем, что в контексте тот же заказ
        self.assertEqual(response.context['order'].pk, self.order.pk)


# ==================== ТЕСТ ДЛЯ OrdersExportView ====================

class OrdersExportTestCase(TestCase):
    fixtures = ['users.json', 'products.json', 'orders.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='staffuser',
            password='staffpass123',
            is_staff=True
        )

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().tearDownClass()

    def setUp(self):
        self.client.login(username='staffuser', password='staffpass123')

    def test_orders_export(self):
        url = reverse('shopapp:orders_export')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('orders', data)

        # Проверяем структуру данных
        for order_data in data['orders']:
            self.assertIn('id', order_data)
            self.assertIn('delivery_address', order_data)
            self.assertIn('promocode', order_data)
            self.assertIn('user_id', order_data)
            self.assertIn('product_ids', order_data)
            self.assertIsInstance(order_data['product_ids'], list)