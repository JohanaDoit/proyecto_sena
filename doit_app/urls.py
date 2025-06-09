# asistencia/urls.py

from django.urls import path
# from django.urls import path # Esta línea está duplicada, puedes borrar una
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login_view, name='login'),
    path('logout/', views.user_logout_view, name='logout'),
    path('login_experto/', views.login_experto, name='login_experto'),
    path('login_admin/', views.login_admin, name='login_admin'),
    path('principal/', views.principal, name='principal'),
    path('registrarse/', views.registrarse, name='registrarse'),
    path('regisexperto/', views.regisexperto, name='regisexperto'),
    path('modificar/', views.modificar, name='modificar'), 
    path('perfil/', views.editar_perfil_view, name='perfil'),
    path('busc_experto/', views.busc_experto, name='busc_experto'),
    path('admin_principal/', views.admin_principal, name='admin_principal'),
    path('solicitudes_admin/', views.solicitudes_admin, name='solicitudes_admin'),
    path('servicioAceptado/', views.servicioAceptado, name='servicioAceptado'),
    path('servicioAceptadoexpe/', views.servicioAceptadoexpe, name='servicioAceptadoexpe'),
    path('chat/', views.chat, name='chat'),
    path('servicioCancelado/', views.servicioCancelado, name='servicioCancelado'),
    path('servicioCanceladoexpe/', views.servicioCanceladoexpe, name='servicioCanceladoexpe'),
    path('reserva/', views.reserva, name='reserva'),
    path('terminos-condiciones/', views.terminos_condiciones, name='terminos_condiciones'),
    path('tratamiento-datos/', views.tratamiento_datos, name='tratamiento_datos'),
    path('experto/', views.experto, name='experto'),
    path('historial_experto/', views.historial_experto, name='historial_experto'),
    path('fin/', views.fin, name='fin'),
    path('normalizacion/', views.normalizacion, name='normalizacion'),
    path('modelo_relacional/', views.modelo_relacional, name='modelo_relacional'),
    path('sentenciasddl/', views.sentenciasddl, name='sentenciasddl'),
    path('sentencias_dml/', views.sentencias_dml, name='sentencias_dml'),
    path('diccionario_de_datos/', views.diccionario_de_datos, name='diccionario_de_datos'),
    path('diagrama_de_clases/', views.diagrama_de_clases, name='diagrama_de_clases'),
]