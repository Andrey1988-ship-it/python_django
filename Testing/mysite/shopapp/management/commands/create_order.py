from django.contrib.auth.models import User
from django.core.management import BaseCommand
from shopapp.models import Order


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Create order with products")

        # Создаём пользователя admin, если его нет
        user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "is_staff": True,
                "is_superuser": True,
            }
        )
        if created:
            user.set_password("admin123")  # установите свой пароль
            user.save()
            self.stdout.write(self.style.SUCCESS("✅ Создан пользователь admin"))

        # Создаём заказ
        order, created = Order.objects.get_or_create(
            delivery_address="ul Pupkina, d 8",
            promocode="SALE123",
            user=user,
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"✅ Создан заказ {order}"))
        else:
            self.stdout.write(self.style.WARNING(f"⚠️ Заказ уже существует {order}"))