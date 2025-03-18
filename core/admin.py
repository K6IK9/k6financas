from django.contrib import admin
from .models import Categoria, Conta, Transacao, Meta, TipoConta

admin.site.register(Categoria)
admin.site.register(Conta)
admin.site.register(Transacao)
admin.site.register(Meta)
admin.site.register(TipoConta)
