from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Profile



# ==================== ВЫХОД ====================

class CustomLogoutView(LogoutView):
    """Кастомный выход с перенаправлением на главную"""
    next_page = reverse_lazy('myauth:index')
    http_method_names = ['get', 'post', 'options']


# ==================== ГЛАВНАЯ СТРАНИЦА ====================

def index_view(request):
    """Главная страница"""
    return render(request, 'myauth/index.html')


# ==================== РЕГИСТРАЦИЯ ====================

def register_view(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('myauth:index')
    else:
        form = UserCreationForm()
    return render(request, 'myauth/register.html', {'form': form})


# ==================== ПРОФИЛЬ ====================

@login_required
def profile_view(request):
    """Профиль пользователя"""
    profile = request.user.profile
    return render(request, 'myauth/profile.html', {'profile': profile})


# ==================== COOKIES ====================

def get_cookie_view(request):
    """Чтение данных из cookies"""
    cookie_value = request.COOKIES.get('my_cookie', 'Значение не установлено')
    return HttpResponse(f'🍪 Значение cookie: {cookie_value}')


def set_cookie_view(request):
    """Установка данных в cookies"""
    response = HttpResponse('🍪 Cookie установлено!')
    response.set_cookie('my_cookie', 'Hello from Django!', max_age=3600)
    return response


# ==================== SESSION ====================

def get_session_view(request):
    """Чтение данных из session"""
    session_value = request.session.get('my_session', 'Значение не установлено')
    return HttpResponse(f'📦 Значение session: {session_value}')


def set_session_view(request):
    """Установка данных в session"""
    request.session['my_session'] = 'Hello from session!'
    return HttpResponse('📦 Session установлено!')

def register_view(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Автоматический вход после регистрации
            return redirect('myauth:index')
    else:
        form = UserCreationForm()
    return render(request, 'myauth/register.html', {'form': form})


@login_required
def profile_view(request):
    """Профиль пользователя"""
    profile = request.user.profile
    return render(request, 'myauth/profile.html', {'profile': profile})