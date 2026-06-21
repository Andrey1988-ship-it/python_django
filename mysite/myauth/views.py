from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy


class CustomLogoutView(LogoutView):
    """Кастомный выход с перенаправлением на главную"""
    next_page = reverse_lazy('myauth:index')
    http_method_names = ['get', 'post', 'options']  # 👈 разрешаем GET


def index_view(request):
    """Главная страница"""
    return render(request, 'myauth/index.html')


def get_cookie_view(request):
    """Чтение данных из cookies"""
    cookie_value = request.COOKIES.get('my_cookie', 'Значение не установлено')
    return HttpResponse(f'🍪 Значение cookie: {cookie_value}')


def set_cookie_view(request):
    """Установка данных в cookies"""
    response = HttpResponse('🍪 Cookie установлено!')
    response.set_cookie('my_cookie', 'Hello from Django!', max_age=3600)
    return response


def get_session_view(request):
    """Чтение данных из session"""
    session_value = request.session.get('my_session', 'Значение не установлено')
    return HttpResponse(f'📦 Значение session: {session_value}')


def set_session_view(request):
    """Установка данных в session"""
    request.session['my_session'] = 'Hello from session!'
    return HttpResponse('📦 Session установлено!')