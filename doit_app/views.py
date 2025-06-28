from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistroForm, PerfilUsuarioForm, ReservaForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Estado, Servicios, Categorias, Reserva, CustomUser
from django.conf import settings
import requests
from django.db.models import Q
from .models import Ciudad
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q  # ← Esto soluciona lo de Q
from .models import Mensaje  # ← Asegúrate de importar tu modelo correctamente
from django.http import HttpResponseForbidden



@login_required
def chat_view(request, receptor_id):
    receptor = get_object_or_404(CustomUser, id=receptor_id)

    # Validar si hay una reserva aceptada entre ellos (cliente o experto)
    reserva_aceptada = Reserva.objects.filter(
        Q(idUsuario=request.user, experto_asignado=receptor) |
        Q(idUsuario=receptor, experto_asignado=request.user),
        idEstado__Nombre='Aceptada'
    ).exists()

    if not reserva_aceptada:
        return HttpResponseForbidden("❌ No tienes permiso para chatear con este usuario.")

    if request.method == 'POST':
        contenido = request.POST.get('contenido')
        if contenido:
            Mensaje.objects.create(emisor=request.user, receptor=receptor, contenido=contenido)

    # Marcar mensajes como leídos
    Mensaje.objects.filter(receptor=request.user, emisor=receptor, leido=False).update(leido=True)

    mensajes = Mensaje.objects.filter(
        Q(emisor=request.user, receptor=receptor) |
        Q(emisor=receptor, receptor=request.user)
    ).order_by('fecha_envio')

    return render(request, 'chat.html', {
        'receptor': receptor,
        'mensajes': mensajes
    })







# Funciones de test para @user_passes_test
def is_cliente(user):
    return user.is_authenticated and user.tipo_usuario == 'cliente'

def is_experto(user):
    # Mantener el print para depuración de la función is_experto
    print(f"DEBUG is_experto: User: {user.username}, Is Authenticated: {user.is_authenticated}, Tipo: {user.tipo_usuario}")
    return user.is_authenticated and user.tipo_usuario == 'experto'

def is_admin(user):
    return user.is_authenticated and user.tipo_usuario == 'admin'

# --- Vistas Generales ---
def home(request):
    return render(request, 'home.html')



@login_required
def cancelar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)

    # Verificar que el usuario autenticado sea el dueño de la reserva
    if reserva.idUsuario != request.user:
        messages.error(request, "No tienes permiso para cancelar esta reserva.")
        return redirect('principal')

    if request.method == 'POST':
        motivo = request.POST.get('motivo')
        if motivo == 'otra':
            motivo = request.POST.get('otro_motivo', '').strip()

        try:
            estado_cancelada = Estado.objects.get(Nombre='Cancelada')
        except Estado.DoesNotExist:
            messages.error(request, "No se pudo cancelar la reserva. Estado 'Cancelada' no existe.")
            return redirect('principal')

        reserva.idEstado = estado_cancelada
        reserva.motivo_cancelacion = motivo
        reserva.save()

        messages.success(request, f'Has cancelado la reserva #{reserva.id}.')
        return redirect('principal')

    return redirect('principal')


@login_required
def principal(request):
    # Redirección según tipo de usuario
    if request.user.tipo_usuario == 'experto':
        return redirect('dashboard_experto')

    if request.user.tipo_usuario == 'admin':
        return redirect('admin_principal')

    categorias = Categorias.objects.all()
    servicios = Servicios.objects.all()

    # Agrupar servicios por categoría
    servicios_por_categoria = {
        cat.Nombre: list(servicios.filter(idCategorias=cat))
        for cat in categorias
    }

    # Últimas 3 reservas no canceladas ni completadas
    ultimas_reservas = Reserva.objects.filter(
        idUsuario=request.user
    ).exclude(
        Q(idEstado__Nombre='Cancelada') | Q(idEstado__Nombre='Completada')
    ).order_by('-Fecha', '-Hora')[:3]

    # Última reserva aceptada (para mostrar mensaje de confirmación)
    reserva_aceptada = Reserva.objects.filter(
        idUsuario=request.user,
        idEstado__Nombre='Aceptada'
    ).order_by('-Fecha', '-Hora').first()

    # 🔴 Mensajes no leídos del experto hacia el cliente
    mensajes_no_leidos = {}
    if reserva_aceptada and reserva_aceptada.experto_asignado:
        experto = reserva_aceptada.experto_asignado
        count = Mensaje.objects.filter(
            emisor=experto,
            receptor=request.user,
            leido=False
        ).count()
        if count > 0:
            mensajes_no_leidos[experto.id] = count

    return render(request, 'principal.html', {
        'categorias': categorias,
        'servicios_por_categoria': servicios_por_categoria,
        'ultimas_reservas': ultimas_reservas,
        'reserva_aceptada': reserva_aceptada,
        'mensajes_no_leidos': mensajes_no_leidos,  # ✅ ahora sí está en el contexto
    })


@login_required
@user_passes_test(is_cliente, login_url=reverse_lazy('login')) 
def reserva(request):
    servicio_id = request.GET.get('servicio_id') or request.session.get('servicio_id')

    if not servicio_id:
        messages.error(request, "⚠️ Servicio no seleccionado. Por favor, elige un servicio.")
        return redirect('principal')

    servicio = get_object_or_404(Servicios, id=servicio_id)
    request.session['servicio_id'] = servicio_id

    if request.method == 'POST':
        form = ReservaForm(request.POST)

        pais_id = request.POST.get('pais')
        if pais_id:
            form.fields['ciudad'].queryset = Ciudad.objects.filter(departamento__pais_id=pais_id)
        else:
            form.fields['ciudad'].queryset = Ciudad.objects.none()

        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.idUsuario = request.user
            reserva.idServicios = servicio

            try:
                estado_pendiente = Estado.objects.get(Nombre='Pendiente')
                reserva.idEstado = estado_pendiente
            except Estado.DoesNotExist:
                messages.error(request, "Error interno: El estado 'Pendiente' no se encontró en la base de datos.")
                return redirect('principal')

            reserva.save()

            # Guarda datos en sesión para mostrar mensaje en la siguiente vista
            request.session['mensaje_reserva'] = {
                'servicio': servicio.NombreServicio,
                'fecha': reserva.Fecha.strftime('%d/%m/%Y'),
                'hora': reserva.Hora.strftime('%H:%M'),
                'direccion': reserva.direccion,
                'ciudad': reserva.ciudad.Nombre if reserva.ciudad else 'No especificada'
            }

            return redirect('principal')
        else:
            messages.error(request, '❌ Hubo un error al procesar tu reserva. Por favor, revisa los datos.')
    else:
        form = ReservaForm(initial={'idServicios': servicio})

    return render(request, 'reserva.html', {
        'form': form,
        'servicio': servicio
    })



def ciudades_por_pais(request):
    pais_id = request.GET.get('pais_id')
    if pais_id:
        ciudades = Ciudad.objects.filter(departamento__pais_id=pais_id).values('id', 'Nombre')
        return JsonResponse(list(ciudades), safe=False)
    return JsonResponse({'error': 'No se proporcionó un ID de país'}, status=400)

@require_POST
@user_passes_test(is_experto, login_url=reverse_lazy('login'))
def aceptar_reserva_experto(request, reserva_id):
    reserva = get_object_or_404(Reserva, pk=reserva_id, experto_asignado__isnull=True)

    try:
        estado_activa = Estado.objects.get(Nombre='Activa')
    except Estado.DoesNotExist:
        messages.error(request, "Error interno: Estado 'Activa' no existe.")
        return redirect('dashboard_experto')

    reserva.experto_asignado = request.user
    reserva.idEstado = estado_activa
    reserva.save()

    messages.success(request, "✅ Has aceptado la reserva correctamente.")
    return redirect('dashboard_experto')


@require_POST
@user_passes_test(is_experto, login_url=reverse_lazy('login'))
def rechazar_reserva_experto(request, reserva_id):
    # Opcional: registrar rechazo, pero por ahora solo redireccionar
    messages.info(request, "Has rechazado la reserva.")
    return redirect('dashboard_experto')
















@login_required
@user_passes_test(is_cliente, login_url=reverse_lazy('login'))
def mis_reservas_cliente(request):
    reservas = Reserva.objects.filter(idUsuario=request.user).order_by('-creado_en')
    return render(request, 'cliente/mis_reservas.html', {'reservas': reservas})


@login_required
def busc_experto(request):
    return render(request, 'busc_experto.html')

@login_required
def modificar(request):
    return redirect('editar_perfil')

@login_required
def servicioAceptado(request):
    return render(request, 'servicioAceptado.html')

@login_required
def servicioAceptadoexpe(request):
    return render(request, 'servicioAceptadoexpe.html')


@login_required
def servicioCancelado(request):
    return render(request, 'servicioCancelado.html')

@login_required
def servicioCanceladoexpe(request):
    return render(request, 'servicioCanceladoexpe.html')




# ESTA ES LA ÚNICA DEFINICIÓN DE dashboard_experto QUE DEBE QUEDAR
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse_lazy
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Reserva, Estado



@user_passes_test(is_experto, login_url=reverse_lazy('login'))
def dashboard_experto(request):
    print(f"DEBUG dashboard_experto: Accediendo. User: {request.user.username}, Is Authenticated: {request.user.is_authenticated}, Tipo: {request.user.tipo_usuario}")

    if not is_experto(request.user):
        print("DEBUG: is_experto regresó False para el usuario autenticado.")
        return redirect('principal')

    try:
        estado_pendiente = Estado.objects.get(Nombre='Pendiente')
        estado_activa = Estado.objects.get(Nombre='Activa')
    except Estado.DoesNotExist:
        messages.error(request, "Error de configuración de estados. Contacte al administrador.")
        return redirect('principal')

    reservas_pendientes = Reserva.objects.none()

    if request.user.especialidad:
        reservas_pendientes = Reserva.objects.filter(
            (Q(experto_asignado__isnull=True) | Q(experto_asignado=request.user)),
            Q(idEstado=estado_pendiente) | Q(idEstado=estado_activa),
            idServicios=request.user.especialidad
        ).order_by('Fecha', 'Hora')

    reservas_asignadas = Reserva.objects.filter(
        experto_asignado=request.user,
        idEstado__Nombre__in=['Aceptada', 'En progreso']
    ).select_related('idUsuario', 'idServicios')

    reservas_canceladas = Reserva.objects.filter(
        experto_asignado=request.user,
        idEstado__Nombre='Cancelada'
    ).order_by('-Fecha', '-Hora')

    # NUEVO: verificar mensajes no leídos por cada cliente
    mensajes_no_leidos = {}
    for reserva in reservas_asignadas:
        cliente = reserva.idUsuario
        count = Mensaje.objects.filter(
            emisor=cliente,
            receptor=request.user,
            leido=False
        ).count()
        if count > 0:
            mensajes_no_leidos[cliente.id] = count

    return render(request, 'experto/dashboard_experto.html', {
        'reservas_pendientes': reservas_pendientes,
        'reservas_asignadas': reservas_asignadas,
        'reservas_canceladas': reservas_canceladas,
        'user_especialidad': request.user.especialidad,
        'mensajes_no_leidos': mensajes_no_leidos  # 👈 lo pasamos al template
    })



@login_required
@user_passes_test(lambda u: u.tipo_usuario == 'experto', login_url=reverse_lazy('login'))
def aceptar_reserva_experto(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)

    # Verifica si la reserva ya fue aceptada por otro experto
    if reserva.experto_asignado and reserva.experto_asignado != request.user:
        messages.warning(request, "Esta reserva ya ha sido aceptada por otro experto.")
        return redirect('dashboard_experto')

    # 🔁 Validación por categoría de especialidad del servicio del experto
    if not request.user.especialidad or not request.user.especialidad.idCategorias:
        messages.error(request, "Tu perfil no tiene una especialidad o categoría válida.")
        return redirect('dashboard_experto')

    if reserva.idServicios.idCategorias != request.user.especialidad.idCategorias:
        messages.error(request, "No estás cualificado para aceptar este tipo de servicio.")
        return redirect('dashboard_experto')

    # Si todo está bien, procesar aceptación POST
    if request.method == 'POST':
        try:
            reserva.experto_asignado = request.user
            estado_aceptada = Estado.objects.get(Nombre='Aceptada')
            reserva.idEstado = estado_aceptada
            reserva.save()

            return redirect('dashboard_experto')

        except Estado.DoesNotExist:
            messages.error(request, "Error de configuración de estados. Contacte al administrador.")
            return redirect('dashboard_experto')
        except Exception as e:
            messages.error(request, f"Ocurrió un error al aceptar la reserva: {e}")
            return redirect('dashboard_experto')

    return render(request, 'experto/confirmar_aceptar_reserva.html', {'reserva': reserva})



@login_required
@user_passes_test(is_experto, login_url=reverse_lazy('login'))
def rechazar_reserva_experto(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)

    if reserva.experto_asignado and reserva.experto_asignado != request.user:
        messages.warning(request, "Esta reserva ya ha sido asignada a otro experto y no puedes rechazarla.")
        return redirect('dashboard_experto')
    
    if request.method == 'POST':
        try:
            if reserva.experto_asignado == request.user:
                reserva.experto_asignado = None
            
            estado_rechazada = Estado.objects.get(Nombre='Rechazada')
            reserva.idEstado = estado_rechazada

            reserva.save()
            return redirect('dashboard_experto')
        except Estado.DoesNotExist:
            return redirect('dashboard_experto')
        except Exception as e:
            messages.error(request, f"Ocurrió un error al rechazar la reserva: {e}")
            return redirect('dashboard_experto')
    
    return render(request, 'experto/confirmar_rechazar_reserva.html', {'reserva': reserva})





@login_required
@user_passes_test(is_experto, login_url=reverse_lazy('login'))
def historial_experto(request):
    reservas_completadas_canceladas = Reserva.objects.filter(
        experto_asignado=request.user,
        idEstado__Nombre__in=['Completada', 'Cancelada']
    ).order_by('-Fecha', '-Hora')
    return render(request, 'experto/historial_experto.html', {
        'reservas': reservas_completadas_canceladas
    })


@login_required
def fin(request):
    return render(request, 'fin.html')

@login_required
def normalizacion(request):
    return render(request, 'normalizacion.html')

@login_required
def modelo_relacional(request):
    return render(request, 'modelo_relacional.html')

@login_required
def sentenciasddl(request):
    return render(request, 'sentenciasddl.html')

@login_required
def sentencias_dml(request):
    return render(request, 'sentencias_dml.html')

@login_required
def diccionario_de_datos(request):
    return render(request, 'diccionario_de_datos.html')

@login_required
def diagrama_de_clases(request):
    return render(request, 'diagrama_de_clases.html')

@login_required
@user_passes_test(is_admin, login_url=reverse_lazy('login'))
def admin_principal(request):
    total_users = CustomUser.objects.count()
    total_reservas = Reserva.objects.count()
    reservas_pendientes = Reserva.objects.filter(idEstado__Nombre='Pendiente').count()
    expertos_registrados = CustomUser.objects.filter(tipo_usuario='experto').count()

    return render(request, 'admin/admin_principal.html', {
        'total_users': total_users,
        'total_reservas': total_reservas,
        'reservas_pendientes': reservas_pendientes,
        'expertos_registrados': expertos_registrados,
    })

@login_required
@user_passes_test(is_admin, login_url=reverse_lazy('login'))
def solicitudes_admin(request):
    reservas_a_gestionar = Reserva.objects.all().order_by('-creado_en')
    return render(request, 'admin/solicitudes_admin.html', {'reservas': reservas_a_gestionar})


# --- Vistas de Autenticación y Registro (NO deben tener @login_required) ---

def user_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f"¡Bienvenido, {user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            if user.tipo_usuario == 'cliente':
                return redirect(reverse_lazy('principal'))
            elif user.tipo_usuario == 'experto':
                return redirect(reverse_lazy('dashboard_experto'))
            elif user.tipo_usuario == 'admin':
                return redirect(reverse_lazy('admin_principal'))
            else: # Fallback
                return redirect(reverse_lazy('principal'))
    else:
        form = AuthenticationForm()
    return render(request, 'sign-in/login.html', {'form': form})

def user_logout_view(request):
    auth_logout(request)
    return redirect(reverse_lazy('home'))

def login_experto(request):
    if request.user.is_authenticated:
        if request.user.tipo_usuario == 'experto':
            return redirect('dashboard_experto')
        else:
            return redirect('principal')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'experto':
                auth_login(request, user)
                messages.success(request, f"¡Bienvenido, experto {user.username}!")
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect(reverse_lazy('dashboard_experto'))
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
            if hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'admin':
                auth_login(request, user)
                messages.success(request, f"¡Bienvenido, administrador {user.username}!")
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect(reverse_lazy('admin_principal'))
            else:
                form.add_error(None, "Las credenciales no corresponden a un administrador.")
                messages.error(request, "Acceso denegado: Usuario no es un administrador.")
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
            auth_login(request, user)
            messages.success(request, '🎉 ¡Registro exitoso! Bienvenido a DoIt.')
            return redirect(reverse_lazy('principal'))
        else:
            messages.error(request, 'Hubo un error al registrarte. Por favor, revisa los datos.')
            print("Errores del formulario de registro:", form.errors)
    else:
        form = RegistroForm(initial={'tipo_usuario': 'cliente'})
    return render(request, 'registrarse.html', {'form': form, 'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY})

def regisexperto(request):
    if request.user.is_authenticated:
        return redirect('principal')

    if request.method == 'POST':
        form = RegistroForm(request.POST, request.FILES)
        
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
            user.save()
            auth_login(request, user)
            messages.success(request, '🎉 ¡Registro de experto exitoso! Bienvenido a DoIt.')
            return redirect(reverse_lazy('dashboard_experto')) # Redirige directamente al dashboard del experto
        else:
            messages.error(request, 'Hubo un error al registrarte como experto. Por favor, revisa los datos.')
            print("Errores del formulario de registro de experto:", form.errors)
    else:
        form = RegistroForm(initial={'tipo_usuario': 'experto'})
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
                if user_instance.tipo_usuario == 'cliente':
                    return redirect('principal')
                elif user_instance.tipo_usuario == 'experto':
                    return redirect('dashboard_experto')
                else:
                    return redirect('principal')
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
def nosotros(request):
    return render(request, 'nosotros.html')

def terminos_condiciones(request):
    return render(request, 'terminos_condiciones.html')

def tratamiento_datos(request):
    return render(request, 'tratamiento_datos.html')


