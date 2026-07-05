from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = 'myauth'

urlpatterns = [
    path('about-me/', views.MyProfileView.as_view(), name='about_me'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('user/<str:username>/', views.UserProfileDetailView.as_view(), name='user_detail'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(template_name='myauth/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='/accounts/users/'), name='logout'),
]