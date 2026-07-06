from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = 'myauth'

urlpatterns = [
    # Главная страница профиля текущего пользователя
    path('about-me/', views.MyProfileView.as_view(), name='about_me'),

    # Список всех пользователей
    path('users/', views.UserListView.as_view(), name='user_list'),

    # Детальная страница пользователя (по username)
    path('user/<str:username>/', views.UserProfileDetailView.as_view(), name='user_detail'),

    # Обновление профиля пользователя (по username)
    path('user/<str:username>/update/', views.UpdateUserProfileView.as_view(), name='update_user_profile'),

    # Регистрация
    path('register/', views.RegisterView.as_view(), name='register'),

    # Вход
    path('login/', LoginView.as_view(template_name='myauth/login.html'), name='login'),

    # Выход (с редиректом на список пользователей или главную)
    path('logout/', LogoutView.as_view(next_page='/accounts/users/'), name='logout'),
    path('update-my-profile/', views.UpdateMyProfileView.as_view(), name='update_my_profile'),
]