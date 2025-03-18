
from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import (
    RegistroUsuarioForm,
)



def registro(request):
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request, "Registro realizado com sucesso! Bem-vindo ao sistema."
            )
            return redirect("core:dashboard")
    else:
        form = RegistroUsuarioForm()

    return render(request, "registration/registro.html", {"form": form})