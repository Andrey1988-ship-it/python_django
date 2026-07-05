from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shopapp.urls')),      # 👈 главная страница
    path('shop/', RedirectView.as_view(url='/', permanent=False)),  # 👈 редирект с /shop/ на /
    path('req/', include('requestdataapp.urls')),
    path('myauth/', include('myauth.urls')),
]