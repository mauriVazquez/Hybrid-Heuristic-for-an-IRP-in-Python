# Generated by Django 5.0 on 2023-12-12 02:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ZonaTransporte', '0002_remove_vehiculo_asignado_remove_vehiculo_disponible_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehiculo',
            name='zona',
            field=models.ForeignKey(default=None, help_text='Asignado a Zona', null=True, on_delete=django.db.models.deletion.CASCADE, to='ZonaTransporte.zona'),
        ),
    ]
