from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    tipo = models.CharField(
        max_length=10, choices=[("receita", "Receita"), ("despesa", "Despesa")]
    )
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name_plural = "Categorias"


class TipoConta(models.Model):
    nome = models.CharField(max_length=100)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Tipo de Conta"
        verbose_name_plural = "Tipos de Conta"


class Conta(models.Model):
    nome = models.CharField(max_length=100)
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tipo = models.ForeignKey(TipoConta, on_delete=models.SET_NULL, null=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nome} - R$ {self.saldo}"


class Transacao(models.Model):
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField(default=timezone.now)
    tipo = models.CharField(
        max_length=10, choices=[("receita", "Receita"), ("despesa", "Despesa")]
    )
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    conta = models.ForeignKey(Conta, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    observacao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.descricao} - R$ {self.valor} ({self.data})"

    class Meta:
        verbose_name_plural = "Transações"
        ordering = ["-data"]  # Ordena do mais recente para o mais antigo

    def save(self, *args, **kwargs):
        # Verificar se é uma nova transação ou uma atualização
        is_new = self.pk is None  # Nova transação
        
        if not is_new:
            # Em caso de atualização, obter a versão anterior da transação
            try:
                antiga = Transacao.objects.get(pk=self.pk)
                
                # Somente reverter o efeito se o valor ou tipo mudou
                if antiga.valor != self.valor or antiga.tipo != self.tipo or antiga.conta != self.conta:
                    # Reverter o efeito anterior
                    if antiga.tipo == "receita":
                        antiga.conta.saldo -= antiga.valor
                    else:
                        antiga.conta.saldo += antiga.valor
                    antiga.conta.save()
                    
                    # Aplicar novo efeito
                    if self.tipo == "receita":
                        self.conta.saldo += self.valor
                    else:
                        self.conta.saldo -= self.valor
                    self.conta.save()
                
            except Transacao.DoesNotExist:
                # Se por algum motivo não encontrar a transação anterior, trata como nova
                is_new = True
        
        if is_new:  # Nova transação
            # Atualizar saldo da conta
            if self.tipo == "receita":
                self.conta.saldo += self.valor
            else:
                self.conta.saldo -= self.valor
            self.conta.save()
        
        super(Transacao, self).save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Reverter efeito da transação no saldo da conta antes de excluir
        if self.tipo == "receita":
            self.conta.saldo -= self.valor
        else:
            self.conta.saldo += self.valor
        self.conta.save()
        
        super(Transacao, self).delete(*args, **kwargs)


class Meta(models.Model):
    descricao = models.CharField(max_length=100)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_limite = models.DateField()
    concluida = models.BooleanField(default=False)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.descricao} - R$ {self.valor} (Até {self.data_limite})"

    class Meta:
        verbose_name_plural = "Metas"
