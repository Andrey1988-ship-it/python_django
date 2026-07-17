from timeit import default_timer
from django.core.cache import cache
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.http import (HttpResponse, HttpRequest, HttpResponseRedirect,
                       JsonResponse
                         )
from django.shortcuts import render, reverse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import (LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin)
from .forms import ProductForm
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from .serializers import ProductSerializer, OrderSerializer
from django.http import JsonResponse
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views import View
from .models import Product, Order
from django.contrib.syndication.views import Feed
from django.urls import reverse
from .models import Product
from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .serializers import OrderSerializer   # если у вас есть сериализатор

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = ['name','description']
    filterset_fields = [
        'name',
        'description',
        'price',
        'discount',
        'archived'
    ]
    ordering_fields = [
        'name',
        'price',
        'discount',
    ]


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


class ProductDetailsView(DetailView):
    template_name = "shopapp/products-details.html"
    model = Product
    queryset = Product.objects.prefetch_related('images')
    context_object_name = "product"


class ProductsListView(ListView):
    template_name = "shopapp/products-list.html"
    # model = Product
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)
    filterset_fields = ['name', 'price', 'archived']

class ProductCreateView(CreateView):
    model = Product
    fields = "name", "price", "description", "discount",'preview'
    success_url = reverse_lazy("shopapp:products_list")


class ProductUpdateView(UpdateView):
    model = Product
    #fields = "name", "price", "description", "discount",'preview'
    template_name_suffix = "_update_form"
    form_class = ProductForm

    def get_success_url(self):
        return reverse(
            "shopapp:product_details",
            kwargs={"pk": self.object.pk},
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        return response




class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrdersListView(LoginRequiredMixin, ListView):
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )


class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "shopapp.view_order"
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )


class OrdersExportView(UserPassesTestMixin, View):
    """Выгрузка заказов в JSON формате (только для is_staff)"""

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request, *args, **kwargs):
        orders = Order.objects.select_related('user').prefetch_related('products').all()

        orders_data = []
        for order in orders:
            orders_data.append({
                'id': order.pk,
                'delivery_address': order.delivery_address,
                'promocode': order.promocode,
                'user_id': order.user.pk,
                'product_ids': [product.pk for product in order.products.all()],
            })

        return JsonResponse({'orders': orders_data})

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.select_related('user').prefetch_related('products')
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['user', 'created_at', 'promocode']
    ordering_fields = ['created_at', 'user']
    ordering = ['-created_at']

class LatestProductsFeed(Feed):
    title = "Latest products"
    link = "/shop/products/"
    description = "Updates on products in our shop"

    def items(self):
        return Product.objects.order_by('-created_at')[:5]

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.description[:200]

    def item_link(self, item):
        return reverse('shopapp:product_details', kwargs={'pk': item.pk})

# ==================== USER ORDERS (с кешированием) ====================

class UserOrdersListView(LoginRequiredMixin, ListView):
    """Список заказов конкретного пользователя (только для авторизованных)"""
    model = Order
    template_name = 'shopapp/user_orders_list.html'
    context_object_name = 'orders'
    paginate_by = 10  # опционально

    def get_queryset(self):
        self.user_id = self.kwargs.get('user_id')
        self.owner = get_object_or_404(User, pk=self.user_id)

        cache_key = f'user_orders_data_{self.user_id}'
        orders = cache.get(cache_key)

        if orders is None:
            # Загружаем заказы с продуктами через prefetch_related
            orders = list(
                Order.objects
                .filter(user=self.owner)
                .order_by('pk')
                .prefetch_related('products')  # 👈 ДОБАВЛЯЕМ
            )
            cache.set(cache_key, orders, timeout=300)

        return orders

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['owner'] = self.owner  # передаём в шаблон как owner (не user)
        return context


class UserOrdersExportView(LoginRequiredMixin, View):
    """Экспорт заказов пользователя в JSON с низкоуровневым кешированием"""

    def get(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        # Проверяем существование пользователя
        user = get_object_or_404(User, pk=user_id)

        # Генерируем ключ кеша (уникальный для пользователя)
        cache_key = f'user_orders_export_{user_id}'
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            # Данные найдены в кеше – возвращаем их
            return JsonResponse(cached_data, safe=False)

        # Данных в кеше нет – загружаем из БД
        orders = Order.objects.filter(user=user).order_by('pk')
        # Используем имеющийся сериализатор
        serializer = OrderSerializer(orders, many=True)
        data = serializer.data
        print(f"[DEBUG] Saving cache for user {user_id} with {len(data)} orders")
        cache.set(cache_key, data, timeout=300)
        print(f"[DEBUG] Cache saved. Checking: {cache.get(cache_key)}")
        # Сохраняем в кеш на 5 минут (300 секунд)
        cache.set(cache_key, data, timeout=300)

        return JsonResponse(data, safe=False)