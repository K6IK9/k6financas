from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("transacoes/", views.transacoes_lista, name="transacoes_lista"),
    path("transacoes/criar/", views.transacao_criar, name="transacao_criar"),
    path(
        "transacoes/editar/<int:pk>/", views.transacao_editar, name="transacao_editar"
    ),
    path(
        "transacoes/excluir/<int:pk>/",
        views.transacao_excluir,
        name="transacao_excluir",
    ),
    path("categorias/", views.categorias_lista, name="categorias_lista"),
    path("categorias/criar/", views.categoria_criar, name="categoria_criar"),
    path(
        "categorias/editar/<int:pk>/", views.categoria_editar, name="categoria_editar"
    ),
    path(
        "categorias/excluir/<int:pk>/",
        views.categoria_excluir,
        name="categoria_excluir",
    ),
    path("contas/", views.contas_lista, name="contas_lista"),
    path("contas/criar/", views.conta_criar, name="conta_criar"),
    path("contas/editar/<int:pk>/", views.conta_editar, name="conta_editar"),
    path("contas/excluir/<int:pk>/", views.conta_excluir, name="conta_excluir"),
    path("contas/transferencia/", views.transferencia, name="transferencia"),
    path("metas/", views.metas_lista, name="metas_lista"),
    path("metas/criar/", views.meta_criar, name="meta_criar"),
    path("metas/editar/<int:pk>/", views.meta_editar, name="meta_editar"),
    path("metas/excluir/<int:pk>/", views.meta_excluir, name="meta_excluir"),
    path("metas/depositar/<int:pk>/", views.meta_depositar, name="meta_depositar"),
    path("relatorios/", views.relatorios, name="relatorios"),
    
    
    # Tipos de Conta
    path("tipos-conta/", views.tipos_conta_lista, name="tipos_conta_lista"),
    path("tipos-conta/criar/", views.tipo_conta_criar, name="tipo_conta_criar"),
    path(
        "tipos-conta/<int:pk>/editar/",
        views.tipo_conta_editar,
        name="tipo_conta_editar",
    ),
    path(
        "tipos-conta/<int:pk>/excluir/",
        views.tipo_conta_excluir,
        name="tipo_conta_excluir",
    ),
]
