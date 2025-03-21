# Generated by Django 5.1.7 on 2025-03-19 01:59

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Abastecimento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(default=django.utils.timezone.now)),
                ('total_gasto', models.DecimalField(decimal_places=2, max_digits=10)),
                ('litros', models.DecimalField(decimal_places=2, max_digits=6)),
                ('preco_por_litro', models.DecimalField(decimal_places=3, max_digits=6)),
                ('tipo_combustivel', models.CharField(choices=[('gasolina', 'Gasolina'), ('etanol', 'Etanol'), ('gasolinaadt', 'Gasolina Aditivada')], max_length=20)),
                ('km_atual', models.PositiveIntegerField()),
                ('posto', models.CharField(blank=True, max_length=200, null=True)),
                ('cidade', models.CharField(blank=True, max_length=200, null=True)),
                ('observacao', models.TextField(blank=True, null=True)),
                ('metodo_pagamento', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.conta')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
