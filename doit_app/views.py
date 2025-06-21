from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistroForm, PerfilUsuarioForm, ReservaForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Estado, Servicios, Categorias, Reserva, CustomUser # Asegúrate de importar CustomUser
from django.conf import settings
import requests
from django.db.models import Q

# --- Funciones de test para @user_passes_test (sin cambios, ya están bien) ---
def is_cliente(user):
    return user.is_authenticated and user.tipo_usuario == 'cliente' and user.is_active

def is_experto(user):
    # Un experto solo es "experto" si está autenticado, su tipo es 'experto' Y está activo (aprobado)
    return user.is_authenticated and user.tipo_usuario == 'experto' and user.is_active

def is_admin(user):
    return user.is_authenticated and user.is_staff and user.is_superuser # Mejor usar is_staff/is_superuser para admin, o añadir un tipo_usuario='admin' y comprobar is_active
    # Si tu admin es solo por tipo_usuario='admin' y quieres que también esté activo, sería:
    # return user.is_authenticated and user.tipo_usuario == 'admin' and user.is_active


# --- Vistas Generales ---

def home(request):
    return render(request, 'home.html')

@login_required
def principal(request):
    # Redirigir a los expertos y admins a sus propios dashboards si ya están logeados
    if request.user.tipo_usuario == 'experto':
        # Expertos NO aprobados deben ir a una página de espera
        if request.user.approval_status != 'APPROVED' or not request.user.is_active:
            return redirect('espera_aprobacion')
        return redirect('dashboard_experto')
    
    if request.user.tipo_usuario == 'admin':
        return redirect('admin_principal')

    # Lógica para clientes
    categorias = Categorias.objects.all()
    servicios = Servicios.objects.all()

    # Agrupar servicios por categoría
    servicios_por_categoria = {}
    for cat in categorias:
        servicios_por_categoria[cat.Nombre] = list(servicios.filter(idCategorias=cat))

    # Obtener las últimas 3 reservas del usuario cliente autenticado
    ultimas_reservas = Reserva.objects.filter(
        idUsuario=request.user
    ).exclude(
        Q(idEstado__Nombre='Cancelada') | Q(idEstado__Nombre='Completada')
    ).order_by('-Fecha', '-Hora')[:3]

    return render(request, 'principal.html', {
        'categorias': categorias,
        'servicios_por_categoria': servicios_por_categoria,
        'ultimas_reservas': ultimas_reservas,
    })

@login_required
@user_passes_test(is_cliente, login_url=reverse_lazy('login')) 
def reserva(request):
    servicio_id = request.GET.get('servicio_id') or request.session.get('servicio_id')

    if not servicio_id:
        messages.error(request, "⚠️ Servicio no seleccionado. Por favor, elige un servicio.")
        return redirect('principal')

    servicio = get_object_or_404(Servicios, id=servicio_id)
    request.session['servicio_id'] = servicio_id # Guardar en sesión para POST

    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.idUsuario = request.user
            reserva.idServicios = servicio
            
            try:
                estado_pendiente = Estado.objects.get(Nombre='Pendiente')
                reserva.idEstado = estado_pendiente
            except Estado.DoesNotExist:
                messages.error(request, "Error interno: El estado 'Pendiente' no se encontró en la base de datos. Contacta al administrador.")
                return redirect('principal')

            reserva.save()

            messages.success(request, '✅ ¡Tu reserva ha sido creada con éxito y está pendiente de un experto!')
            return redirect('principal')
        else:
            messages.error(request, '❌ Hubo un error al procesar tu reserva. Por favor, revisa los datos.')
            print(form.errors) 
    else:
        form = ReservaForm(initial={'idServicios': servicio})
    
    return render(request, 'reserva.html', {
        'form': form,
        'servicio': servicio
    })

@login_required
@user_passes_test(is_cliente, login_url=reverse_lazy('login'))
def mis_reservas_cliente(request):
    reservas = Reserva.objects.filter(idUsuario=request.user).order_by('-creado_en')
    return render(request, 'cliente/mis_reservas.html', {'reservas': reservas})


@login_required
def busc_experto(request):
    # Esta vista podría listar expertos disponibles o buscar expertos por especialidad
    # Por ahora, solo renderiza el template.
    return render(request, 'busc_experto.html')

@login_required
def modificar(request):
    # Esta es solo una redirección, lo cual es redundante.
    # El enlace en tus templates debe apuntar directamente a 'editar_perfil'.
    return redirect('editar_perfil')

@login_required
def servicioAceptado(request):
    return render(request, 'servicioAceptado.html')

@login_required
def servicioAceptadoexpe(request):
    return render(request, 'servicioAceptadoexpe.html')

@login_required
def chat(request):
    return render(request, 'chat.html')

@login_required
def servicioCancelado(request):
    return render(request, 'servicioCancelado.html')

@login_required
def servicioCanceladoexpe(request):
    return render(request, 'servicioCanceladoexpe.html')

# --- Vistas de EXPERTO ---
@login_required
@user_passes_test(is_experto, login_url=reverse_lazy('login_experto')) # Redirige al login de experto si no es experto o no está activo
def dashboard_experto(request):
    # Si el usuario NO está aprobado, redirige a la página de espera.
    # user_passes_test ya debería manejar la inactividad, pero es un doble chequeo.
    if request.user.approval_status != 'APPROVED' or not request.user.is_active:
        return redirect('espera_aprobacion')

    try:
        estado_pendiente = Estado.objects.get(Nombre='Pendiente')
        estado_activa = Estado.objects.get(Nombre='Activa')
    except Estado.DoesNotExist:
        messages.error(request, "Error de configuración de estados. Contacte al administrador.")
        return redirect('principal') 

    # Reservas donde el experto NO está asignado O es el experto asignado Y está pendiente/activa
    # Y la especialidad del servicio coincide con la especialidad del experto.
    reservas_pendientes = Reserva.objects.filter(
        Q(experto_asignado__isnull=True) | Q(experto_asignado=request.user),
        Q(idEstado=estado_pendiente) | Q(idEstado=estado_activa),
        idServicios__NombreServicio__iexact=request.user.especialidad
    ).order_by('Fecha', 'Hora')

    # Reservas ya asignadas a este experto, excluyendo completadas, canceladas, pendientes y activas
    # Los estados a excluir son los que ya se han "procesado" o están en la fase de "búsqueda de experto".
    # Asumo que 'Activa' es un estado intermedio que podría ser listado aquí si el experto ya la aceptó.
    # Si 'Activa' significa "ha sido asignada y está en progreso", entonces no debería estar en la Q de arriba.
    # Revisa la definición de tus estados para asegurarte de la lógica.
    reservas_asignadas = Reserva.objects.filter(
        experto_asignado=request.user
    ).exclude(
        Q(idEstado__Nombre='Completada') | Q(idEstado__Nombre='Cancelada') | Q(idEstado=estado_pendiente) # Ya no excluye 'Activa' si se supone que la 'Activa' ya es una asignada
    ).order_by('Fecha', 'Hora')

    return render(request, 'experto/dashboard_experto.html', {
        'reservas_pendientes': reservas_pendientes,
        'reservas_asignadas': reservas_asignadas,
        'user_especialidad': request.user.especialidad
    })

@login_required
@user_passes_test(is_experto, login_url=reverse_lazy('login_experto'))
def aceptar_reserva_experto(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)

    # Validaciones adicionales para evitar aceptar una reserva ya asignada o no calificada
    if reserva.experto_asignado and reserva.experto_asignado != request.user:
        messages.warning(request, "Esta reserva ya ha sido aceptada por otro experto.")
        return redirect('dashboard_experto')
    
    # Asegúrate de que el experto tiene la especialidad correcta para el servicio
    if request.user.especialidad and reserva.idServicios.NombreServicio.lower() != request.user.especialidad.lower():
        messages.error(request, "No estás cualificado para aceptar este tipo de servicio.")
        return redirect('dashboard_experto')
    
    # Asegúrate de que la reserva esté en un estado que permita ser aceptada (Pendiente o Activa)
    try:
        estado_pendiente = Estado.objects.get(Nombre='Pendiente')
        estado_activa = Estado.objects.get(Nombre='Activa')
        if reserva.idEstado not in [estado_pendiente, estado_activa]:
            messages.error(request, f"La reserva #{reserva.id} no puede ser aceptada en su estado actual ({reserva.idEstado.Nombre}).")
            return redirect('dashboard_experto')
    except Estado.DoesNotExist:
        messages.error(request, "Error de configuración de estados. Contacte al administrador.")
        return redirect('dashboard_experto')

    if request.method == 'POST':
        try:
            reserva.experto_asignado = request.user
            # El estado al aceptar debería ser 'Aceptada' o 'Activa' dependiendo de tu flujo de negocio
            # Si 'Activa' es el estado de "en progreso" después de aceptar, úsalo aquí.
            # Si 'Aceptada' es un paso intermedio antes de 'Activa', mantén 'Aceptada'.
            estado_aceptada = Estado.objects.get(Nombre='Aceptada') 
            reserva.idEstado = estado_aceptada
            
            reserva.save()
            messages.success(request, f'✅ ¡Has aceptado la reserva #{reserva.id}!')
            return redirect('dashboard_experto')
        except Estado.DoesNotExist:
            messages.error(request, "Error de configuración de estados. El estado 'Aceptada' no se encontró. Contacte al administrador.")
            return redirect('dashboard_experto')
        except Exception as e:
            messages.error(request, f"Ocurrió un error al aceptar la reserva: {e}")
            print(f"Error al aceptar reserva {reserva_id}: {e}") # Para depuración
            return redirect('dashboard_experto')
    
    return render(request, 'experto/confirmar_aceptar_reserva.html', {'reserva': reserva})


@login_required
@user_passes_test(is_experto, login_url=reverse_lazy('login_experto'))
def rechazar_reserva_experto(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)

    # Validaciones adicionales: solo se puede rechazar si no está asignada a otro experto
    if reserva.experto_asignado and reserva.experto_asignado != request.user:
        messages.warning(request, "Esta reserva ya ha sido asignada a otro experto y no puedes rechazarla.")
        return redirect('dashboard_experto')
    
    # Solo se pueden rechazar reservas en estado 'Pendiente' o 'Activa' (si Activa es "en búsqueda")
    try:
        estado_pendiente = Estado.objects.get(Nombre='Pendiente')
        estado_activa = Estado.objects.get(Nombre='Activa') # Si Activa es un estado "en búsqueda"
        if reserva.idEstado not in [estado_pendiente, estado_activa]:
             messages.error(request, f"La reserva #{reserva.id} no puede ser rechazada en su estado actual ({reserva.idEstado.Nombre}).")
             return redirect('dashboard_experto')
    except Estado.DoesNotExist:
        messages.error(request, "Error de configuración de estados. Contacte al administrador.")
        return redirect('dashboard_experto')

    if request.method == 'POST':
        try:
            # Si el experto es el asignado o no hay asignado, puede rechazar
            if reserva.experto_asignado == request.user:
                reserva.experto_asignado = None # Desasigna si ya estaba asignado
            
            estado_rechazada = Estado.objects.get(Nombre='Rechazada')
            reserva.idEstado = estado_rechazada

            reserva.save()
            messages.info(request, f'❌ Has rechazado la reserva #{reserva.id}.')
            return redirect('dashboard_experto')
        except Estado.DoesNotExist:
            messages.error(request, "Error de configuración de estados. El estado 'Rechazada' no se encontró. Contacte al administrador.")
            return redirect('dashboard_experto')
        except Exception as e:
            messages.error(request, f"Ocurrió un error al rechazar la reserva: {e}")
            print(f"Error al rechazar reserva {reserva_id}: {e}") # Para depuración
            return redirect('dashboard_experto')
    
    return render(request, 'experto/confirmar_rechazar_reserva.html', {'reserva': reserva})


@login_required
@user_passes_test(is_experto, login_url=reverse_lazy('login_experto'))
def historial_experto(request):
    reservas_completadas_canceladas = Reserva.objects.filter(
        experto_asignado=request.user,
        idEstado__Nombre__in=['Completada', 'Cancelada'] # Ajusta si tienes otros estados finales
    ).order_by('-Fecha', '-Hora')
    return render(request, 'experto/historial_experto.html', {
        'reservas': reservas_completadas_canceladas
    })


# --- Vistas de ADMINISTRADOR ---
@login_required
@user_passes_test(is_admin, login_url=reverse_lazy('login_admin'))
def admin_principal(request):
    total_users = CustomUser.objects.count()
    total_reservas = Reserva.objects.count()
    
    # Asegúrate de que el nombre del estado exista en tu base de datos
    try:
        estado_pendiente_reserva = Estado.objects.get(Nombre='Pendiente')
        reservas_pendientes = Reserva.objects.filter(idEstado=estado_pendiente_reserva).count()
    except Estado.DoesNotExist:
        reservas_pendientes = 0
        messages.warning(request, "Estado 'Pendiente' de reserva no encontrado. Las estadísticas pueden ser incorrectas.")

    expertos_registrados = CustomUser.objects.filter(tipo_usuario='experto').count()
    expertos_pendientes_aprobacion = CustomUser.objects.filter(
        tipo_usuario='experto', 
        approval_status='PENDING',
        is_active=False
    ).count()

    return render(request, 'admin/admin_principal.html', {
        'total_users': total_users,
        'total_reservas': total_reservas,
        'reservas_pendientes': reservas_pendientes,
        'expertos_registrados': expertos_registrados,
        'expertos_pendientes_aprobacion': expertos_pendientes_aprobacion,
    })

@login_required
@user_passes_test(is_admin, login_url=reverse_lazy('login_admin'))
def solicitudes_admin(request):
    # Esta vista podría listar tanto reservas como solicitudes de registro de expertos.
    # Por ahora, solo lista reservas. Considera dividirla o añadir un filtro.
    reservas_a_gestionar = Reserva.objects.all().order_by('-creado_en')
    return render(request, 'admin/solicitudes_admin.html', {'reservas': reservas_a_gestionar})

@login_required
@user_passes_test(is_admin, login_url=reverse_lazy('login_admin'))
def gestion_usuarios_admin(request):
    # Obtener todos los usuarios, ordenados por fecha de registro y luego por tipo
    usuarios = CustomUser.objects.all().order_by('-date_joined', 'tipo_usuario')
    return render(request, 'admin/gestion_usuarios.html', {'usuarios': usuarios})

@login_required
@user_passes_test(is_admin, login_url=reverse_lazy('login_admin'))
def aprobar_usuario(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        if user.tipo_usuario == 'experto': # Solo expertos requieren aprobación de esta manera
            user.approval_status = 'APPROVED'
            user.is_active = True # Activar el usuario
            user.save()
            messages.success(request, f"✅ Usuario '{user.username}' (experto) ha sido aprobado y activado.")
        else:
            messages.info(request, f"El usuario '{user.username}' no requiere aprobación especial.")
        return redirect('gestion_usuarios_admin')
    return render(request, 'admin/confirmar_aprobacion.html', {'usuario': user})

@login_required
@user_passes_test(is_admin, login_url=reverse_lazy('login_admin'))
def rechazar_usuario(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        if user.tipo_usuario == 'experto':
            user.approval_status = 'REJECTED'
            user.is_active = False # Mantener inactivo o desactivar
            user.save()
            messages.warning(request, f"❌ Usuario '{user.username}' (experto) ha sido rechazado y desactivado.")
        else:
            messages.info(request, f"El usuario '{user.username}' no requiere gestión de aprobación especial.")
        return redirect('gestion_usuarios_admin')
    return render(request, 'admin/confirmar_rechazo.html', {'usuario': user})

# Vista para usuarios no aprobados (expertos)
def espera_aprobacion(request):
    if request.user.is_authenticated and request.user.tipo_usuario == 'experto':
        if request.user.approval_status == 'APPROVED' and request.user.is_active:
            # Si el experto ya está aprobado, redirigirlo a su dashboard
            return redirect('dashboard_experto')
        elif request.user.approval_status == 'REJECTED':
            messages.error(request, "🚫 Tu cuenta ha sido rechazada. Por favor, contacta al soporte para más información.")
            return render(request, 'espera_aprobacion.html', {'status_message': 'rechazado'})
        else: # PENDING
            return render(request, 'espera_aprobacion.html', {'status_message': 'pendiente'})
    # Si no es un experto o no está autenticado, redirigir a home o login
    messages.info(request, "Acceso no autorizado.")
    return redirect('home')


# --- Vistas de Autenticación y Registro (NO deben tener @login_required) ---

def user_login_view(request):
    if request.user.is_authenticated:
        # Redirige según el tipo de usuario si ya está autenticado
        if request.user.tipo_usuario == 'cliente':
            return redirect(reverse_lazy('principal'))
        elif request.user.tipo_usuario == 'experto':
            # Expertos no aprobados deben ir a la página de espera
            if request.user.approval_status != 'APPROVED' or not request.user.is_active:
                return redirect('espera_aprobacion')
            return redirect(reverse_lazy('dashboard_experto'))
        elif request.user.tipo_usuario == 'admin':
            return redirect(reverse_lazy('admin_principal'))
        else: # Fallback para cualquier otro tipo
            return redirect(reverse_lazy('principal'))

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Validar estado de aprobación para expertos
            if user.tipo_usuario == 'experto' and (user.approval_status != 'APPROVED' or not user.is_active):
                auth_logout(request) # Asegurarse de que no quede logeado
                if user.approval_status == 'REJECTED':
                    messages.error(request, "🚫 Tu cuenta de experto ha sido rechazada. Contacta al soporte.")
                    return redirect('login_experto') # Redirige al login de experto para que lo intente de nuevo o vea el mensaje
                else: # PENDING
                    messages.warning(request, "⏳ Tu cuenta de experto está pendiente de aprobación. Serás notificado cuando sea revisada.")
                    return redirect('espera_aprobacion')
            
            # Si todo está bien, login
            auth_login(request, user)
            messages.success(request, f"¡Bienvenido, {user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            
            # Redirigir según el tipo de usuario
            if user.tipo_usuario == 'cliente':
                return redirect(reverse_lazy('principal'))
            elif user.tipo_usuario == 'experto':
                return redirect(reverse_lazy('dashboard_experto'))
            elif user.tipo_usuario == 'admin':
                return redirect(reverse_lazy('admin_principal'))
            else: # Fallback
                return redirect(reverse_lazy('principal'))
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = AuthenticationForm()
    return render(request, 'sign-in/login.html', {'form': form})

def user_logout_view(request):
    auth_logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect(reverse_lazy('home'))

def login_experto(request):
    if request.user.is_authenticated:
        # Si ya está autenticado y es un experto aprobado, redirigir a su dashboard
        if request.user.tipo_usuario == 'experto' and request.user.approval_status == 'APPROVED' and request.user.is_active:
            return redirect('dashboard_experto')
        # Si es un experto no aprobado, a la página de espera
        elif request.user.tipo_usuario == 'experto' and (request.user.approval_status != 'APPROVED' or not request.user.is_active):
            return redirect('espera_aprobacion')
        # Cualquier otro usuario autenticado, a principal (o su dashboard si es admin)
        else:
            return redirect('principal')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # VALIDACIÓN CRÍTICA PARA EXPERTOS:
            if hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'experto':
                if user.approval_status == 'APPROVED' and user.is_active:
                    auth_login(request, user)
                    messages.success(request, f"¡Bienvenido, experto {user.username}!")
                    next_url = request.GET.get('next')
                    if next_url:
                        return redirect(next_url)
                    return redirect(reverse_lazy('dashboard_experto'))
                elif user.approval_status == 'PENDING':
                    auth_logout(request) # Asegurarse de que no quede logeado si fue autenticado por el form
                    messages.warning(request, "⏳ Tu cuenta de experto está pendiente de aprobación.")
                    return redirect('espera_aprobacion')
                elif user.approval_status == 'REJECTED':
                    auth_logout(request)
                    messages.error(request, "🚫 Tu cuenta de experto ha sido rechazada. Contacta al soporte.")
                    return redirect('login_experto') # Se queda en la página de login con el error
            else:
                form.add_error(None, "Las credenciales no corresponden a un experto.")
                messages.error(request, "Acceso denegado: Usuario no es un experto.")
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = AuthenticationForm()
    return render(request, 'sign-in/login_experto.html', {'form': form})

def login_admin(request):
    if request.user.is_authenticated:
        if request.user.tipo_usuario == 'admin':
            return redirect('admin_principal')
        else:
            return redirect('principal')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # VALIDACIÓN CRÍTICA PARA ADMINS:
            # Puedes usar is_staff o is_superuser para administradores
            # o si usas tipo_usuario='admin', comprueba que esté activo.
            if hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'admin' and user.is_active:
                auth_login(request, user)
                messages.success(request, f"¡Bienvenido, administrador {user.username}!")
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect(reverse_lazy('admin_principal'))
            else:
                form.add_error(None, "Las credenciales no corresponden a un administrador o la cuenta no está activa.")
                messages.error(request, "Acceso denegado: Usuario no es un administrador o cuenta inactiva.")
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = AuthenticationForm()
    return render(request, 'sign-in/login_admin.html', {'form': form})

def registrarse(request):
    if request.user.is_authenticated:
        return redirect('principal')

    if request.method == 'POST':
        form = RegistroForm(request.POST, request.FILES) 

        # ReCaptcha validation
        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.RECAPTCHA_PRIVATE_KEY,
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        if not result.get('success'):
            messages.error(request, '⚠️ Debes verificar que no eres un robot.')
        elif form.is_valid():
            user = form.save()
            # Si es un cliente, lo logeamos directamente.
            if user.tipo_usuario == 'cliente':
                auth_login(request, user)
                messages.success(request, '🎉 ¡Registro exitoso! Bienvenido a DoIt.')
                return redirect(reverse_lazy('principal'))
            # Si es un experto, no lo logeamos inmediatamente, solo lo registramos y mostramos mensaje de espera.
            elif user.tipo_usuario == 'experto':
                # No logear automáticamente al experto si su cuenta necesita aprobación
                # Dejarlo inactivo por defecto y en estado PENDING, como en el modelo
                messages.info(request, '🎉 ¡Registro de experto exitoso! Tu cuenta está pendiente de aprobación.')
                return redirect(reverse_lazy('login_experto')) # Redirige al login de experto para que vea el mensaje de espera
        else:
            messages.error(request, 'Hubo un error al registrarte. Por favor, revisa los datos.')
            print("Errores del formulario de registro:", form.errors)
    else:
        form = RegistroForm(initial={'tipo_usuario': 'cliente'}) # Valor por defecto para el registro general
    return render(request, 'registrarse.html', {'form': form, 'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY})

def regisexperto(request):
    if request.user.is_authenticated:
        return redirect('principal')

    if request.method == 'POST':
        form = RegistroForm(request.POST, request.FILES)
        
        # ReCaptcha validation
        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.RECAPTCHA_PRIVATE_KEY,
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        if not result.get('success'):
            messages.error(request, '⚠️ Debes verificar que no eres un robot.')
        elif form.is_valid():
            user = form.save(commit=False)
            user.tipo_usuario = 'experto'
            # user.is_active y user.approval_status ya son manejados por el modelo por defecto.
            user.save()
            # NO logear al experto automáticamente aquí. Dejar que pase por el flujo de aprobación.
            messages.success(request, '🎉 ¡Registro de experto exitoso! Tu cuenta está pendiente de aprobación y será revisada por un administrador.')
            return redirect(reverse_lazy('login_experto')) # Redirige al login de experto para que se le muestre el mensaje de espera
        else:
            messages.error(request, 'Hubo un error al registrarte como experto. Por favor, revisa los datos.')
            print("Errores del formulario de registro de experto:", form.errors)
    else:
        form = RegistroForm(initial={'tipo_usuario': 'experto'}) # Valor por defecto para el registro de experto
    return render(request, 'regisexperto.html', {'form': form, 'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY})

# --- Vistas de Perfil de Usuario ---
@login_required
def editar_perfil_view(request):
    user = request.user
    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            try:
                user_instance = form.save()
                messages.success(request, '✅ ¡Tu perfil ha sido actualizado con éxito!')
                # Redirigir al usuario a su dashboard correspondiente después de editar su perfil
                if user_instance.tipo_usuario == 'cliente':
                    return redirect('principal')
                elif user_instance.tipo_usuario == 'experto':
                    # Si un experto edita su perfil, redirige a su dashboard de experto
                    return redirect('dashboard_experto')
                else:
                    return redirect('principal') # Fallback
            except Exception as e:
                messages.error(request, f'Hubo un error al guardar el perfil: {e}')
                print(f"ERROR al guardar el formulario de perfil: {e}")
        else:
            messages.error(request, 'Hubo un error al actualizar tu perfil. Por favor, revisa los datos.')
            print("Errores del formulario:", form.errors)
    else:
        form = PerfilUsuarioForm(instance=user)

    return render(request, 'modificar.html', {'form': form})


# Vistas de contenido estático
def fin(request):
    return render(request, 'fin.html')

def normalizacion(request):
    return render(request, 'normalizacion.html')

def modelo_relacional(request):
    return render(request, 'modelo_relacional.html')

def sentenciasddl(request):
    return render(request, 'sentenciasddl.html')

def sentencias_dml(request):
    return render(request, 'sentencias_dml.html')

def diccionario_de_datos(request):
    return render(request, 'diccionario_de_datos.html')

def diagrama_de_clases(request):
    return render(request, 'diagrama_de_clases.html')

def nosotros(request):
    return render(request, 'nosotros.html')

def terminos_condiciones(request):
    return render(request, 'terminos_condiciones.html')

def tratamiento_datos(request):
    return render(request, 'tratamiento_datos.html')