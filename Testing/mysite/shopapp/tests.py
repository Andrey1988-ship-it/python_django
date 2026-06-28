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

class OrdersExportViewTestCase(TestCase):
    """
    Тестовый класс для OrdersExportView.
    Проверяет, что данные экспорта соответствуют данным из БД.
    """
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

        # Дополнительно создаем тестовые данные для точной проверки
        # Чтобы быть уверенными, что данные из фикстур + наши данные совпадают
        self.test_product1 = Product.objects.create(
            name='Test Product 1',
            price=100.50,
            description='Test description 1'
        )
        self.test_product2 = Product.objects.create(
            name='Test Product 2',
            price=200.75,
            description='Test description 2'
        )
        self.test_order = Order.objects.create(
            user=self.user,
            delivery_address='Test Address, 123',
            promocode='TEST456'
        )
        self.test_order.products.set([self.test_product1, self.test_product2])

    def tearDown(self):
        # Очищаем созданные тестовые данные
        self.test_order.delete()
        self.test_product1.delete()
        self.test_product2.delete()

    def test_orders_export_data_match(self):
        """
        Основной тест: проверяет, что данные экспорта заказов из API
        соответствуют данным, полученным напрямую из БД через ORM.

        Сравниваем полную структуру данных одним self.assertEqual
        """
        # 1. Получаем данные через HTTP запрос
        url = reverse('shopapp:orders_export')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        api_response = response.json()
        self.assertIn('orders', api_response)
        api_data = api_response['orders']

        # 2. Получаем данные из БД через ORM
        db_data = self._get_orders_from_db()

        # 3. Сортируем для стабильного сравнения (порядок может отличаться)
        api_data_sorted = sorted(api_data, key=lambda x: x['id'])
        db_data_sorted = sorted(db_data, key=lambda x: x['id'])

        # 4. Сравниваем данные целиком
        self.assertEqual(api_data_sorted, db_data_sorted)

    def _get_orders_from_db(self):
        """
        Формирует структуру данных из БД, аналогичную API ответу
        """
        # Используем те же запросы, что и в OrdersExportView
        orders = Order.objects.select_related('user').prefetch_related('products').all()

        orders_data = []
        for order in orders:
            orders_data.append({
                'id': order.pk,
                'delivery_address': order.delivery_address,
                'promocode': order.promocode,
                'user_id': order.user.pk,
                'product_ids': sorted([product.pk for product in order.products.all()]),
            })

        return sorted(orders_data, key=lambda x: x['id'])

    def test_orders_export_structure_only(self):
        """
        Дополнительный тест: проверка структуры данных (быстрый smoke-тест)
        """
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


# ==================== ДОПОЛНИТЕЛЬНЫЕ ТЕСТЫ ДЛЯ EDGE CASES ====================

class OrdersExportEdgeCasesTestCase(TestCase):
    """
    Тесты для проверки пограничных случаев экспорта
    """

    def setUp(self):
        self.staff_user = User.objects.create_user(
            username='staffuser2',
            password='staffpass123',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username='regularuser',
            password='regularpass123'
        )

        # Создаем заказы для разных пользователей
        self.order1 = Order.objects.create(
            user=self.staff_user,
            delivery_address='Address 1',
            promocode='PROMO1'
        )
        self.order2 = Order.objects.create(
            user=self.regular_user,
            delivery_address='Address 2',
            promocode='PROMO2'
        )

        # Добавляем продукты
        self.product = Product.objects.create(
            name='Test Product',
            price=99.99,
            description='Test'
        )
        self.order1.products.set([self.product])
        self.order2.products.set([self.product])

        self.client.login(username='staffuser2', password='staffpass123')

    def tearDown(self):
        self.order1.delete()
        self.order2.delete()
        self.product.delete()
        self.staff_user.delete()
        self.regular_user.delete()

    def test_export_with_empty_orders(self):
        """Тест экспорта когда нет заказов"""
        # Удаляем все заказы
        Order.objects.all().delete()

        url = reverse('shopapp:orders_export')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('orders', data)
        self.assertEqual(len(data['orders']), 0)

        # Проверяем через ORM
        db_data = self._get_orders_from_db()
        self.assertEqual(data['orders'], db_data)

    def test_export_with_orders_without_products(self):
        """Тест экспорта заказов без продуктов"""
        order_without_products = Order.objects.create(
            user=self.staff_user,
            delivery_address='Empty Order',
            promocode='EMPTY'
        )

        url = reverse('shopapp:orders_export')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        data = response.json()

        # Находим наш заказ в ответе
        order_data = next((o for o in data['orders'] if o['id'] == order_without_products.pk), None)
        self.assertIsNotNone(order_data)
        self.assertEqual(order_data['product_ids'], [])

        # Проверяем через ORM
        db_data = self._get_orders_from_db()
        self.assertEqual(data['orders'], db_data)

        order_without_products.delete()

    def test_access_for_non_staff(self):
        """Тест доступа для не-персонала"""
        self.client.logout()
        self.client.login(username='regularuser', password='regularpass123')

        url = reverse('shopapp:orders_export')
        response = self.client.get(url)

        # Должен быть редирект или 403
        self.assertIn(response.status_code, [302, 403])

    def test_access_for_anonymous(self):
        """Тест доступа для анонимного пользователя"""
        self.client.logout()

        url = reverse('shopapp:orders_export')
        response = self.client.get(url)

        # Должен быть редирект на логин
        self.assertEqual(response.status_code, 302)

    def _get_orders_from_db(self):
        """Вспомогательный метод для получения данных из БД"""
        orders = Order.objects.select_related('user').prefetch_related('products').all()

        orders_data = []
        for order in orders:
            orders_data.append({
                'id': order.pk,
                'delivery_address': order.delivery_address,
                'promocode': order.promocode,
                'user_id': order.user.pk,
                'product_ids': sorted([product.pk for product in order.products.all()]),
            })

        return sorted(orders_data, key=lambda x: x['id'])


# ==================== ТЕСТ С КОНКРЕТНЫМИ ДАННЫМИ ====================

class OrdersExportSpecificDataTestCase(TestCase):
    """
    Тест с конкретными, заранее известными данными
    """

    def setUp(self):
        self.staff_user = User.objects.create_user(
            username='staffuser3',
            password='staffpass123',
            is_staff=True
        )

        # Создаем продукты с конкретными ID
        self.product1 = Product.objects.create(
            id=999,
            name='Specific Product 1',
            price=50.00,
            description='Specific description 1'
        )
        self.product2 = Product.objects.create(
            id=888,
            name='Specific Product 2',
            price=75.50,
            description='Specific description 2'
        )

        # Создаем заказ с конкретными данными
        self.order = Order.objects.create(
            id=777,
            user=self.staff_user,
            delivery_address='Specific Address, 456',
            promocode='SPECIFIC123'
        )
        self.order.products.set([self.product1, self.product2])

        self.client.login(username='staffuser3', password='staffpass123')

    def tearDown(self):
        self.order.delete()
        self.product1.delete()
        self.product2.delete()
        self.staff_user.delete()

    def test_export_specific_data(self):
        """Тест с проверкой конкретных значений"""
        url = reverse('shopapp:orders_export')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        data = response.json()

        # Находим наш заказ
        order_data = next((o for o in data['orders'] if o['id'] == 777), None)
        self.assertIsNotNone(order_data)

        # Проверяем конкретные значения
        expected_order_data = {
            'id': 777,
            'delivery_address': 'Specific Address, 456',
            'promocode': 'SPECIFIC123',
            'user_id': self.staff_user.pk,
            'product_ids': [888, 999]  # Сортируем для стабильности
        }

        # Сортируем product_ids для сравнения
        order_data['product_ids'] = sorted(order_data['product_ids'])

        self.assertEqual(order_data, expected_order_data)

        # Полное сравнение всех данных
        db_data = self._get_orders_from_db()

        # Сортируем для стабильности
        api_data_sorted = sorted(data['orders'], key=lambda x: x['id'])
        db_data_sorted = sorted(db_data, key=lambda x: x['id'])

        # Сортируем product_ids в обоих наборах данных
        for item in api_data_sorted:
            item['product_ids'] = sorted(item['product_ids'])
        for item in db_data_sorted:
            item['product_ids'] = sorted(item['product_ids'])

        self.assertEqual(api_data_sorted, db_data_sorted)

    def _get_orders_from_db(self):
        """Вспомогательный метод для получения данных из БД"""
        orders = Order.objects.select_related('user').prefetch_related('products').all()

        orders_data = []
        for order in orders:
            orders_data.append({
                'id': order.pk,
                'delivery_address': order.delivery_address,
                'promocode': order.promocode,
                'user_id': order.user.pk,
                'product_ids': sorted([product.pk for product in order.products.all()]),
            })

        return sorted(orders_data, key=lambda x: x['id'])