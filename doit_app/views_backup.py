from django.shortcuts import render, redirect, get_object_or_404
from .utils import obtener_promedio_calificaciones_experto
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
from django.db.models import Q 
from .models import Mensaje
from django.http import HttpResponseForbidden
from django.urls import reverse
from datetime import timedelta
from .models import Calificaciones
from django.contrib.auth.decorators import login_required
from .models import Notificacion
from django.db import models
from .models import Disponibilidad  
from .forms import DisponibilidadForm 
from django.db.models import Value, OuterRef, Exists, CharField, Case, When, BooleanField
from django.db.models.functions import Concat
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model
from functools import wraps
from django.core.mail import send_mail
from django.conf import settings


def usuario_aprobado_required(view_func):
    """
    Decorador que verifica si el usuario está aprobado antes de permitir el acceso.
    Para clientes: verifica aprobado_cliente == 'aprobado'
    Para expertos: verifica verificado == 'aprobado'
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Permitir acceso a superusuarios/admin
        if request.user.is_superuser or request.user.tipo_usuario == 'admin':
            return view_func(request, *args, **kwargs)
        
        # Verificar estado de aprobación según tipo de usuario
        if request.user.tipo_usuario == 'cliente':
            if request.user.aprobado_cliente != 'aprobado':
                messages.warning(request, 'Tu cuenta está pendiente de aprobación por parte del administrador. No puedes acceder a todas las funcionalidades hasta que sea aprobada.')
                return render(request, 'pendiente_aprobacion.html', {
                    'tipo_usuario': 'cliente',
                    'estado': request.user.aprobado_cliente
                })
        elif request.user.tipo_usuario == 'experto':
            if request.user.verificado != 'aprobado':
                messages.warning(request, 'Tu cuenta está pendiente de aprobación por parte del administrador. No puedes acceder a todas las funcionalidades hasta que sea aprobada.')
                return render(request, 'pendiente_aprobacion.html', {
                    'tipo_usuario': 'experto',
                    'estado': request.user.verificado
                })
        
        return view_func(request, *args, **kwargs)
    return wrapper
from functools import wraps



def usuario_aprobado_required(view_func):
    """
    Decorador que verifica si el usuario está aprobado antes de permitir el acceso.
    Para clientes: verifica aprobado_cliente == 'aprobado'
    Para expertos: verifica verificado == 'aprobado'
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Permitir acceso a superusuarios/admin
        if request.user.is_superuser or request.user.tipo_usuario == 'admin':
            return view_func(request, *args, **kwargs)
        
        # Verificar estado de aprobación según tipo de usuario
        if request.user.tipo_usuario == 'cliente':
            if request.user.aprobado_cliente != 'aprobado':
                messages.warning(request, 'Tu cuenta está pendiente de aprobación por parte del administrador. No puedes acceder a todas las funcionalidades hasta que sea aprobada.')
                return render(request, 'pendiente_aprobacion.html', {
                    'tipo_usuario': 'cliente',
                    'estado': request.user.aprobado_cliente
                })
        elif request.user.tipo_usuario == 'experto':
            if request.user.verificado != 'aprobado':
                messages.warning(request, 'Tu cuenta está pendiente de aprobación por parte del administrador. No puedes acceder a todas las funcionalidades hasta que sea aprobada.')
                return render(request, 'pendiente_aprobacion.html', {
                    'tipo_usuario': 'experto',
                    'estado': request.user.verificado
                })
        
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
@usuario_aprobado_required
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


@login_required(login_url='login')
@user_passes_test(lambda u: u.tipo_usuario == 'experto', login_url='login')
@require_http_methods(["GET", "POST"])
def dashboard_experto(request):
    print(f"DEBUG dashboard_experto: Accediendo. User: {request.user.username}, Tipo: {request.user.tipo_usuario}")

    if request.user.verificado == 'pendiente':
        return render(request, 'experto/espera_verificacion.html')
    elif request.user.verificado == 'rechazado':
        return render(request, 'experto/rechazado.html')

    form_disponibilidad = DisponibilidadForm()
    mostrar_mensaje_finalizado = False
    reserva_id_calificar = None

    if request.method == 'POST':
        if 'form_disponibilidad' in request.POST:
            fechas = request.POST.getlist('fechas[]')
            estados = request.POST.getlist('estados[]')
            hora_inicio = request.POST.get('hora_inicio')
            hora_fin = request.POST.get('hora_fin')

            errores = False
            if not fechas or not estados or len(fechas) != len(estados):
                messages.error(request, "Debe seleccionar al menos un día y un estado válido.")
                errores = True

            if not hora_inicio or not hora_fin:
                messages.error(request, "Debe especificar hora inicio y hora fin.")
                errores = True

            if not errores:
                for fecha_str, estado_nombre in zip(fechas, estados):
                    try:
                        estado_obj = Estado.objects.get(Nombre__iexact=estado_nombre)
                    except Estado.DoesNotExist:
                        messages.error(request, f"Estado '{estado_nombre}' no existe en la base de datos.")
                        errores = True
                        continue

                    form_data = {
                        'fecha': fecha_str,
                        'hora_inicio': hora_inicio,
                        'hora_fin': hora_fin,
                    }
                    form = DisponibilidadForm(form_data)
                    if form.is_valid():
                        disponibilidad = form.save(commit=False)
                        disponibilidad.experto = request.user
                        disponibilidad.idEstado = estado_obj
                        disponibilidad.save()
                    else:
                        messages.error(request, f"Error en la fecha {fecha_str}: {form.errors}")
                        errores = True

                if not errores:
                    messages.success(request, "Disponibilidad registrada correctamente.")
                    return redirect('dashboard_experto')
            else:
                form_disponibilidad = DisponibilidadForm()

        elif request.POST.get('accion') == 'eliminar_disponibilidad':
            disponibilidad_id = request.POST.get('disponibilidad_id')
            try:
                disponibilidad = Disponibilidad.objects.get(id=disponibilidad_id, experto=request.user)
                disponibilidad.delete()
                messages.success(request, "Disponibilidad eliminada correctamente.")
            except Disponibilidad.DoesNotExist:
                messages.error(request, "No se encontró la disponibilidad a eliminar.")
            return redirect('dashboard_experto')

        elif 'accion' in request.POST and 'reserva_id' in request.POST:
            accion = request.POST.get('accion')
            reserva_id = request.POST.get('reserva_id')
            print(f"POST recibido | Acción: {accion}, Reserva ID: {reserva_id}")

            try:
                reserva = Reserva.objects.get(id=reserva_id)

                if accion == 'aceptar':
                    conflicto = Reserva.objects.filter(
                        experto_asignado=request.user,
                        Fecha=reserva.Fecha,
                        Hora=reserva.Hora,
                        servicio_finalizado=False
                    ).exists()

                    if conflicto:
                        messages.warning(request, "Ya tienes una reserva aceptada a esa hora y aún no la has finalizado.")
                        return redirect('dashboard_experto')

                    if reserva.experto_solicitado and reserva.experto_solicitado != request.user:
                        messages.error(request, "Esta reserva fue solicitada a otro experto.")
                        return redirect('dashboard_experto')

                    if not reserva.experto_asignado and reserva.idServicios in request.user.especialidad.all():
                        Reserva.objects.filter(
                            id=reserva.id
                        ).exclude(
                            experto_asignado=request.user
                        ).update(experto_asignado=None)

                        reserva.experto_asignado = request.user
                        estado_aceptada = Estado.objects.get(Nombre='Aceptada')
                        reserva.idEstado = estado_aceptada
                        reserva.save()

                        Notificacion.objects.create(
                            usuario=reserva.idUsuario,
                            mensaje=f'Tu servicio \"{reserva.idServicios.NombreServicio}\" fue aceptado por el experto {request.user.get_full_name() or request.user.username}.',
                            url=''
                        )

                        messages.success(request, "Has aceptado correctamente la reserva.")
                        return redirect('dashboard_experto')

                elif accion == 'iniciar_servicio':
                    if reserva.experto_asignado == request.user and not reserva.servicio_iniciado:
                        reserva.servicio_iniciado = True
                        reserva.save()
                        messages.info(request, "Has iniciado el servicio.")
                        return redirect('dashboard_experto')

                elif accion == 'finalizar_servicio':
                    if reserva.experto_asignado == request.user and reserva.servicio_iniciado and not reserva.servicio_finalizado:
                        comentario = request.POST.get('comentario', '').strip()
                        duracion = request.POST.get('duracion', '').strip()
                        reserva.comentario_durante_servicio = comentario
                        reserva.duracion_estimada = duracion
                        reserva.servicio_finalizado = True
                        estado_finalizado = Estado.objects.get(Nombre='Finalizado')
                        reserva.idEstado = estado_finalizado
                        reserva.save()

                        Notificacion.objects.create(
                            usuario=reserva.idUsuario,
                            mensaje=f'¡Tu servicio "{reserva.idServicios.NombreServicio}" con {request.user.get_full_name() or request.user.username} ha sido completado! 🎉 Comparte tu experiencia.',
                            url=f'/calificar_reserva/{reserva.id}/'
                        )

                        estado_no_disp = Estado.objects.get(Nombre='No disponible')
                        Disponibilidad.objects.filter(
                            experto=request.user,
                            fecha=reserva.Fecha,
                            idEstado=estado_no_disp
                        ).delete()

                        mostrar_mensaje_finalizado = True
                        reserva_id_calificar = reserva.id

            except Reserva.DoesNotExist:
                messages.error(request, "La reserva no existe.")
            except Estado.DoesNotExist:
                messages.error(request, "Estado no encontrado.")
            except Exception as e:
                print(f"⚠️ Error inesperado: {e}")
                messages.error(request, "Ocurrió un error inesperado.")

    estado_pendiente = Estado.objects.filter(Nombre='Pendiente').first()
    estado_finalizado = Estado.objects.filter(Nombre='Finalizado').first()
    estado_rechazada = Estado.objects.filter(Nombre='Rechazada').first()

    reservas_pendientes = Reserva.objects.filter(
        Q(idEstado=estado_pendiente) & Q(experto_asignado__isnull=True) &
        (
            Q(experto_solicitado=request.user) |
            Q(experto_solicitado__isnull=True, idServicios__in=request.user.especialidad.all())
        )
    ).select_related('idUsuario', 'idServicios').order_by('Fecha', 'Hora')

    for reserva in reservas_pendientes:
        categorias_experto = set(request.user.especialidad.values_list('idCategorias', flat=True))
        categoria_reserva = reserva.idServicios.idCategorias_id
        reserva.especialidad_permitida = categoria_reserva in categorias_experto

    reservas_asignadas = Reserva.objects.filter(
        experto_asignado=request.user,
        motivo_cancelacion__isnull=True
    ).exclude(
        Q(idEstado=estado_pendiente) |
        Q(idEstado=estado_finalizado) |
        Q(idEstado__Nombre='Rechazada')  # ✅ ← CORRECCIÓN agregada aquí
    ).select_related('idUsuario', 'idServicios')

    reservas_canceladas = Reserva.objects.filter(
        experto_asignado=request.user,
        motivo_cancelacion__isnull=False
    ).order_by('-Fecha', '-Hora')

    reservas_rechazadas = Reserva.objects.filter(
        experto_asignado=request.user,
        idEstado=estado_rechazada
    ).select_related('idUsuario', 'idServicios').order_by('-Fecha', '-Hora')

    mensajes_no_leidos = {
        reserva.idUsuario.id: Mensaje.objects.filter(
            emisor=reserva.idUsuario,
            receptor=request.user,
            leido=False
        ).count()
        for reserva in reservas_asignadas
        if Mensaje.objects.filter(
            emisor=reserva.idUsuario,
            receptor=request.user,
            leido=False
        ).exists()
    }

    puede_calificar_experto = {
        reserva.id: not Calificaciones.objects.filter(
            reserva=reserva,
            calificado_por=request.user,
            tipo='experto_a_cliente'
        ).exists()
        if reserva.servicio_finalizado else False
        for reserva in reservas_asignadas
    }

    promedio_calificacion = obtener_promedio_calificaciones_experto(request.user)
    estrellas = int(round(promedio_calificacion or 0))

    disponibilidades = Disponibilidad.objects.filter(
        experto=request.user
    ).order_by('-fecha', 'hora_inicio')

    dispo_dict = {
        d.fecha.strftime('%Y-%m-%d'): d.idEstado.Nombre if d.idEstado else ''
        for d in disponibilidades
    }

    return render(request, 'experto/dashboard_experto.html', {
        'reservas_pendientes': reservas_pendientes,
        'reservas_asignadas': reservas_asignadas,
        'reservas_canceladas': reservas_canceladas,
        'reservas_rechazadas': reservas_rechazadas,  # ✅ Añadido
        'user_especialidad': request.user.especialidad,
        'mensajes_no_leidos': mensajes_no_leidos,
        'puede_calificar_experto': puede_calificar_experto,
        'promedio_calificacion': promedio_calificacion,
        'estrellas': estrellas,
        'form_disponibilidad': form_disponibilidad,
        'disponibilidades': disponibilidades,
        'dispo_dict': dispo_dict,
        'mostrar_mensaje_finalizado': mostrar_mensaje_finalizado,
        'reserva_id_calificar': reserva_id_calificar,
    })





@login_required
def principal(request):
    # ✅ Forzar recarga del usuario desde la base de datos
    User = get_user_model()
    usuario_actualizado = User.objects.get(id=request.user.id)

    # ✅ Redireccionar si es cliente y su estado no es 'aprobado'
    if usuario_actualizado.tipo_usuario == 'cliente' and usuario_actualizado.aprobado_cliente != 'aprobado':
        if usuario_actualizado.aprobado_cliente == 'rechazado':
            messages.error(request, "Tu cuenta ha sido rechazada por un administrador.")
            return render(request, 'cliente/cliente_rechazado.html')  # ✅ Nuevo template para rechazados
        else:
            messages.warning(request, "Tu cuenta aún está siendo revisada por un administrador.")
            return render(request, 'cliente/cliente_en_aprobacion.html')  # Pendiente

    if usuario_actualizado.tipo_usuario == 'experto':
        return redirect('dashboard_experto')
    elif usuario_actualizado.tipo_usuario == 'admin':
        return redirect('admin_principal')

    categorias = Categorias.objects.all()
    servicios = Servicios.objects.all()
    servicios_por_categoria = {
        cat.Nombre: list(servicios.filter(idCategorias=cat))
        for cat in categorias
    }

    ultimas_reservas = Reserva.objects.filter(
        idUsuario=request.user
    ).exclude(
        Q(idEstado__Nombre='Cancelado') | Q(idEstado__Nombre='Completada')
    ).order_by('-Fecha', '-Hora')[:3]

    try:
        estado_aceptada = Estado.objects.get(Nombre='Aceptada')
    except Estado.DoesNotExist:
        estado_aceptada = None

    # === VERIFICAR RESERVA ACTIVA (NO CANCELADA NI FINALIZADA) ===
    reserva_aceptada = None
    if estado_aceptada:
        try:
            # Obtener todos los estados que deben excluirse
            estado_cancelado = Estado.objects.get(Nombre='Cancelado')
            estado_finalizado = Estado.objects.get(Nombre='Finalizado')
            
            # Buscar reserva aceptada que esté activa (no cancelada, no finalizada)
            reserva_aceptada = Reserva.objects.filter(
                idUsuario=request.user,
                idEstado=estado_aceptada,
                experto_asignado__isnull=False,
                servicio_finalizado=False  # Solo servicios no finalizados
            ).exclude(
                Q(idEstado=estado_cancelado) | Q(idEstado=estado_finalizado)
            ).order_by('-Fecha', '-Hora').first()
            
            # 🔥 DEBUG: Verificar que no haya reservas canceladas en el resultado
            if reserva_aceptada:
                print(f"🟢 DEBUG: Reserva aceptada encontrada - ID: {reserva_aceptada.id}, Estado: {reserva_aceptada.idEstado.Nombre}")
                # Doble verificación por seguridad
                if reserva_aceptada.idEstado.Nombre in ['Cancelado', 'Finalizado']:
                    print("🚨 ERROR: Se encontró una reserva cancelada/finalizada cuando no debería!")
                    reserva_aceptada = None
            else:
                print("🔵 DEBUG: No se encontró ninguna reserva aceptada activa")
            
        except Estado.DoesNotExist as e:
            print(f"⚠️ Estado no encontrado: {e}")
            reserva_aceptada = None

    # === GUARDAR COMENTARIO DEL CLIENTE SI EL SERVICIO ESTÁ INICIADO ===
    if request.method == 'POST':
        comentario_cliente = request.POST.get('comentario_cliente', '').strip()
        reserva_id = request.POST.get('reserva_id')

        print("🟡 POST recibido con comentario:", comentario_cliente)
        print("🟡 Reserva ID recibida:", reserva_id)

        if comentario_cliente and reserva_id:
            try:
                reserva = Reserva.objects.get(id=reserva_id, idUsuario=request.user)
                print("🔵 Reserva encontrada:", reserva.id)

                if reserva.servicio_iniciado and not reserva.servicio_finalizado:
                    print("🟢 Condiciones válidas para guardar comentario")
                    reserva.comentario_cliente = comentario_cliente
                    reserva.save()
                    print("✅ Comentario del cliente guardado")
                else:
                    print("🔴 Servicio no iniciado o ya finalizado")
            except Reserva.DoesNotExist:
                print("❌ No se encontró la reserva con ID", reserva_id)

    # === MENSAJES NO LEÍDOS ===
    mensajes_no_leidos = {}
    if reserva_aceptada:
        experto = reserva_aceptada.experto_asignado
        mensajes_sin_leer = Mensaje.objects.filter(
            emisor=experto,
            receptor=request.user,
            leido=False
        ).count()

        if mensajes_sin_leer > 0:
            mensajes_no_leidos[experto.id] = mensajes_sin_leer

    puede_calificar = False
    servicio_para_calificar = None
    if reserva_aceptada and reserva_aceptada.servicio_finalizado and reserva_aceptada.experto_asignado:
        ya_calificado = Calificaciones.objects.filter(
            reserva=reserva_aceptada,
            calificado_por=request.user,
            tipo='cliente_a_experto'
        ).exists()
        if not ya_calificado and request.user == reserva_aceptada.idUsuario:
            puede_calificar = True
            servicio_para_calificar = reserva_aceptada
    
    # === BUSCAR OTROS SERVICIOS FINALIZADOS PENDIENTES DE CALIFICAR ===
    if not servicio_para_calificar:
        # Buscar servicios finalizados sin calificar y donde NO se haya descartado la notificación
        servicios_sin_calificar = Reserva.objects.filter(
            idUsuario=request.user,
            servicio_finalizado=True,
            idEstado__Nombre='Finalizado',
            notificacion_calificar_descartada=False  # NUEVO: Solo mostrar si no se descartó
        ).exclude(
            id__in=Calificaciones.objects.filter(
                calificado_por=request.user,
                tipo='cliente_a_experto'
            ).values_list('reserva_id', flat=True)
        ).order_by('-actualizado_en').first()
        
        if servicios_sin_calificar:
            servicio_para_calificar = servicios_sin_calificar
            puede_calificar = True

    # === DISPONIBILIDAD DE EXPERTOS ===
    expertos = CustomUser.objects.filter(tipo_usuario='experto', verificado='aprobado')
    disponibilidad_por_experto = {
        experto.id: Disponibilidad.objects.filter(experto=experto)
        for experto in expertos
    }

    # === INFORMACIÓN DE CANCELACIÓN (SOLO UNA VEZ) ===
    reserva_cancelada_info = None
    if 'reserva_cancelada' in request.session:
        cancelacion_data = request.session['reserva_cancelada']
        # Solo mostrar si no se ha mostrado antes
        if not cancelacion_data.get('mostrado', False):
            reserva_cancelada_info = cancelacion_data
            # Marcar como mostrado
            request.session['reserva_cancelada']['mostrado'] = True
            request.session.modified = True
        else:
            # Si ya se mostró, eliminar de la sesión
            del request.session['reserva_cancelada']

    # === LIMPIEZA DE SESIÓN (datos antiguos) ===
    # Limpiar datos de reservas exitosas antiguas si existen
    if 'mensaje_reserva' in request.session:
        # Opcional: puedes añadir lógica para limpiar mensajes de reserva antiguos
        pass

    return render(request, 'principal.html', {
        'categorias': categorias,
        'servicios_por_categoria': servicios_por_categoria,
        'ultimas_reservas': ultimas_reservas,
        'reserva_aceptada': reserva_aceptada,
        'mensajes_no_leidos': mensajes_no_leidos,
        'puede_calificar': puede_calificar,
        'servicio_para_calificar': servicio_para_calificar,  # 🔥 NUEVO: servicio específico para calificar
        'reserva_cancelada_info': reserva_cancelada_info,  # 🔥 NUEVO: información de cancelación una sola vez

        # 👇 Agregados
        'expertos': expertos,
        'disponibilidad_por_experto': disponibilidad_por_experto,
    })



@login_required
@usuario_aprobado_required
@user_passes_test(is_cliente, login_url=reverse_lazy('login')) 
def reserva(request):
    from doit_app.models import CustomUser  # ✅ Import al principio
    
    servicio_id = request.GET.get('servicio_id') or request.session.get('servicio_id')
    experto_id = request.GET.get('experto_id')  # ✅ Capturar experto desde la URL

    # Si viene un experto pero no un servicio, intentar usar el primer servicio del experto
    if experto_id and not servicio_id:
        experto = CustomUser.objects.filter(pk=experto_id).first()
        if experto and experto.especialidad.exists():
            servicio_id = experto.especialidad.first().id
            request.session['servicio_id'] = servicio_id

    if not servicio_id:
        messages.error(request, "⚠️ Servicio no seleccionado. Por favor, elige un servicio.")
        return redirect('principal')

    servicio = get_object_or_404(Servicios, id=servicio_id)
    request.session['servicio_id'] = servicio_id

    experto_seleccionado = None  # ✅ nuevo

    if request.method == 'POST':
        form = ReservaForm(request.POST, experto_id=experto_id)

        pais_id = request.POST.get('pais')
        if pais_id:
            form.fields['ciudad'].queryset = Ciudad.objects.filter(departamento__pais_id=pais_id)
        else:
            form.fields['ciudad'].queryset = Ciudad.objects.none()

        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.idUsuario = request.user
            reserva.idServicios = servicio

            fecha_seleccionada = reserva.Fecha

            if experto_id:
                experto = CustomUser.objects.filter(pk=experto_id).first()
                if experto:
                    experto_seleccionado = experto  # ✅ mostrar en template
                    
                    # Validar que el servicio seleccionado esté en las especialidades del experto
                    if not experto.especialidad.filter(id=servicio.id).exists():
                        messages.error(request, f"❌ El servicio '{servicio.NombreServicio}' no está disponible para el experto {experto.get_full_name()}.")
                        return redirect('reserva')
                    
                    # Verificar disponibilidad del experto específico
                    no_disponible_manual = Disponibilidad.objects.filter(
                        experto=experto,
                        fecha=fecha_seleccionada,
                        idEstado__Nombre__iexact='No disponible'
                    ).exists()
                    
                    # Verificar si tiene una reserva aceptada no finalizada ese día
                    reserva_activa = Reserva.objects.filter(
                        experto_asignado=experto,
                        Fecha=fecha_seleccionada,
                        idEstado__Nombre='Aceptada',
                        servicio_finalizado=False
                    ).exists()

                    if no_disponible_manual or reserva_activa:
                        motivo = "no está disponible" if no_disponible_manual else "ya tiene un servicio en curso"
                        messages.error(request, f"❌ El experto {experto.get_full_name()} {motivo} en la fecha seleccionada.")
                        return redirect('reserva')

                    reserva.experto_solicitado = experto
            else:
                # Buscar expertos disponibles para la fecha seleccionada
                expertos_disponibles = CustomUser.objects.filter(
                    tipo_usuario='experto',
                    especialidad=servicio,
                    is_active=True
                ).exclude(
                    # Excluir expertos con disponibilidad marcada como "No disponible"
                    disponibilidad__fecha=fecha_seleccionada,
                    disponibilidad__idEstado__Nombre__iexact='No disponible'
                ).exclude(
                    # Excluir expertos con reservas aceptadas no finalizadas ese día
                    reservas_aceptadas__Fecha=fecha_seleccionada,
                    reservas_aceptadas__idEstado__Nombre='Aceptada',
                    reservas_aceptadas__servicio_finalizado=False
                ).distinct()

                if not expertos_disponibles.exists():
                    messages.error(request, "❌ No hay expertos disponibles en esa fecha. Intenta con otra fecha.")
                    return redirect('reserva')

            try:
                estado_pendiente = Estado.objects.get(Nombre='Pendiente')
                reserva.idEstado = estado_pendiente
            except Estado.DoesNotExist:
                messages.error(request, "Error interno: El estado 'Pendiente' no se encontró en la base de datos.")
                return redirect('principal')

            reserva.save()

            # Las notificaciones se envían a todos los expertos con esa especialidad
            expertos = CustomUser.objects.filter(tipo_usuario='experto', especialidad=servicio)
            for experto in expertos:
                Notificacion.objects.create(
                    usuario=experto,
                    mensaje=f'Nuevo servicio disponible: {servicio.NombreServicio}',
                    url=''
                )

            request.session['mensaje_reserva'] = {
                'servicio': servicio.NombreServicio,
                'fecha': reserva.Fecha.strftime('%d/%m/%Y'),
                'hora': reserva.Hora.strftime('%H:%M'),
                'direccion': reserva.direccion,
                'ciudad': reserva.ciudad.Nombre if reserva.ciudad else 'No especificada',
                'reserva_id': reserva.id  # Agregar ID de la reserva para poder cancelarla
            }

            return redirect('principal')
        else:
            messages.error(request, '❌ Hubo un error al procesar tu reserva. Por favor, revisa los datos.')
    else:
        initial_data = {'idServicios': servicio}
        if experto_id:
            initial_data['experto_solicitado'] = experto_id
            experto_seleccionado = CustomUser.objects.filter(pk=experto_id).first()  # ✅ mostrar en template

        form = ReservaForm(initial=initial_data, experto_id=experto_id)

    # Obtener todos los días no disponibles de todos los expertos
    dias_no_disponibles = []
    
    if experto_id:
        # Si se seleccionó un experto específico, sus días no disponibles
        experto = CustomUser.objects.filter(pk=experto_id).first()
        if experto:
            # 1. Días marcados manualmente como "No disponible" en Disponibilidad
            dias_disponibilidad = list(
                Disponibilidad.objects.filter(
                    experto=experto,
                    idEstado__Nombre__iexact='No disponible'
                ).values_list('fecha', flat=True)
            )
            
            # 2. Días con reservas aceptadas pero no finalizadas
            dias_reservas_activas = list(
                Reserva.objects.filter(
                    experto_asignado=experto,
                    idEstado__Nombre='Aceptada',
                    servicio_finalizado=False
                ).values_list('Fecha', flat=True)
            )
            
            # Combinar ambos conjuntos y eliminar duplicados
            todas_fechas_no_disponibles = dias_disponibilidad + dias_reservas_activas
            dias_no_disponibles = list(set([d.strftime('%Y-%m-%d') for d in todas_fechas_no_disponibles]))
    else:
        # Si no hay experto específico, mostrar días ocupados de todos los expertos
        # que tengan la especialidad del servicio seleccionado
        expertos_con_especialidad = CustomUser.objects.filter(
            tipo_usuario='experto',
            especialidad=servicio,
            is_active=True
        )
        
        # 1. Días marcados manualmente como "No disponible" en Disponibilidad
        dias_disponibilidad = list(
            Disponibilidad.objects.filter(
                experto__in=expertos_con_especialidad,
                idEstado__Nombre__iexact='No disponible'
            ).values_list('fecha', flat=True)
        )
        
        # 2. Días con reservas aceptadas pero no finalizadas de expertos con esa especialidad
        dias_reservas_activas = list(
            Reserva.objects.filter(
                experto_asignado__in=expertos_con_especialidad,
                idEstado__Nombre='Aceptada',
                servicio_finalizado=False
            ).values_list('Fecha', flat=True)
        )
        
        # Combinar ambos conjuntos y eliminar duplicados
        todas_fechas_no_disponibles = dias_disponibilidad + dias_reservas_activas
        dias_no_disponibles = list(set([d.strftime('%Y-%m-%d') for d in todas_fechas_no_disponibles]))

    return render(request, 'reserva.html', {
        'form': form,
        'servicio': servicio,
        'servicio_seleccionado': servicio,  # ✅ Para mostrar en el template
        'experto_id': experto_id,
        'dias_no_disponibles': dias_no_disponibles,
        'experto_seleccionado': experto_seleccionado,  # ✅ NUEVO: pasa al template
        'cantidad_dias_ocupados': len(dias_no_disponibles),  # ✅ NUEVO: información adicional
    })


@login_required
@usuario_aprobado_required
@user_passes_test(is_cliente, login_url=reverse_lazy('login'))
def cancelar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)

    # Solo el cliente que creó la reserva puede cancelarla
    if reserva.idUsuario != request.user:
        messages.error(request, "No tienes permiso para cancelar esta reserva.")
        return redirect('principal')

    if request.method == 'POST':
        motivo = request.POST.get('motivo')
        otro_motivo = request.POST.get('otro_motivo', '').strip()

        # Determinar el motivo final
        if motivo == 'otra' and otro_motivo:
            motivo_final = otro_motivo
        elif motivo:
            motivo_final = motivo
        else:
            messages.error(request, "Debes seleccionar un motivo de cancelación.")
            return redirect('principal')

        # Cambiar estado a cancelado
        try:
            estado_cancelado = Estado.objects.get(Nombre='Cancelado')
        except Estado.DoesNotExist:
            messages.error(request, "No se pudo cancelar la reserva. Estado 'Cancelado' no existe.")
            return redirect('principal')
        
        # Si la reserva estaba aceptada y tenía un experto asignado, liberar su disponibilidad
        if reserva.experto_asignado and reserva.idEstado.Nombre == 'Aceptada':
            estado_no_disp = Estado.objects.get(Nombre='No disponible')
            # Eliminar la marca de no disponible para ese día y experto
            Disponibilidad.objects.filter(
                experto=reserva.experto_asignado,
                fecha=reserva.Fecha,
                idEstado=estado_no_disp
            ).delete()
        
        reserva.idEstado = estado_cancelado
        reserva.motivo_cancelacion = motivo_final
        
        # 🔥 NUEVO: Resetear campos de servicio para evitar confusión en la UI
        reserva.servicio_iniciado = False
        reserva.servicio_finalizado = False  # NO marcar como finalizado si se cancela
        
        reserva.save()

        # 🔥 NUEVO: Guardar información de cancelación en sesión para mostrar una sola vez
        request.session['reserva_cancelada'] = {
            'id': reserva.id,
            'servicio': reserva.idServicios.NombreServicio,
            'fecha': reserva.Fecha.strftime('%d/%m/%Y'),
            'hora': reserva.Hora.strftime('%H:%M'),
            'motivo': motivo_final,
            'mostrado': False  # Controla si ya se mostró
        }

        # 🔥 NUEVO: Si la reserva cancelada corresponde a la reserva recién creada, limpiar mensaje_reserva
        if ('mensaje_reserva' in request.session and 
            'reserva_id' in request.session['mensaje_reserva'] and 
            str(request.session['mensaje_reserva']['reserva_id']) == str(reserva.id)):
            del request.session['mensaje_reserva']

        messages.success(request, "Servicio cancelado satisfactoriamente")
        return redirect('principal')

    return redirect('principal')


@login_required
@usuario_aprobado_required
@user_passes_test(is_cliente, login_url=reverse_lazy('login'))
def mis_reservas_cliente(request):
    from doit_app.models import Calificaciones, Notificacion
    
    # Obtener parámetros de filtrado
    orden = request.GET.get('orden', 'fecha_desc')  # Por defecto: fecha descendente
    estado_filtro = request.GET.get('estado', 'todos')
    
    # Base queryset
    reservas = Reserva.objects.filter(idUsuario=request.user)
    
    # Filtrar por estado si se especifica
    if estado_filtro != 'todos':
        if estado_filtro == 'pendiente':
            reservas = reservas.filter(idEstado__Nombre='Pendiente')
        elif estado_filtro == 'en_proceso':
            reservas = reservas.filter(servicio_iniciado=True, servicio_finalizado=False)
        elif estado_filtro == 'finalizado':
            reservas = reservas.filter(idEstado__Nombre='Finalizado')
        elif estado_filtro == 'cancelado':
            reservas = reservas.filter(idEstado__Nombre='Cancelado')
    
    # Aplicar ordenamiento
    if orden == 'fecha_asc':
        reservas = reservas.order_by('creado_en')
    elif orden == 'fecha_desc':
        reservas = reservas.order_by('-creado_en')
    elif orden == 'estado':
        reservas = reservas.order_by('idEstado__Nombre', '-creado_en')
    elif orden == 'calificacion_desc':
        # Ordenar por calificación (si existe), luego por fecha
        reservas = reservas.annotate(
            tiene_calificacion=Exists(
                Calificaciones.objects.filter(
                    reserva=OuterRef('pk'),
                    calificado_por=request.user,
                    tipo='cliente_a_experto'
                )
            )
        ).order_by('-tiene_calificacion', '-creado_en')
    elif orden == 'calificacion_asc':
        reservas = reservas.annotate(
            tiene_calificacion=Exists(
                Calificaciones.objects.filter(
                    reserva=OuterRef('pk'),
                    calificado_por=request.user,
                    tipo='cliente_a_experto'
                )
            )
        ).order_by('tiene_calificacion', '-creado_en')
    else:
        reservas = reservas.order_by('-creado_en')
    
    # Anexar si ya fue calificado por el cliente
    for reserva in reservas:
        # Buscar calificación existente del cliente hacia el experto
        calif = Calificaciones.objects.filter(
            reserva=reserva, 
            calificado_por=request.user, 
            tipo='cliente_a_experto'
        ).first()
        reserva.calificacion_cliente = calif

    context = {
        'reservas': reservas,
        'orden_actual': orden,
        'estado_actual': estado_filtro,
    }
    return render(request, 'cliente/mis_reservas.html', context)



def ciudades_por_pais(request):
    pais_id = request.GET.get('pais_id')
    if pais_id:
        ciudades = Ciudad.objects.filter(departamento__pais_id=pais_id).values('id', 'Nombre')
        return JsonResponse(list(ciudades), safe=False)
    return JsonResponse({'error': 'No se proporcionó un ID de país'}, status=400)




@login_required
@usuario_aprobado_required
def busc_experto(request):
    q = request.GET.get('q', '').strip()
    fecha = request.GET.get('fecha', '').strip()  # nueva línea
    expertos = []

    if q:
        expertos = CustomUser.objects.filter(
            tipo_usuario='experto'
        ).annotate(
            nombre_completo=Concat(
                models.F('first_name'),
                Value(' '),
                models.F('last_name'),
                output_field=CharField()
            )
        ).filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(nombre_completo__icontains=q) |
            Q(especialidad__NombreServicio__icontains=q)
        ).distinct()

        # 👇 Si hay fecha, anotar si el experto NO está disponible
        if fecha:
            # Verificar disponibilidad manual
            subquery_disponibilidad = Disponibilidad.objects.filter(
                experto=OuterRef('pk'),
                fecha=fecha,
                idEstado__Nombre__iexact='No disponible'
            )
            
            # Verificar reservas activas
            subquery_reservas = Reserva.objects.filter(
                experto_asignado=OuterRef('pk'),
                Fecha=fecha,
                idEstado__Nombre='Aceptada',
                servicio_finalizado=False
            )
            
            expertos = expertos.annotate(
                no_disponible_manual=Exists(subquery_disponibilidad),
                reserva_activa=Exists(subquery_reservas)
            ).annotate(
                no_disponible=Case(
                    When(Q(no_disponible_manual=True) | Q(reserva_activa=True), then=True),
                    default=False,
                    output_field=BooleanField()
                )
            )


    # Obtener días NO disponibles para cada experto
    disponibilidad_por_experto = {}
    for experto in expertos:
        # 1. Días marcados manualmente como "No disponible" en Disponibilidad
        dias_disponibilidad = list(
            Disponibilidad.objects.filter(
                experto=experto,
                idEstado__Nombre__iexact='No disponible'
            ).values_list('fecha', flat=True)
        )
        
        # 2. Días con reservas aceptadas pero no finalizadas
        dias_reservas_activas = list(
            Reserva.objects.filter(
                experto_asignado=experto,
                idEstado__Nombre='Aceptada',
                servicio_finalizado=False
            ).values_list('Fecha', flat=True)
        )
        
        # Combinar ambos conjuntos y eliminar duplicados
        todas_fechas_no_disponibles = dias_disponibilidad + dias_reservas_activas
        dias_no_str = list(set([d.strftime('%Y-%m-%d') for d in todas_fechas_no_disponibles]))
        disponibilidad_por_experto[experto.id] = dias_no_str

    return render(request, 'busc_experto.html', {
        'searched_expert': q,
        'expertos': expertos,
        'fecha': fecha,  # Pasamos la fecha al template
        'disponibilidad_por_experto': disponibilidad_por_experto,
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

            # Sincronizar disponibilidad: marcar ese día como NO disponible para el experto
            estado_no_disp = Estado.objects.get(Nombre='No disponible')
            # Si no existe ya una marca de no disponible para ese día y experto, la creamos
            if not Disponibilidad.objects.filter(experto=request.user, fecha=reserva.Fecha, idEstado=estado_no_disp).exists():
                Disponibilidad.objects.create(
                    experto=request.user,
                    fecha=reserva.Fecha,
                    hora_inicio=reserva.Hora,
                    hora_fin=reserva.Hora,  # O ajusta según tu lógica de duración
                    idEstado=estado_no_disp
                )

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
                if reserva.idEstado.Nombre == 'Aceptada':
                    estado_no_disp = Estado.objects.get(Nombre='No disponible')
                    Disponibilidad.objects.filter(
                        experto=request.user,
                        fecha=reserva.Fecha,
                        idEstado=estado_no_disp
                    ).delete()

                # ✅ Ya no eliminamos experto_asignado

            else:
                # ✅ Si aún no tenía experto_asignado, lo asignamos antes de rechazar
                reserva.experto_asignado = request.user

            estado_rechazada = Estado.objects.get(Nombre='Rechazada')
            reserva.idEstado = estado_rechazada
            reserva.save()

            messages.success(request, "La reserva ha sido rechazada correctamente.")
            return redirect('dashboard_experto')
        except Estado.DoesNotExist:
            messages.error(request, "El estado 'Rechazada' no existe en la base de datos.")
            return redirect('dashboard_experto')
        except Exception as e:
            messages.error(request, f"Ocurrió un error al rechazar la reserva: {e}")
            return redirect('dashboard_experto')

    return render(request, 'experto/confirmar_rechazar_reserva.html', {'reserva': reserva})



    

@login_required
@usuario_aprobado_required
@user_passes_test(is_experto, login_url=reverse_lazy('login'))
def historial_experto(request):
    from doit_app.models import Calificaciones, Estado

    # Obtener parámetros de filtrado
    orden = request.GET.get('orden', 'fecha_desc')  # Por defecto: fecha descendente

    # Base queryset - solo servicios finalizados
    reservas_finalizadas = Reserva.objects.filter(
        experto_asignado=request.user,
        servicio_finalizado=True
    )

    # ✅ Reservas rechazadas también
    estado_rechazada = Estado.objects.filter(Nombre='Rechazada').first()
    reservas_rechazadas = Reserva.objects.filter(
        experto_asignado=request.user,
        idEstado=estado_rechazada
    ).order_by('-Fecha', '-Hora')

    # Aplicar ordenamiento a finalizadas
    if orden == 'fecha_asc':
        reservas_finalizadas = reservas_finalizadas.order_by('Fecha', 'Hora')
    elif orden == 'fecha_desc':
        reservas_finalizadas = reservas_finalizadas.order_by('-Fecha', '-Hora')
    elif orden == 'calificacion_recibida_desc':
        reservas_finalizadas = reservas_finalizadas.annotate(
            calificacion_valor=models.Subquery(
                Calificaciones.objects.filter(
                    reserva=OuterRef('pk'),
                    tipo='cliente_a_experto'
                ).values('puntuacion')[:1]
            )
        ).order_by('-calificacion_valor', '-Fecha')
    elif orden == 'calificacion_recibida_asc':
        reservas_finalizadas = reservas_finalizadas.annotate(
            calificacion_valor=models.Subquery(
                Calificaciones.objects.filter(
                    reserva=OuterRef('pk'),
                    tipo='cliente_a_experto'
                ).values('puntuacion')[:1]
            )
        ).order_by('calificacion_valor', '-Fecha')
    elif orden == 'calificacion_dada_desc':
        reservas_finalizadas = reservas_finalizadas.annotate(
            calificacion_dada_valor=models.Subquery(
                Calificaciones.objects.filter(
                    reserva=OuterRef('pk'),
                    tipo='experto_a_cliente'
                ).values('puntuacion')[:1]
            )
        ).order_by('-calificacion_dada_valor', '-Fecha')
    elif orden == 'calificacion_dada_asc':
        reservas_finalizadas = reservas_finalizadas.annotate(
            calificacion_dada_valor=models.Subquery(
                Calificaciones.objects.filter(
                    reserva=OuterRef('pk'),
                    tipo='experto_a_cliente'
                ).values('puntuacion')[:1]
            )
        ).order_by('calificacion_dada_valor', '-Fecha')
    else:
        reservas_finalizadas = reservas_finalizadas.order_by('-Fecha', '-Hora')

    # Historial con calificaciones
    historial = []
    for reserva in reservas_finalizadas:
        calif_cliente = Calificaciones.objects.filter(reserva=reserva, tipo='cliente_a_experto').first()
        calif_experto = Calificaciones.objects.filter(reserva=reserva, tipo='experto_a_cliente').first()
        historial.append({
            'reserva': reserva,
            'calif_cliente': calif_cliente,
            'calif_experto': calif_experto
        })

    context = {
        'historial': historial,
        'orden_actual': orden,
        'reservas_rechazadas': reservas_rechazadas,  # ✅ Agregado
    }

    return render(request, 'experto/historial_experto.html', context)






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
        if request.user.tipo_usuario == 'experto':
            return redirect('dashboard_experto')
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

            if user.tipo_usuario == 'experto':
                return redirect('dashboard_experto')
            return redirect('principal')

        else:
            messages.error(request, '❌ Error al registrarte. Revisa los datos.')
            print("Errores del formulario:", form.errors)
    else:
        form = RegistroForm()

    return render(request, 'registrarse.html', {
        'form': form,
        'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY
    })



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

@login_required
def historial_cliente(request):
    from doit_app.models import Calificaciones
    reservas_finalizadas = Reserva.objects.filter(
        idUsuario=request.user,
        servicio_finalizado=True
    ).order_by('-Fecha', '-Hora')
    historial = []
    for reserva in reservas_finalizadas:
        calif_cliente = Calificaciones.objects.filter(reserva=reserva, tipo='cliente_a_experto').first()
        calif_experto = Calificaciones.objects.filter(reserva=reserva, tipo='experto_a_cliente').first()
        historial.append({
            'reserva': reserva,
            'calif_cliente': calif_cliente,
            'calif_experto': calif_experto
        })
    return render(request, 'cliente/historial_cliente.html', {
        'historial': historial
    })

@login_required
@usuario_aprobado_required
def notificaciones(request):
    notificaciones = Notificacion.objects.filter(usuario=request.user).order_by('-fecha')
    # Marcar como leídas todas las no leídas
    Notificacion.objects.filter(usuario=request.user, leida=False).update(leida=True)
    return render(request, 'notificaciones.html', {'notificaciones': notificaciones})


def busc_experto_sugerencias(request):
    q = request.GET.get('q', '').strip()
    sugerencias = []
    if q:
        expertos = CustomUser.objects.filter(
            tipo_usuario='experto'
        ).filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(especialidad__NombreServicio__icontains=q)
        ).distinct()[:8]
        for experto in expertos:
            nombre = experto.get_full_name() or experto.username
            # Si la búsqueda coincide con parte del nombre, muestra el nombre
            if q.lower() in nombre.lower() or q.lower() in (experto.username or '').lower():
                texto = nombre
            else:
                # Si coincide con alguna especialidad, muestra solo la especialidad coincidente
                especialidad_match = next((esp.NombreServicio for esp in experto.especialidad.all() if q.lower() in esp.NombreServicio.lower()), None)
                texto = especialidad_match if especialidad_match else nombre
            sugerencias.append({'id': experto.id, 'texto': texto})
    return JsonResponse({'sugerencias': sugerencias})

def expertos_por_especialidad(request):
    servicio_id = request.GET.get('servicio_id')
    expertos = []
    if servicio_id:
        expertos = CustomUser.objects.filter(
            tipo_usuario='experto',
            especialidad__id=servicio_id
        ).distinct()
    data = [
        {
            'id': e.id,
            'nombre': e.get_full_name() or e.username,
            'foto': e.foto_perfil.url if e.foto_perfil else '',
            'especialidades': ', '.join([esp.NombreServicio for esp in e.especialidad.all()]),
            'username': e.username
        }
        for e in expertos
    ]
    return JsonResponse({'expertos': data})

@login_required
@usuario_aprobado_required
def experto_perfil(request):
    """Vista para el perfil del experto"""
    # Promedio de calificaciones del experto
    promedio_calificacion = obtener_promedio_calificaciones_experto(request.user)
    
    context = {
        'promedio_calificacion': promedio_calificacion,
    }
    
    return render(request, 'experto.html', context)

@login_required
@require_POST
def marcar_notificacion_leida(request):
    """Vista para marcar una notificación como leída vía AJAX"""
    reserva_id = request.POST.get('reserva_id')
    if reserva_id:
        try:
            # Buscar la notificación específica de calificación para esta reserva
            notificaciones = Notificacion.objects.filter(
                usuario=request.user,
                url=f'/calificar_reserva/{reserva_id}/',
                leida=False
            )
            
            # Marcar la reserva como descartada para que no vuelva a aparecer
            try:
                reserva = Reserva.objects.get(id=reserva_id, idUsuario=request.user)
                reserva.notificacion_calificar_descartada = True
                reserva.save()
            except Reserva.DoesNotExist:
                pass
            
            if notificaciones.exists():
                # Marcar todas las notificaciones coincidentes como leídas
                notificaciones.update(leida=True)
                return JsonResponse({
                    'status': 'success', 
                    'message': f'Notificación descartada correctamente'
                })
            else:
                # Aunque no haya notificación, ya marcamos la reserva como descartada
                return JsonResponse({'status': 'success', 'message': 'Notificación descartada correctamente'})
                    
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'ID de reserva no válido'})


@login_required
@usuario_aprobado_required
def pqr_view(request):
    from .forms import PQRForm
    from .models import PQR
    
    if request.method == 'POST':
        form = PQRForm(request.POST)
        if form.is_valid():
            pqr = form.save(commit=False)
            pqr.usuario = request.user
            pqr.save()
            
            # Enviar correo electrónico
            try:
                tipo_pqr = pqr.get_tipo_display()
                usuario_info = f"{request.user.get_full_name()}" if request.user.get_full_name() else request.user.username
                
                asunto_correo = f"Nuevo {tipo_pqr} - {pqr.asunto}"
                
                mensaje_correo = f"""
Has recibido un nuevo {tipo_pqr} desde la plataforma DOIT.

INFORMACIÓN DEL USUARIO:
- Nombre: {usuario_info}
- Usuario: {request.user.username}
- Email: {request.user.email}
- Tipo de usuario: {request.user.get_tipo_usuario_display()}
- Teléfono: {request.user.telefono or 'No registrado'}

DETALLES DEL {tipo_pqr.upper()}:
- Tipo: {tipo_pqr}
- Asunto: {pqr.asunto}
- Fecha: {pqr.fecha_creacion.strftime('%d/%m/%Y %H:%M')}

DESCRIPCIÓN:
{pqr.descripcion}

---
PQR ID: #{pqr.id}
Sistema DOIT - Plataforma de Servicios
                """
                
                send_mail(
                    subject=asunto_correo,
                    message=mensaje_correo,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['ose.luis.quintero@gmail.com'],
                    fail_silently=False,
                )
                
                messages.success(request, f'Tu {tipo_pqr.lower()} ha sido enviado exitosamente. Recibirás una respuesta pronto.')
                
            except Exception as e:
                messages.warning(request, f'Tu {tipo_pqr.lower()} fue registrado, pero hubo un problema enviando el correo. El equipo ha sido notificado.')
            
            # Redirigir según el tipo de usuario
            if request.user.tipo_usuario == 'cliente':
                return redirect('principal')
            else:
                return redirect('dashboard_experto')
    else:
        form = PQRForm()
    
    return render(request, 'pqr_form.html', {
        'form': form,
        'titulo': 'Enviar PQR (Petición, Queja o Reclamo)'
    })


@login_required
@usuario_aprobado_required  
def mis_pqrs(request):
    """Vista para que el usuario vea sus PQRs enviados"""
    from .models import PQR
    
    pqrs = PQR.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    
    return render(request, 'mis_pqrs.html', {
        'pqrs': pqrs,
        'titulo': 'Mis PQRs'
    })

