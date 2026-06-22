from django.contrib import admin
from django.urls import path, include
from myauth.views import index_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('myauth.urls')),  # 👈 было 'auth/', стало 'accounts/'
    path('', index_view, name='home'),
    path('shop/', include('shopapp.urls')),
]