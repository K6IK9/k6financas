from django.contrib import admin
from django.urls import path, include

from usuarios import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('django.contrib.auth.urls')),  # Para autenticação
    path("registro/", views.registro, name="registro"),
]