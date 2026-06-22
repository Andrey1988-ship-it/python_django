from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = 'myauth'

urlpatterns = [
    # Главная страница
    path('', views.index_view, name='index'),

    # Вход
    path('login/', LoginView.as_view(
        template_name='myauth/login.html',
        redirect_authenticated_user=True,
        next_page='/',
    ), name='login'),

    # Выход
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),

    # Регистрация
    path('register/', views.register_view, name='register'),

    # Профиль
    path('profile/', views.profile_view, name='profile'),

    # Cookies
    path('cookie/get/', views.get_cookie_view, name='cookie_get'),
    path('cookie/set/', views.set_cookie_view, name='cookie_set'),

    # Session
    path('session/get/', views.get_session_view, name='session_get'),
    path('session/set/', views.set_session_view, name='session_set'),
]