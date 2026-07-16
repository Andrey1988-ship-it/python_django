from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
from .forms import OrderImportForm
import csv
from decimal import Decimal
from .models import Product, Order, ProductImage
from .admin_mixins import ExportAsCSVMixin


class OrderInline(admin.TabularInline):
    model = Product.orders.through



class ProductInline(admin.StackedInline):
    model = ProductImage


@admin.action(description="Archive products")
def mark_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=True)


@admin.action(description="Unarchive products")
def mark_unarchived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=False)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ExportAsCSVMixin):
    actions = [
        mark_archived,
        mark_unarchived,
        "export_csv",
    ]
    inlines = [
        OrderInline,
        ProductInline,
    ]
    # list_display = "pk", "name", "description", "price", "discount"
    list_display = "pk", "name", "description_short", "price", "discount", "archived"
    list_display_links = "pk", "name"
    ordering = "-name", "pk"
    search_fields = "name", "description"
    fieldsets = [
        (None, {
           "fields": ("name", "description"),
        }),
        ("Price options", {
            "fields": ("price", "discount"),
            "classes": ("wide", "collapse"),
        }),
        ("Extra options", {
            "fields": ("archived",),
            "classes": ("collapse",),
            "description": "Extra options. Field 'archived' is for soft delete",
        }),
        ("Images", {
            "fields": ("preview",),
        })
    ]

    def description_short(self, obj: Product) -> str:
        if len(obj.description) < 48:
            return obj.description
        return obj.description[:48] + "..."


# admin.site.register(Product, ProductAdmin)


# class ProductInline(admin.TabularInline):
class ProductInline(admin.StackedInline):
    model = Order.products.through


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [
        ProductInline,
    ]
    change_list_template = "shopapp/orders_changelist.html"
    list_display = "delivery_address", "promocode", "created_at", "user_verbose"

    def import_csv(self, request):
        if request.method == 'POST':
            form = OrderImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES['csv_file']
                reader = csv.DictReader(csv_file.read().decode().splitlines())
                for row in reader:
                    # предполагаем поля: user_id, delivery_address, promocode, product_ids (разделённые запятой)
                    order = Order.objects.create(
                        user_id=row['user_id'],
                        delivery_address=row['delivery_address'],
                        promocode=row.get('promocode', ''),
                    )
                    product_ids = [int(pid.strip()) for pid in row['product_ids'].split(',') if pid.strip()]
                    products = Product.objects.filter(pk__in=product_ids)
                    order.products.set(products)
                self.message_user(request, f"Orders imported successfully from {csv_file.name}")
                return redirect('..')  # обязательно возвращаем HttpResponse
        else:
            form = OrderImportForm()

        return render(request, 'admin/csv_form.html', {'form': form, 'title': 'Import Orders'})

    def get_urls(self):
        urls = super().get_urls()  # получаем стандартные URL админки
        my_urls = [
            path('import-csv/', self.import_csv, name='import_csv'),
        ]
        return my_urls + urls  # добавляем свои URL перед стандартными


    def get_queryset(self, request):
        return Order.objects.select_related("user").prefetch_related("products")

    def user_verbose(self, obj: Order) -> str:
        return obj.user.first_name or obj.user.username
