from django.views.generic import ListView, DetailView, UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from .models import Profile
from .forms import ProfileForm


# === Страница "О себе" – профиль текущего пользователя + редактирование аватара ===
class MyProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'myauth/about_me.html'
    success_url = reverse_lazy('myauth:about_me')

    def get_object(self, queryset=None):
        # Возвращаем профиль текущего пользователя
        return self.request.user.profile


# === Список всех пользователей ===
class UserListView(ListView):
    model = User
    template_name = 'myauth/user_list.html'
    context_object_name = 'users'
    ordering = ['username']


# === Детальная страница пользователя (только просмотр) ===
class UserProfileDetailView(DetailView):
    model = User
    template_name = 'myauth/user_detail.html'
    context_object_name = 'user_obj'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.object.profile
        return context


# === Регистрация ===
class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'myauth/register.html'
    success_url = reverse_lazy('myauth:login')