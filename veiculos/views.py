from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import AbastecimentoForm
from .models import Transacao

from django.contrib.auth.decorators import login_required
from .models import Abastecimento

def registrar_abastecimento(request):
    if request.method == "POST":
        form = AbastecimentoForm(request.POST)
        if form.is_valid():
            abastecimento = form.save(commit=False)
            abastecimento.usuario = request.user
            abastecimento.save()

            # Criar uma transação automaticamente
            Transacao.objects.create(
                descricao=f"Abastecimento ({abastecimento.tipo_combustivel})",
                valor=abastecimento.total_gasto,
                data=abastecimento.data,
                tipo="despesa",
                categoria="Combustivel",  # Pode definir uma categoria específica para abastecimento
                conta=abastecimento.metodo_pagamento,
                usuario=request.user,
                observacao=abastecimento.observacao,
            )

            messages.success(request, "Abastecimento registrado com sucesso!")
            return redirect("veiculos:dashboard_veiculos")  # Redireciona para a listagem

    else:
        form = AbastecimentoForm()

    return render(request, "veiculos/abastecimento_form.html", {"form": form})


@login_required
def listar_abastecimentos(request):
    abastecimentos = Abastecimento.objects.filter(usuario=request.user).order_by("-data")

    # Calculando estatísticas
    total_gasto = sum(a.total_gasto for a in abastecimentos)
    total_litros = sum(a.litros for a in abastecimentos)
    media_preco_litro = (total_gasto / total_litros) if total_litros > 0 else 0
    media_consumo = (
        sum(
            abastecimentos[i].km_atual - abastecimentos[i - 1].km_atual
            for i in range(1, len(abastecimentos))
        ) / total_litros
        if len(abastecimentos) > 1 and total_litros > 0
        else 0
    )

    context = {
        "abastecimentos": abastecimentos,
        "total_gasto": total_gasto,
        "total_litros": total_litros,
        "media_preco_litro": round(media_preco_litro, 2),
        "media_consumo": round(media_consumo, 2),
    }

    return render(request, "veiculos/dashboard_veiculo.html", context)