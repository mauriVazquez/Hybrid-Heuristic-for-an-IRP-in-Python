# Generated by Django 5.0 on 2023-12-27 03:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Departamento',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name_plural': 'Departamentos',
            },
        ),
        migrations.CreateModel(
            name='Provincia',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name_plural': 'Provincias',
            },
        ),
        migrations.CreateModel(
            name='Localidad',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=255)),
                ('departamento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='localidades.departamento')),
            ],
            options={
                'verbose_name_plural': 'Localidades',
            },
        ),
        migrations.AddField(
            model_name='departamento',
            name='provincia',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='localidades.provincia'),
        ),
    ]