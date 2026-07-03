from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView, UpdateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.urls import reverse_lazy, reverse
from .models import Profile
from .forms import ProfileForm
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView




class MyProfileView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'myauth/about_me.html'
    context_object_name = 'profile'

    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

# Обновление своего профиля (аватарки)
class UpdateMyProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'myauth/update_profile.html'
    success_url = reverse_lazy('myauth:about_me')

    def get_object(self):
        return self.request.user.profile

# Список всех пользователей
class UserListView(ListView):
    model = User
    template_name = 'myauth/user_list.html'
    context_object_name = 'users'
    ordering = ['username']

# Детальная страница пользователя (профиль)
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

# Обновление профиля любого пользователя (только для is_staff или владельца)
class UpdateUserProfileView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'myauth/update_profile.html'

    def get_object(self):
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username)
        return user.profile

    def test_func(self):
        # Проверка прав: is_staff или владелец
        profile = self.get_object()
        return self.request.user.is_staff or self.request.user == profile.user

    def get_success_url(self):
        return reverse('myauth:user_detail', kwargs={'username': self.object.user.username})

class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'myauth/register.html'
    success_url = reverse_lazy('myauth:login')