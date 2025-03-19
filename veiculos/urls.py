from django.contrib import admin
from django.urls import path, include

from veiculos import views

app_name = "veiculos"

urlpatterns = [
    path('', views.listar_abastecimentos, name='dashboard_veiculos'),
    path("abastecimento/novo/", views.registrar_abastecimento, name="registrar_abastecimento")
    
]