from django import forms
from .models import Categoria, Conta, Transacao, Meta, TipoConta


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nome", "tipo"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "tipo": forms.Select(attrs={"class": "form-select"}),
        }


class TipoContaForm(forms.ModelForm):
    class Meta:
        model = TipoConta
        fields = ["nome"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
        }


class ContaForm(forms.ModelForm):
    saldo_inicial = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )

    class Meta:
        model = Conta
        fields = ["nome", "tipo", "saldo_inicial"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            ""
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "saldo_inicial": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields["tipo"].queryset = TipoConta.objects.filter(usuario=user)


class TransacaoForm(forms.ModelForm):
    class Meta:
        model = Transacao
        fields = [
            "descricao",
            "valor",
            "data",
            "tipo",
            "categoria",
            "conta",
            "observacao",
        ]
        widgets = {
            "descricao": forms.TextInput(attrs={"class": "form-control"}),
            "valor": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "data": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "categoria": forms.Select(attrs={"class": "form-select"}),
            "conta": forms.Select(attrs={"class": "form-select"}),
            "observacao": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields["categoria"].queryset = Categoria.objects.filter(usuario=user)
            self.fields["conta"].queryset = Conta.objects.filter(usuario=user)


class MetaForm(forms.ModelForm):
    valor_inicial = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )

    class Meta:
        model = Meta
        fields = ["descricao", "valor", "data_limite"]
        widgets = {
            "descricao": forms.TextInput(attrs={"class": "form-control"}),
            "valor": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "data_limite": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
        }


class TransferenciaForm(forms.Form):
    conta_origem = forms.ModelChoiceField(
        queryset=Conta.objects.none(),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    conta_destino = forms.ModelChoiceField(
        queryset=Conta.objects.none(),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    valor = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )
    data = forms.DateField(
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"})
    )
    descricao = forms.CharField(
        initial="Transferência entre contas",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields["conta_origem"].queryset = Conta.objects.filter(usuario=user)
            self.fields["conta_destino"].queryset = Conta.objects.filter(usuario=user)

    def clean(self):
        cleaned_data = super().clean()
        conta_origem = cleaned_data.get("conta_origem")
        conta_destino = cleaned_data.get("conta_destino")
        valor = cleaned_data.get("valor")

        if conta_origem and conta_destino and conta_origem == conta_destino:
            raise forms.ValidationError(
                "A conta de origem e destino não podem ser a mesma."
            )

        if conta_origem and valor and conta_origem.saldo < valor:
            raise forms.ValidationError(
                f"Saldo insuficiente na conta {conta_origem.nome}."
            )

        return cleaned_data
