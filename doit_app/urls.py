# doit_app/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import chat_view   # Importar las vistas de autenticación de Django

urlpatterns = [
    # --- Vistas Generales ---
    path('', views.home, name='home'),
    path('nosotros/', views.nosotros, name='nosotros'), # Si tienes una vista de "nosotros"
    path('terminos-condiciones/', views.terminos_condiciones, name='terminos_condiciones'),
    path('tratamiento-datos/', views.tratamiento_datos, name='tratamiento_datos'),

    # --- Vistas de Autenticación y Registro ---
    path('login/', views.user_login_view, name='login'),
    path('logout/', views.user_logout_view, name='user_logout'), # ¡Cambiado 'logout' a 'user_logout'!    path('login_experto/', views.login_experto, name='login_experto'),
    path('login_admin/', views.login_admin, name='login_admin'),
    path('registrarse/', views.registrarse, name='registrarse'),
    path('regisexperto/', views.regisexperto, name='regisexperto'),

    # Vistas de cambio de contraseña de Django (las dejas como están, son robustas)
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    
    # --- Vistas de Perfil de Usuario ---
    # La vista 'modificar' ahora redirige a 'editar_perfil'.
    # Si 'modificar' es solo un menú o landing, déjalo así. Si es la página para editar, usa 'editar_perfil'.
    # Te recomiendo que 'modificar' sea el enlace al perfil.
    path('modificar/', views.modificar, name='modificar'), # Esta redireccionará a 'editar_perfil_view'
    path('perfil/editar/', views.editar_perfil_view, name='editar_perfil'), # Renombrado para claridad

    # --- Vistas de Cliente ---
    path('principal/', views.principal, name='principal'), # Dashboard principal para clientes
    path('reserva/', views.reserva, name='reserva'),
    path('mis_reservas/', views.mis_reservas_cliente, name='mis_reservas_cliente'), # Nueva vista
    path('busc_experto/', views.busc_experto, name='busc_experto'), # Si esta es para clientes buscando expertos


    # --- Vistas de Experto ---
    # 'experto' ahora es el dashboard del experto, renombrado para mayor claridad
    path('experto/dashboard/', views.dashboard_experto, name='dashboard_experto'), 
    path('experto/historial/', views.historial_experto, name='historial_experto'), # Renombrado para claridad
    path('experto/reserva/<int:reserva_id>/aceptar/', views.aceptar_reserva_experto, name='aceptar_reserva_experto'), # Nueva
    path('experto/reserva/<int:reserva_id>/rechazar/', views.rechazar_reserva_experto, name='rechazar_reserva_experto'), # Nueva

    # --- Vistas de Administrador ---
    path('admin/principal/', views.admin_principal, name='admin_principal'),
    path('admin/solicitudes/', views.solicitudes_admin, name='solicitudes_admin'),

    # --- Vistas de Confirmación/Cancelación (si son genéricas, revisar si son necesarias) ---
    path('servicioAceptado/', views.servicioAceptado, name='servicioAceptado'), # Podría ser un template con mensaje de éxito
    path('servicioAceptadoexpe/', views.servicioAceptadoexpe, name='servicioAceptadoexpe'), # Podría ser un template con mensaje de éxito
    path('servicioCancelado/', views.servicioCancelado, name='servicioCancelado'), # Podría ser un template con mensaje de éxito
    path('servicioCanceladoexpe/', views.servicioCanceladoexpe, name='servicioCanceladoexpe'), # Podría ser un template con mensaje de éxito

    # --- Otras Vistas (revisar si son necesarias o consolidar) ---
    path('fin/', views.fin, name='fin'), # ¿Es una página de finalización general?

    # --- Vistas de Documentación/Contenido Estático (mantener si son informativas) ---
    path('normalizacion/', views.normalizacion, name='normalizacion'),
    path('modelo_relacional/', views.modelo_relacional, name='modelo_relacional'),
    path('sentenciasddl/', views.sentenciasddl, name='sentenciasddl'),
    path('sentencias_dml/', views.sentencias_dml, name='sentencias_dml'),
    path('diccionario_de_datos/', views.diccionario_de_datos, name='diccionario_de_datos'),
    path('diagrama_de_clases/', views.diagrama_de_clases, name='diagrama_de_clases'),


    path('api/ciudades_por_pais/', views.ciudades_por_pais, name='ciudades_por_pais'),
    path('experto/reserva/aceptar/<int:reserva_id>/', views.aceptar_reserva_experto, name='aceptar_reserva_experto'),
    path('experto/reserva/rechazar/<int:reserva_id>/', views.rechazar_reserva_experto, name='rechazar_reserva_experto'),


    path('chat/<int:receptor_id>/', chat_view, name='chat'),


]

