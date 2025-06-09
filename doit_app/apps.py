# doit_app/apps.py

from django.apps import AppConfig

class DoitAppConfig(AppConfig): # <- Nombre de la clase
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'doit_app'         # <- Atributo 'name'
    verbose_name = "Doit App" # <- Opcional, pero bueno tenerlo