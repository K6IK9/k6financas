from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from core.views import Conta, Transacao

class Abastecimento(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    data = models.DateField(default=timezone.now)
    total_gasto = models.DecimalField(max_digits=10, decimal_places=2)
    litros = models.DecimalField(max_digits=6, decimal_places=2)
    preco_por_litro = models.DecimalField(max_digits=6, decimal_places=3)
    tipo_combustivel = models.CharField(
        max_length=20,
        choices=[
            ("gasolina", "Gasolina"),
            ("etanol", "Etanol"),
            ("gasolinaadt", "Gasolina Aditivada"),
        ],
    )
    km_atual = models.PositiveIntegerField()
    posto = models.CharField(max_length=200, blank=True, null=True)
    cidade = models.CharField(max_length=200, blank=True, null=True)
    metodo_pagamento = models.ForeignKey(Conta, on_delete=models.SET_NULL, null=True)
    observacao = models.TextField(blank=True, null=True)


    def __str__(self):
        return f"{self.data} - {self.tipo_combustivel} - R$ {self.total_gasto}"