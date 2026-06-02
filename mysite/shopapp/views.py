from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db import transaction
from .models import Product, Order, OrderItem, UploadedFile
from .cart import Cart
from .forms import OrderCreateForm, FileUploadForm
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import UploadedFile as DjangoUploadedFile



def shop_index(request):
    """Главная страница — список всех товаров"""
    products = Product.objects.filter(is_active=True, stock__gt=0)
    context = {
        'title': 'Магазин брелков',
        'products': products,  # ← Это ключ 'products', а не 'pages'
    }
    return render(request, 'shopapp/shop_index.html', context)


def products_list(request):
    """Список всех товаров"""
    products = Product.objects.filter(is_active=True)
    return render(request, 'shopapp/products_list.html', {'products': products})


def product_detail(request, product_id):
    """Детальная страница товара"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    return render(request, 'shopapp/product_detail.html', {'product': product})


@require_POST
def cart_add(request, product_id):
    """Добавление товара в корзину"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product=product, quantity=quantity, override_quantity=False)
    messages.success(request, f'Товар "{product.name}" добавлен в корзину')
    return redirect('shopapp:cart_detail')


def cart_remove(request, product_id):
    """Удаление товара из корзины"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.success(request, 'Товар удалён из корзины')
    return redirect('shopapp:cart_detail')


def cart_detail(request):
    """Просмотр корзины"""
    cart = Cart(request)
    return render(request, 'shopapp/cart.html', {'cart': cart})


def order_create(request):
    """Оформление заказа"""
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, 'Ваша корзина пуста')
        return redirect('shopapp:products_list')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                if request.user.is_authenticated:
                    order.user = request.user
                order.save()

                for item in cart:
                    OrderItem.objects.create(
                        order=order,
                        product=item['product'],
                        price=item['price'],
                        quantity=item['quantity'],
                    )
                    product = item['product']
                    product.stock -= item['quantity']
                    product.save()

                cart.clear()
                messages.success(request, f'Заказ #{order.id} успешно оформлен!')
                return redirect('shopapp:order_success', order_id=order.id)
    else:
        form = OrderCreateForm()

    return render(request, 'shopapp/order_create.html', {'cart': cart, 'form': form})


def order_success(request, order_id):
    """Страница успешного оформления заказа"""
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'shopapp/order_success.html', {'order': order})


def orders_list(request):
    """Список заказов пользователя"""
    if request.user.is_authenticated:
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
    else:
        orders = []
    return render(request, 'shopapp/orders_list.html', {'orders': orders})


# shopapp/views.py - исправленная upload_file

@login_required
def upload_file(request):
    """View для загрузки файлов"""
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            description = form.cleaned_data['description']

            # Создаем запись в БД
            file_record = UploadedFile(
                file=uploaded_file,
                description=description,
                uploaded_by=request.user
            )
            file_record.save()

            messages.success(request,
                             f'Файл "{uploaded_file.name}" успешно загружен! '
                             f'Размер: {uploaded_file.size / 1024:.1f} КБ'
                             )
            return redirect('shopapp:upload_file')
        else:
            # Если форма не валидна, показываем ошибки
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = FileUploadForm()

    # Получаем список загруженных файлов
    recent_files = UploadedFile.objects.all()[:10]

    context = {
        'form': form,
        'recent_files': recent_files,
        'title': 'Загрузка файлов',
    }
    return render(request, 'shopapp/upload_file.html', context)


def upload_success(request, file_id):
    """Страница успешной загрузки"""
    file_record = get_object_or_404(UploadedFile, id=file_id)
    return render(request, 'shopapp/upload_success.html', {'file': file_record})


def throttle_test(request):
    """Тестовая страница для проверки throttling"""
    return render(request, 'shopapp/throttle_test.html')