# Generated by Django 5.1.6 on 2025-06-14 02:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doit_app', '0002_alter_ciudad_options_alter_departamento_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='foto_perfil',
            field=models.ImageField(blank=True, null=True, upload_to='perfil/', verbose_name='Foto de Perfil'),
        ),
    ]
