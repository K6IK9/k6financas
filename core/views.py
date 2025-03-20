from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.db import transaction
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Categoria, Conta, Transacao, Meta, TipoConta
from .forms import (
    CategoriaForm,
    ContaForm,
    TransacaoForm,
    MetaForm,
    TransferenciaForm,
    TipoContaForm,
)  # Remova RegistroUsuarioForm
import datetime
from decimal import Decimal
import calendar


@login_required
def dashboard(request):
    # Obter o mês atual
    hoje = timezone.now().date()
    inicio_mes = hoje.replace(day=1)
    if hoje.month == 12:
        fim_mes = hoje.replace(year=hoje.year + 1, month=1, day=1) - datetime.timedelta(
            days=1
        )
    else:
        fim_mes = hoje.replace(month=hoje.month + 1, day=1) - datetime.timedelta(days=1)

    # Calcular saldo total
    contas = Conta.objects.filter(usuario=request.user)
    saldo_total = contas.aggregate(total=Sum("saldo")).get("total", 0) or 0

    # Obter totais do mês atual
    receitas_mes = (
        Transacao.objects.filter(
            usuario=request.user, tipo="receita", data__range=[inicio_mes, fim_mes]
        )
        .aggregate(total=Sum("valor"))
        .get("total", 0)
        or 0
    )

    despesas_mes = (
        Transacao.objects.filter(
            usuario=request.user, tipo="despesa", data__range=[inicio_mes, fim_mes]
        )
        .aggregate(total=Sum("valor"))
        .get("total", 0)
        or 0
    )

    # Transações recentes
    transacoes_recentes = Transacao.objects.filter(usuario=request.user).order_by(
        "-data"
    )[:5]

    # Metas pendentes
    metas_pendentes = Meta.objects.filter(
        usuario=request.user, concluida=False
    ).order_by("data_limite")

    # Dados para o gráfico de categorias
    categorias_despesa = Categoria.objects.filter(usuario=request.user, tipo="despesa")

    dados_categorias = []
    for categoria in categorias_despesa:
        total = (
            Transacao.objects.filter(
                usuario=request.user,
                categoria=categoria,
                data__range=[inicio_mes, fim_mes],
            )
            .aggregate(total=Sum("valor"))
            .get("total", 0)
            or 0
        )

        if total > 0:
            dados_categorias.append({"nome": categoria.nome, "total": float(total)})

    context = {
        "saldo_total": saldo_total,
        "receitas_mes": receitas_mes,
        "despesas_mes": despesas_mes,
        "saldo_mes": receitas_mes - despesas_mes,
        "transacoes_recentes": transacoes_recentes,
        "metas_pendentes": metas_pendentes,
        "mes_atual": hoje.strftime("%B %Y"),
        "dados_categorias": dados_categorias,
    }

    return render(request, "core/dashboard.html", context)


@login_required
def transacoes_lista(request):
    # Obtendo filtros da URL
    data_inicio = request.GET.get("data_inicio")
    data_fim = request.GET.get("data_fim")
    tipo = request.GET.get("tipo")
    categoria_id = request.GET.get("categoria")
    

    # Base da consulta
    transacoes = Transacao.objects.filter(usuario=request.user)

    # Aplicando filtros
    if data_inicio:
        transacoes = transacoes.filter(data__gte=data_inicio)

    if data_fim:
        transacoes = transacoes.filter(data__lte=data_fim)

    if tipo:
        transacoes = transacoes.filter(tipo=tipo)

    if categoria_id:
        transacoes = transacoes.filter(categoria_id=categoria_id)

    # Ordenação
    transacoes = transacoes.order_by("-data")

    # Paginação
    paginator = Paginator(transacoes, 20)  # 20 itens por página
    page_number = request.GET.get("page")
    transacoes_paginadas = paginator.get_page(page_number)

    # Obter categorias para o filtro
    categorias = Categoria.objects.filter(usuario=request.user)
    
    # Obter contas para o filtro
    contas = Conta.objects.filter(usuario=request.user)
    
    #obter 
    

    
    context = {
        "transacoes": transacoes_paginadas,
        "categorias": categorias,
        "contas": contas,
        "filtros": {
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "tipo": tipo,
            "categoria": categoria_id,
        },
    }

    return render(request, "core/transacoes_lista.html", context)



@login_required
def transacao_criar(request):
    if request.method == "POST":
        form = TransacaoForm(user=request.user, data=request.POST)
        categorias = Categoria.objects.filter(usuario=request.user)
        
        form.fields["categoria"].queryset = categorias
        if form.is_valid():
            transacao = form.save(commit=False)
            transacao.usuario = request.user
            transacao.save()  # O método save() do modelo agora cuida da atualização do saldo

            messages.success(request, "Transação registrada com sucesso!")
            return redirect("core:transacoes_lista")
    else:
        if request.method == 'GET':
            form = TransacaoForm()
            categorias = Categoria.objects.all()  # Garantindo que todas as categorias sejam carregadas
            context = {
                'form': form,
                'categorias': categorias,  # Adicionando categorias ao contexto
            }
        return render(request, 'core/transacao_form.html', context)

    return render(request, "core/transacao_form.html", {"form": form})


@login_required
def transacao_editar(request, pk):
    transacao = get_object_or_404(Transacao, pk=pk, usuario=request.user)

    if request.method == "POST":
        form = TransacaoForm(request.user, request.POST, instance=transacao)
        if form.is_valid():
            # O método save() do modelo agora verificará as mudanças e atualizará o saldo corretamente
            form.save()
            messages.success(request, "Transação atualizada com sucesso!")
            return redirect("core:transacoes_lista")
    else:
        form = TransacaoForm(request.user, instance=transacao)

    return render(request, "core/transacao_form.html", {"form": form, "editar": True})


@login_required
@transaction.atomic
def transacao_excluir(request, pk):
    transacao = get_object_or_404(Transacao, pk=pk, usuario=request.user)

    if request.method == "POST":
        transacao.delete()  # O método delete() do modelo já cuida de reverter o saldo
        messages.success(request, "Transação excluída com sucesso!")
        return redirect("core:transacoes_lista")

    return render(
        request, "core/transacao_confirmar_exclusao.html", {"transacao": transacao}
    )


@login_required
def categorias_lista(request):
    # Obter todas as categorias do usuário
    categorias = Categoria.objects.filter(usuario=request.user)

    # Obter estatísticas para cada categoria
    categorias_com_stats = []

    for categoria in categorias:
        # Contar transações
        total_transacoes = Transacao.objects.filter(
            usuario=request.user, categoria=categoria
        ).count()

        # Somar valores
        total_valor = (
            Transacao.objects.filter(usuario=request.user, categoria=categoria)
            .aggregate(total=Sum("valor"))
            .get("total", 0)
            or 0
        )

        categorias_com_stats.append(
            {
                "id": categoria.id,
                "nome": categoria.nome,
                "tipo": categoria.tipo,
                "total_transacoes": total_transacoes,
                "total_valor": total_valor,
            }
        )

    # Separar categorias por tipo
    categorias_receita = [c for c in categorias_com_stats if c["tipo"] == "receita"]
    categorias_despesa = [c for c in categorias_com_stats if c["tipo"] == "despesa"]

    context = {
        "categorias": categorias_com_stats,
        "categorias_receita": categorias_receita,
        "categorias_despesa": categorias_despesa,
    }

    return render(request, "core/categorias.html", context)


@login_required
def categoria_criar(request):
    if request.method == "POST":
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save(commit=False)
            categoria.usuario = request.user
            categoria.save()

            messages.success(request, "Categoria criada com sucesso!")
            return redirect("core:categorias_lista")
    else:
        form = CategoriaForm()

    return render(request, "core/categoria_form.html", {"form": form})


@login_required
def categoria_editar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk, usuario=request.user)

    if request.method == "POST":
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoria atualizada com sucesso!")
            return redirect("core:categorias_lista")
    else:
        form = CategoriaForm(instance=categoria)

    return render(request, "core/categoria_form.html", {"form": form, "editar": True})


@login_required
def categoria_excluir(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk, usuario=request.user)

    # Verificar se há transações associadas à categoria
    has_transacoes = Transacao.objects.filter(categoria=categoria).exists()

    if request.method == "POST":
        # Se houver transações, atualizar para categoria nula
        if has_transacoes:
            Transacao.objects.filter(categoria=categoria).update(categoria=None)

        categoria.delete()
        messages.success(request, "Categoria excluída com sucesso!")
        return redirect("core:categorias_lista")

    return render(
        request,
        "core/categoria_confirmar_exclusao.html",
        {"categoria": categoria, "has_transacoes": has_transacoes},
    )


@login_required
def contas_lista(request):
    # Obter todas as contas do usuário
    contas = Conta.objects.filter(usuario=request.user)

    # Calcular saldo total
    saldo_total = contas.aggregate(total=Sum("saldo")).get("total", Decimal("0.00"))

    # Obter a data de hoje para o formulário de transferência
    hoje = timezone.now().date()

    context = {"contas": contas, "saldo_total": saldo_total, "hoje": hoje}
    return render(request, "core/contas.html", context)


@login_required
def conta_criar(request):
    if request.method == "POST":
        form = ContaForm(data=request.POST, user=request.user)
        if form.is_valid():
            conta = form.save(commit=False)
            conta.usuario = request.user

            # Adicionar saldo inicial, garantindo que sempre seja Decimal
            saldo_inicial = form.cleaned_data.get("saldo_inicial", Decimal("0.00"))
            conta.saldo = saldo_inicial
            
            conta.save()
            messages.success(request, "Conta criada com sucesso!")
            return redirect("core:contas_lista")
    else:
        form = ContaForm(user=request.user)

    return render(request, "core/conta_form.html", {"form": form})


@login_required
def conta_editar(request, pk):
    conta = get_object_or_404(Conta, pk=pk, usuario=request.user)

    if request.method == "POST":
        form = ContaForm(request.POST, instance=conta)
        if form.is_valid():
            form.save()
            messages.success(request, "Conta atualizada com sucesso!")
            return redirect("core:contas_lista")
    else:
        form = ContaForm(instance=conta)

    return render(request, "core/conta_form.html", {"form": form, "editar": True})


@login_required
def conta_excluir(request, pk):
    conta = get_object_or_404(Conta, pk=pk, usuario=request.user)

    # Verificar se há transações associadas à conta
    has_transacoes = Transacao.objects.filter(conta=conta).exists()

    if request.method == "POST":
        # Não permitir exclusão se houver transações
        if has_transacoes:
            messages.error(request, "Não é possível excluir uma conta com transações!")
            return redirect("core:contas_lista")

        conta.delete()
        messages.success(request, "Conta excluída com sucesso!")
        return redirect("core:contas_lista")

    return render(
        request,
        "core/conta_confirmar_exclusao.html",
        {"conta": conta, "has_transacoes": has_transacoes},
    )


@login_required
@transaction.atomic
def transferencia(request):
    if request.method == "POST":
        form = TransferenciaForm(request.user, request.POST)
        if form.is_valid():
            conta_origem = form.cleaned_data["conta_origem"]
            conta_destino = form.cleaned_data["conta_destino"]
            valor = form.cleaned_data["valor"]
            data = form.cleaned_data["data"]
            descricao = form.cleaned_data["descricao"]

            # Criar transação de saída (despesa)
            transacao_saida = Transacao(
                descricao=f"{descricao} (Saída)",
                valor=valor,
                data=data,
                tipo="despesa",
                categoria=None,
                conta=conta_origem,
                usuario=request.user,
                observacao=f"Transferência para {conta_destino.nome}",
            )

            # Criar transação de entrada (receita)
            transacao_entrada = Transacao(
                descricao=f"{descricao} (Entrada)",
                valor=valor,
                data=data,
                tipo="receita",
                categoria=None,
                conta=conta_destino,
                usuario=request.user,
                observacao=f"Transferência de {conta_origem.nome}",
            )

            # Salvar transações (o método save() do modelo cuida da atualização dos saldos)
            transacao_saida.save()
            transacao_entrada.save()

            messages.success(request, "Transferência realizada com sucesso!")
            return redirect("core:contas_lista")
    else:
        form = TransferenciaForm(request.user)

    return render(request, "core/transferencia_form.html", {"form": form})


@login_required
def metas_lista(request):
    # Obter todas as metas do usuário
    metas = Meta.objects.filter(usuario=request.user).order_by(
        "concluida", "data_limite"
    )

    # Adicionar informações adicionais a cada meta
    hoje = timezone.now().date()
    contas = Conta.objects.filter(usuario=request.user)

    metas_com_info = []
    for meta in metas:
        # Calcular dias restantes
        if hoje <= meta.data_limite:
            dias_restantes = (meta.data_limite - hoje).days
        else:
            dias_restantes = 0

        # Calcular porcentagem de conclusão
        valor_atual = meta.valor_atual if hasattr(meta, "valor_atual") else Decimal("0")
        if meta.valor > 0:
            porcentagem = (valor_atual / meta.valor) * 100
        else:
            porcentagem = 0

        metas_com_info.append(
            {
                "id": meta.id,
                "descricao": meta.descricao,
                "valor_meta": meta.valor,
                "valor_atual": valor_atual,
                "valor_faltante": meta.valor - valor_atual,
                "data_limite": meta.data_limite,
                "concluida": meta.concluida,
                "dias_restantes": dias_restantes,
                "porcentagem_concluida": porcentagem,
            }
        )

    # Contagens e totais
    metas_ativas = sum(1 for m in metas_com_info if not m["concluida"])
    metas_concluidas = len(metas_com_info) - metas_ativas
    total_economizado = sum(m["valor_atual"] for m in metas_com_info)

    context = {
        "metas": metas_com_info,
        "contas": contas,
        "hoje": hoje,
        "metas_ativas": metas_ativas,
        "metas_concluidas": metas_concluidas,
        "total_economizado": total_economizado,
    }

    return render(request, "core/metas.html", context)


@login_required
def meta_criar(request):
    if request.method == "POST":
        form = MetaForm(request.POST)
        if form.is_valid():
            meta = form.save(commit=False)
            meta.usuario = request.user
            meta.save()

            # Registrar valor inicial se informado
            valor_inicial = form.cleaned_data.get("valor_inicial")
            if valor_inicial and valor_inicial > 0:
                # Lógica para registrar o valor inicial
                pass

            messages.success(request, "Meta criada com sucesso!")
            return redirect("core:metas_lista")
    else:
        form = MetaForm()

    return render(request, "core/meta_form.html", {"form": form})


@login_required
def meta_editar(request, pk):
    meta = get_object_or_404(Meta, pk=pk, usuario=request.user)

    if request.method == "POST":
        form = MetaForm(request.POST, instance=meta)
        if form.is_valid():
            form.save()
            messages.success(request, "Meta atualizada com sucesso!")
            return redirect("core:metas_lista")
    else:
        form = MetaForm(instance=meta)

    return render(request, "core/meta_form.html", {"form": form, "editar": True})


@login_required
def meta_excluir(request, pk):
    meta = get_object_or_404(Meta, pk=pk, usuario=request.user)

    if request.method == "POST":
        meta.delete()
        messages.success(request, "Meta excluída com sucesso!")
        return redirect("core:metas_lista")

    return render(request, "core/meta_confirmar_exclusao.html", {"meta": meta})


@login_required
@transaction.atomic
def meta_depositar(request, pk):
    meta = get_object_or_404(Meta, pk=pk, usuario=request.user)

    if request.method == "POST":
        valor = Decimal(request.POST.get("valor", 0))
        data = request.POST.get("data")
        conta_id = request.POST.get("conta")

        if valor <= 0:
            messages.error(request, "O valor deve ser maior que zero!")
            return redirect("core:metas_lista")

        # Atualizar meta
        meta.valor_atual = getattr(meta, "valor_atual", 0) + valor

        # Verificar se a meta foi concluída
        if meta.valor_atual >= meta.valor:
            meta.concluida = True
            meta.data_conclusao = timezone.now().date()

        meta.save()

        # Se uma conta foi selecionada, criar uma transação (o save() do modelo cuida do saldo)
        if conta_id:
            conta = get_object_or_404(Conta, pk=conta_id, usuario=request.user)
            
            # Registrar transação
            Transacao.objects.create(
                descricao=f"Depósito para meta: {meta.descricao}",
                valor=valor,
                data=data,
                tipo="despesa",
                categoria=None,
                conta=conta,
                usuario=request.user,
                observacao=f"Contribuição para meta: {meta.descricao}",
            )

        messages.success(request, "Valor adicionado à meta com sucesso!")
        return redirect("core:metas_lista")

    return redirect("core:metas_lista")


@login_required
def relatorios(request):
    tipo_relatorio = request.GET.get("tipo_relatorio", "mensal")
    data_inicio = request.GET.get("data_inicio")
    data_fim = request.GET.get("data_fim")

    # Data padrão: último ano
    hoje = timezone.now().date()
    if not data_inicio:
        data_inicio = (hoje - datetime.timedelta(days=365)).strftime("%Y-%m-%d")

    if not data_fim:
        data_fim = hoje.strftime("%Y-%m-%d")

    # Converter strings para datas
    data_inicio_obj = datetime.datetime.strptime(data_inicio, "%Y-%m-%d").date()
    data_fim_obj = datetime.datetime.strptime(data_fim, "%Y-%m-%d").date()

    # Base de dados
    transacoes = Transacao.objects.filter(
        usuario=request.user, data__range=[data_inicio_obj, data_fim_obj]
    )

    context = {
        "filtros": {
            "tipo_relatorio": tipo_relatorio,
            "data_inicio": data_inicio,
            "data_fim": data_fim,
        }
    }

    # Preparar dados específicos para cada tipo de relatório
    if tipo_relatorio == "mensal":
        # Lógica para relatório mensal
        meses = []
        dados_mensais = []

        # Determinar o intervalo de meses para o relatório
        data_atual = data_inicio_obj.replace(day=1)
        while data_atual <= data_fim_obj:
            ultimo_dia = calendar.monthrange(data_atual.year, data_atual.month)[1]
            fim_mes = data_atual.replace(day=ultimo_dia)

            # Obter dados do mês
            mes_nome = data_atual.strftime("%B %Y")

            receitas_mes = (
                transacoes.filter(
                    tipo="receita", data__gte=data_atual, data__lte=fim_mes
                )
                .aggregate(total=Sum("valor"))
                .get("total", 0)
                or 0
            )

            despesas_mes = (
                transacoes.filter(
                    tipo="despesa", data__gte=data_atual, data__lte=fim_mes
                )
                .aggregate(total=Sum("valor"))
                .get("total", 0)
                or 0
            )

            saldo_mes = receitas_mes - despesas_mes

            meses.append(mes_nome)
            dados_mensais.append(
                {
                    "mes": mes_nome,
                    "receitas": receitas_mes,
                    "despesas": despesas_mes,
                    "saldo": saldo_mes,
                }
            )

            # Avançar para o próximo mês
            if data_atual.month == 12:
                data_atual = data_atual.replace(year=data_atual.year + 1, month=1)
            else:
                data_atual = data_atual.replace(month=data_atual.month + 1)

        # Calcular totais
        total_receitas = sum(d["receitas"] for d in dados_mensais)
        total_despesas = sum(d["despesas"] for d in dados_mensais)
        total_saldo = total_receitas - total_despesas

        context["dados_mensais"] = dados_mensais
        context["total_receitas"] = total_receitas
        context["total_despesas"] = total_despesas
        context["total_saldo"] = total_saldo
        context["meses"] = meses

    elif tipo_relatorio == "categoria":
        # Lógica para relatório por categoria
        categorias_despesa = Categoria.objects.filter(
            usuario=request.user, tipo="despesa"
        )

        dados_categorias = []
        total_despesas = 0

        for categoria in categorias_despesa:
            total = (
                transacoes.filter(tipo="despesa", categoria=categoria)
                .aggregate(total=Sum("valor"))
                .get("total", 0)
                or 0
            )

            if total > 0:
                total_despesas += total
                qtd_transacoes = transacoes.filter(
                    tipo="despesa", categoria=categoria
                ).count()

                dados_categorias.append(
                    {
                        "nome": categoria.nome,
                        "total": total,
                        "transacoes": qtd_transacoes,
                    }
                )

        # Calcular porcentagens
        for categoria in dados_categorias:
            if total_despesas > 0:
                categoria["porcentagem"] = (categoria["total"] / total_despesas) * 100
            else:
                categoria["porcentagem"] = 0

        context["dados_categorias"] = dados_categorias
        context["total_despesas"] = total_despesas

    elif tipo_relatorio == "fluxo":
        # Lógica para relatório de fluxo de caixa
        fluxo_caixa = []
        saldo_acumulado = 0

        # Obter saldo inicial (antes do período de relatório)
        saldo_inicial_contas = 0
        if data_inicio_obj:
            # Obter todas as transações antes da data de início
            transacoes_anteriores = Transacao.objects.filter(
                usuario=request.user, data__lt=data_inicio_obj
            )

            # Calcular o impacto delas no saldo
            for t in transacoes_anteriores:
                if t.tipo == "receita":
                    saldo_inicial_contas += t.valor
                else:
                    saldo_inicial_contas -= t.valor

            # Adicionar entrada inicial ao fluxo
            fluxo_caixa.append(
                {
                    "data": data_inicio_obj,
                    "descricao": "Saldo inicial",
                    "categoria": "-",
                    "conta": "Todas as contas",
                    "entrada": 0,
                    "saida": 0,
                    "saldo": saldo_inicial_contas,
                }
            )

            saldo_acumulado = saldo_inicial_contas

        # Obter todas as transações ordenadas por data
        transacoes_fluxo = transacoes.order_by("data")

        for t in transacoes_fluxo:
            if t.tipo == "receita":
                entrada = t.valor
                saida = 0
                saldo_acumulado += t.valor
            else:
                entrada = 0
                saida = t.valor
                saldo_acumulado -= t.valor

            fluxo_caixa.append(
                {
                    "data": t.data,
                    "descricao": t.descricao,
                    "categoria": t.categoria.nome if t.categoria else "-",
                    "conta": t.conta.nome,
                    "entrada": entrada,
                    "saida": saida,
                    "saldo": saldo_acumulado,
                }
            )

        # Calcular totais
        total_entradas = sum(item["entrada"] for item in fluxo_caixa)
        total_saidas = sum(item["saida"] for item in fluxo_caixa)

        context["fluxo_caixa"] = fluxo_caixa
        context["total_entradas"] = total_entradas
        context["total_saidas"] = total_saidas
        context["saldo_final"] = saldo_acumulado

    return render(request, "core/relatorios.html", context)

@login_required
def tipos_conta_lista(request):
    tipos_conta = TipoConta.objects.filter(usuario=request.user)
    context = {"tipos_conta": tipos_conta}
    return render(request, "core/tipo_conta_lista.html", context)


@login_required
def tipo_conta_criar(request):
    if request.method == "POST":
        form = TipoContaForm(request.POST)
        if form.is_valid():
            tipo = form.save(commit=False)
            tipo.usuario = request.user
            tipo.save()
            messages.success(request, "Tipo de conta criado com sucesso!")
            return redirect("core:tipos_conta_lista")
    else:
        form = TipoContaForm()

    return render(request, "core/tipo_conta_form.html", {"form": form})


@login_required
def tipo_conta_editar(request, pk):
    tipo = get_object_or_404(TipoConta, pk=pk, usuario=request.user)

    if request.method == "POST":
        form = TipoContaForm(request.POST, instance=tipo)
        if form.is_valid():
            form.save()
            messages.success(request, "Tipo de conta atualizado com sucesso!")
            return redirect("core:tipos_conta_lista")
    else:
        form = TipoContaForm(instance=tipo)

    return render(request, "core/tipo_conta_form.html", {"form": form, "editar": True})


@login_required
def tipo_conta_excluir(request, pk):
    tipo = get_object_or_404(TipoConta, pk=pk, usuario=request.user)

    # Verificar se há contas associadas ao tipo
    has_contas = Conta.objects.filter(tipo=tipo).exists()

    if request.method == "POST" and not has_contas:
        tipo.delete()
        messages.success(request, "Tipo de conta excluído com sucesso!")
        return redirect("core:tipos_conta_lista")

    return render(
        request,
        "core/tipo_conta_confirmar_exclusao.html",
        {"tipo": tipo, "has_contas": has_contas},
    )