from django.urls import path
from . import views
from django.contrib.auth import views as auth_views # Importar las vistas de autenticación de Django

urlpatterns = [
    # --- Vistas Generales ---
    path('', views.home, name='home'),
    path('nosotros/', views.nosotros, name='nosotros'), 
    path('terminos-condiciones/', views.terminos_condiciones, name='terminos_condiciones'),
    path('tratamiento-datos/', views.tratamiento_datos, name='tratamiento_datos'),

    # --- Vistas de Autenticación y Registro ---
    path('login/', views.user_login_view, name='login'),
    path('logout/', views.user_logout_view, name='user_logout'), 
    path('login_experto/', views.login_experto, name='login_experto'),
    path('login_admin/', views.login_admin, name='login_admin'),
    path('registrarse/', views.registrarse, name='registrarse'),
    path('regisexperto/', views.regisexperto, name='regisexperto'),

    # Vistas de cambio de contraseña de Django
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    
    # --- Vistas de Perfil de Usuario ---
    path('modificar/', views.modificar, name='modificar'), 
    path('perfil/editar/', views.editar_perfil_view, name='editar_perfil'), 

    # --- Vistas de Cliente ---
    path('principal/', views.principal, name='principal'), 
    path('reserva/', views.reserva, name='reserva'),
    path('mis_reservas/', views.mis_reservas_cliente, name='mis_reservas_cliente'), 
    path('busc_experto/', views.busc_experto, name='busc_experto'), 

    # --- Vistas de Experto ---
    path('experto/dashboard/', views.dashboard_experto, name='dashboard_experto'), 
    path('experto/historial/', views.historial_experto, name='historial_experto'), 
    path('experto/reserva/<int:reserva_id>/aceptar/', views.aceptar_reserva_experto, name='aceptar_reserva_experto'), 
    path('experto/reserva/<int:reserva_id>/rechazar/', views.rechazar_reserva_experto, name='rechazar_reserva_experto'),

    # --- Vistas de Administrador ---
    path('admin/principal/', views.admin_principal, name='admin_principal'),
    path('admin/solicitudes/', views.solicitudes_admin, name='solicitudes_admin'),
    # NUEVAS URLs para la gestión de usuarios por el administrador
    path('admin/usuarios/', views.gestion_usuarios_admin, name='gestion_usuarios_admin'),
    path('admin/usuarios/<int:user_id>/aprobar/', views.aprobar_usuario, name='aprobar_usuario'),
    path('admin/usuarios/<int:user_id>/rechazar/', views.rechazar_usuario, name='rechazar_usuario'),

    # --- NUEVA URL para la página de espera de aprobación de expertos ---
    path('espera-aprobacion/', views.espera_aprobacion, name='espera_aprobacion'),

    # --- Vistas de Confirmación/Cancelación (si son genéricas, revisar si son necesarias) ---
    path('servicioAceptado/', views.servicioAceptado, name='servicioAceptado'), 
    path('servicioAceptadoexpe/', views.servicioAceptadoexpe, name='servicioAceptadoexpe'), 
    path('servicioCancelado/', views.servicioCancelado, name='servicioCancelado'), 
    path('servicioCanceladoexpe/', views.servicioCanceladoexpe, name='servicioCanceladoexpe'),

    # --- Otras Vistas (revisar si son necesarias o consolidar) ---
    path('chat/', views.chat, name='chat'), 
    path('fin/', views.fin, name='fin'), 

    # --- Vistas de Documentación/Contenido Estático (mantener si son informativas) ---
    path('normalizacion/', views.normalizacion, name='normalizacion'),
    path('modelo_relacional/', views.modelo_relacional, name='modelo_relacional'),
    path('sentenciasddl/', views.sentenciasddl, name='sentenciasddl'),
    path('sentencias_dml/', views.sentencias_dml, name='sentencias_dml'),
    path('diccionario_de_datos/', views.diccionario_de_datos, name='diccionario_de_datos'),
    path('diagrama_de_clases/', views.diagrama_de_clases, name='diagrama_de_clases'),
]