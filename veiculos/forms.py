from django import forms
from .models import Abastecimento

class AbastecimentoForm(forms.ModelForm):
    class Meta:
        model = Abastecimento
        fields = [
            "data",
            "total_gasto",
            "litros",
            "preco_por_litro",
            "tipo_combustivel",
            "km_atual",
            "posto",
            "cidade",
            "metodo_pagamento",
            "observacao",
        ]
        widgets = {
            "data": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "total_gasto": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "litros": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "preco_por_litro": forms.NumberInput(attrs={"class": "form-control", "step": "0.001"}),
            "tipo_combustivel": forms.Select(attrs={"class": "form-control"}),
            "km_atual": forms.NumberInput(attrs={"class": "form-control"}),
            "posto": forms.TextInput(attrs={"class": "form-control"}),
            "cidade": forms.TextInput(attrs={"class": "form-control"}),
            "metodo_pagamento": forms.Select(attrs={"class": "form-control"}),
            "observacao": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
