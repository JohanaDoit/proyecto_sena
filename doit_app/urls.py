# doit_app/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import chat_view
from .views_calificaciones import calificar_reserva

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

    # Vistas de cambio de contraseña de Django (las dejas como están, son robustas)
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    path('perfil/editar/', views.editar_perfil_view, name='editar_perfil'), # Renombrado para claridad
    
    path('principal/', views.principal, name='principal'), # Dashboard principal para clientes
    path('reserva/', views.reserva, name='reserva'),
    path('mis_reservas/', views.mis_reservas_cliente, name='mis_reservas_cliente'), # Nueva vista
    path('busc_experto/', views.busc_experto, name='busc_experto'), # Si esta es para clientes buscando expertos

    # 'experto' ahora es el dashboard del experto, renombrado para mayor claridad
    path('experto/', views.experto_perfil, name='experto_perfil'),  # Nueva vista para el perfil del experto
    path('experto/dashboard/', views.dashboard_experto, name='dashboard_experto'), 
    path('experto/historial/', views.historial_experto, name='historial_experto'), # Renombrado para claridad
    path('experto/reserva/<int:reserva_id>/aceptar/', views.aceptar_reserva_experto, name='aceptar_reserva_experto'), # Nueva
    path('experto/reserva/<int:reserva_id>/rechazar/', views.rechazar_reserva_experto, name='rechazar_reserva_experto'), # Nueva

    # --- Vistas de Administrador ---
    path('admin/principal/', views.admin_principal, name='admin_principal'),
    path('admin/solicitudes/', views.solicitudes_admin, name='solicitudes_admin'),
    path('api/ciudades_por_pais/', views.ciudades_por_pais, name='ciudades_por_pais'),
    path('cancelar-reserva/<int:reserva_id>/', views.cancelar_reserva, name='cancelar_reserva'),
    path('chat/<int:receptor_id>/', chat_view, name='chat'),
    path('notificaciones/', views.notificaciones, name='notificaciones'),
]



urlpatterns += [
    path('reserva/<int:reserva_id>/calificar/', calificar_reserva, name='calificar_reserva'),
    # --- AJAX para sugerencias de búsqueda de expertos ---
    path('ajax/busc_experto_sugerencias/', views.busc_experto_sugerencias, name='busc_experto_sugerencias'),
    # --- AJAX para expertos por especialidad ---
    path('ajax/expertos_por_especialidad/', views.expertos_por_especialidad, name='expertos_por_especialidad'),
]

