from timeit import default_timer
from django.urls import reverse_lazy
from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.views import View
from .forms import GroupForm
from .models import Product, Order
from django.views.generic import (TemplateView, ListView, DetailView,
                                  CreateView, UpdateView, DeleteView)


class ShopIndexView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ('Laptop', 1999),
            ('Desktop', 2999),
            ('Smartphone', 999),
        ]
        context = {
            "time_running": default_timer(),
            "products": products,
        }
        return render(request, 'shopapp/shop-index.html', context=context)


class GroupslistView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "form": GroupForm(),
            "groups": Group.objects.prefetch_related('permissions').all(),
        }
        return render(request, 'shopapp/groups-list.html', context=context)

    def post(self, request: HttpRequest):
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect(request.path)


# ==================== ПРОДУКТЫ ====================

class ProductDetailsView(DetailView):
    template_name = "shopapp/products-details.html"
    model = Product
    context_object_name = 'product'


class ProductsListView(ListView):
    template_name = 'shopapp/products-list.html'
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)


class ProductCreateView(CreateView):
    model = Product
    fields = ['name', 'price', 'description', 'discount']
    template_name = 'shopapp/product_create_form.html'
    success_url = reverse_lazy('shopapp:products_list')


class ProductUpdateView(UpdateView):
    model = Product
    fields = ['name', 'price', 'description', 'discount']
    template_name = 'shopapp/product_update_form.html'

    def get_success_url(self):
        return reverse(
            'shopapp:product_detail',  # 👈 ИСПРАВЛЕНО (было product_details)
            kwargs={'pk': self.object.pk},
        )


class ProductArchiveView(DeleteView):  # 👈 ДОБАВЛЕНО
    """Архивация продукта (soft delete)"""
    model = Product
    template_name = 'shopapp/product_confirm_archive.html'
    success_url = reverse_lazy('shopapp:products_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class ProductDeleteView(DeleteView):
    """Полное удаление продукта"""
    model = Product
    template_name = 'shopapp/product_confirm_delete.html'
    success_url = reverse_lazy('shopapp:products_list')

    def delete(self, request, *args, **kwargs):  # 👈 ИСПРАВЛЕНО (было form_valid)
        self.object = self.get_object()
        self.object.delete()
        return HttpResponseRedirect(self.get_success_url())


# ==================== ЗАКАЗЫ ====================

class OrdersListView(ListView):
    template_name = 'shopapp/orders-list.html'
    context_object_name = 'orders'
    queryset = (
        Order.objects
        .select_related('user')
        .prefetch_related('products')
    )


class OrderDetailView(DetailView):
    template_name = 'shopapp/order-detail.html'
    context_object_name = 'order'
    queryset = (
        Order.objects
        .select_related('user')
        .prefetch_related('products')
    )


class OrderCreateView(CreateView):
    model = Order
    fields = ['delivery_address', 'promocode', 'user', 'products']
    template_name = 'shopapp/order_form.html'
    success_url = reverse_lazy('shopapp:orders_list')


class OrderUpdateView(UpdateView):
    model = Order
    fields = ['delivery_address', 'promocode', 'user', 'products']
    template_name = 'shopapp/order_form.html'

    def get_success_url(self):
        return reverse(
            'shopapp:order_detail',  # 👈 ИСПРАВЛЕНО (было order_details)
            kwargs={'pk': self.object.pk},
        )


class OrderDeleteView(DeleteView):
    model = Order
    template_name = 'shopapp/order_confirm_delete.html'
    success_url = reverse_lazy('shopapp:orders_list')