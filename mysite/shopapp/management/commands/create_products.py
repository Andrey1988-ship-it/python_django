from django.core.management.base import BaseCommand
from shopapp.models import Product


class Command(BaseCommand):
    help = 'Создание продуктов через get_or_create'

    def handle(self, *args, **options):
        products_data = [
            {'name': 'Ноутбук Dell XPS 13', 'description': 'Мощный ультрабук', 'price': 89999.99, 'quantity': 10},
            {'name': 'Мышь Logitech MX Master 3', 'description': 'Беспроводная мышь', 'price': 7999.00, 'quantity': 25},
            {'name': 'Клавиатура Mechanical', 'description': 'Механическая клавиатура', 'price': 5499.50, 'quantity': 15},
            {'name': 'Монитор Samsung 27"', 'description': '4K монитор', 'price': 29999.00, 'quantity': 5},
            {'name': 'Наушники Sony WH-1000XM5', 'description': 'Беспроводные наушники', 'price': 24999.00, 'quantity': 8},
        ]

        created = 0
        for data in products_data:
            product, is_created = Product.objects.get_or_create(
                name=data['name'],
                defaults={
                    'description': data['description'],
                    'price': data['price'],
                    'quantity': data['quantity'],
                }
            )
            if is_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f'✅ Создан: {product.name}'))

        self.stdout.write(self.style.SUCCESS(f'\n📊 Создано продуктов: {created}'))
