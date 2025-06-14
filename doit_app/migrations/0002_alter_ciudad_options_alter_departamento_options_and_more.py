# Generated by Django 5.1.6 on 2025-06-11 01:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doit_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ciudad',
            options={'verbose_name': 'Ciudad', 'verbose_name_plural': 'Ciudades'},
        ),
        migrations.AlterModelOptions(
            name='departamento',
            options={'verbose_name': 'Departamento', 'verbose_name_plural': 'Departamentos'},
        ),
        migrations.AlterModelOptions(
            name='pais',
            options={'verbose_name': 'País', 'verbose_name_plural': 'Países'},
        ),
        migrations.AlterModelOptions(
            name='reserva',
            options={'verbose_name': 'Reserva', 'verbose_name_plural': 'Reservas'},
        ),
        migrations.AlterField(
            model_name='categorias',
            name='Nombre',
            field=models.CharField(max_length=50, unique=True, verbose_name='Nombre de la categoría'),
        ),
        migrations.AlterField(
            model_name='estado',
            name='Nombre',
            field=models.CharField(max_length=50, unique=True, verbose_name='Nombre del estado'),
        ),
        migrations.AlterField(
            model_name='metodo',
            name='Nombre',
            field=models.CharField(max_length=100, unique=True, verbose_name='Nombre del método de pago'),
        ),
        migrations.AlterField(
            model_name='pais',
            name='Nombre',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='tipodoc',
            name='Nombre',
            field=models.CharField(max_length=50, unique=True, verbose_name='Nombre del tipo de documento'),
        ),
    ]
