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
from django.db.models import Q  # ← Esto soluciona lo de Q
from .models import Mensaje  # ← Asegúrate de importar tu modelo correctamente
from django.http import HttpResponseForbidden
from django.urls import reverse
from datetime import timedelta
from .models import Calificaciones
from django.contrib.auth.decorators import login_required
from .models import Notificacion
from django.db import models



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
    if request.user.tipo_usuario == 'experto':
        return redirect('dashboard_experto')
    elif request.user.tipo_usuario == 'admin':
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
        Q(idEstado__Nombre='Cancelada') | Q(idEstado__Nombre='Completada')
    ).order_by('-Fecha', '-Hora')[:3]

    try:
        estado_aceptada = Estado.objects.get(Nombre='Aceptada')
    except Estado.DoesNotExist:
        estado_aceptada = None

    reserva_aceptada = None
    if estado_aceptada:
        reserva_aceptada = Reserva.objects.filter(
            idUsuario=request.user,
            idEstado=estado_aceptada,
            experto_asignado__isnull=False
        ).order_by('-Fecha', '-Hora').first()

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
    if reserva_aceptada and reserva_aceptada.servicio_finalizado and reserva_aceptada.experto_asignado:
        ya_calificado = Calificaciones.objects.filter(
            reserva=reserva_aceptada,
            calificado_por=request.user,
            tipo='cliente_a_experto'
        ).exists()
        if not ya_calificado and request.user == reserva_aceptada.idUsuario:
            puede_calificar = True

    return render(request, 'principal.html', {
        'categorias': categorias,
        'servicios_por_categoria': servicios_por_categoria,
        'ultimas_reservas': ultimas_reservas,
        'reserva_aceptada': reserva_aceptada,
        'mensajes_no_leidos': mensajes_no_leidos,
        'puede_calificar': puede_calificar,
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

            # Notificación para expertos de la especialidad
            from doit_app.models import Notificacion, CustomUser
            expertos = CustomUser.objects.filter(tipo_usuario='experto', especialidad=servicio)
            for experto in expertos:
                Notificacion.objects.create(
                    usuario=experto,
                    mensaje=f'Nuevo servicio disponible: {servicio.NombreServicio}',
                    url=''  # Puedes poner la url de la reserva o dashboard
                )

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




def is_experto(user):
    return user.is_authenticated and user.tipo_usuario == 'experto'

@login_required
@user_passes_test(is_experto, login_url=reverse_lazy('login'))
def aceptar_reserva_experto(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)

    if reserva.idEstado.Nombre == "Aceptada" and reserva.experto_asignado:
        messages.warning(request, "Esta reserva ya fue aceptada por otro experto.")
        return redirect('dashboard_experto')

    try:
        estado_aceptada = Estado.objects.get(Nombre="Aceptada")
    except Estado.DoesNotExist:
        messages.error(request, "Error interno: el estado 'Aceptada' no está registrado.")
        return redirect('dashboard_experto')

    reserva.idEstado = estado_aceptada
    reserva.experto_asignado = request.user
    reserva.save()

    messages.success(request, "Has aceptado la reserva exitosamente.")
    return redirect('dashboard_experto')






@login_required
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

        # Cambiar estado a cancelado (ID 6, o el que uses)
        estado_cancelado = Estado.objects.get(Nombre='Cancelada')  # o Estado.objects.get(id=6)
        reserva.idEstado = estado_cancelado
        reserva.motivo_cancelacion = motivo_final
        reserva.save()

        messages.success(request, "La reserva ha sido cancelada correctamente.")
        return redirect('principal')

    return redirect('principal')





@login_required
@user_passes_test(lambda u: u.tipo_usuario == 'experto', login_url=reverse_lazy('login'))
@require_POST
def rechazar_reserva_experto(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)

    if reserva.experto_asignado and reserva.experto_asignado != request.user:
        messages.warning(request, "Esta reserva ya ha sido asignada a otro experto.")
        return redirect('dashboard_experto')

    try:
        estado_rechazada = Estado.objects.get(Nombre='Rechazada')
    except Estado.DoesNotExist:
        messages.error(request, "Error interno: el estado 'Rechazada' no está registrado.")
        return redirect('dashboard_experto')

    if reserva.experto_asignado == request.user:
        reserva.experto_asignado = None

    reserva.idEstado = estado_rechazada
    reserva.save()

    messages.info(request, "Has rechazado la reserva.")
    return redirect('dashboard_experto')















@login_required
@user_passes_test(is_cliente, login_url=reverse_lazy('login'))
def mis_reservas_cliente(request):
    from doit_app.models import Calificaciones, Notificacion
    reservas = Reserva.objects.filter(idUsuario=request.user).order_by('-creado_en')
    # Anexar si ya fue calificado por el cliente
    for reserva in reservas:
        calif = Calificaciones.objects.filter(reserva=reserva, calificado_por=request.user, tipo='cliente_a_experto').first()
        reserva.calificacion_cliente = calif

    # Notificaciones no leídas para el usuario actual
    notificaciones_no_leidas = Notificacion.objects.filter(usuario=request.user, leida=False).count()

    return render(request, 'cliente/mis_reservas.html', {'reservas': reservas, 'notificaciones_no_leidas': notificaciones_no_leidas})





@login_required
def busc_experto(request):
    q = request.GET.get('q', '').strip()
    expertos = []
    if q:
        # Buscar por nombre completo (first_name + ' ' + last_name)
        expertos = CustomUser.objects.filter(
            tipo_usuario='experto'
        ).annotate(
            nombre_completo=models.functions.Concat(
                models.F('first_name'),
                models.Value(' '),
                models.F('last_name'),
                output_field=models.CharField()
            )
        ).filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(nombre_completo__icontains=q) |
            Q(especialidad__NombreServicio__icontains=q)
        ).distinct()
    return render(request, 'busc_experto.html', {
        'searched_expert': q,
        'expertos': expertos
    })


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
from django.views.decorators.http import require_http_methods




@login_required(login_url='login')
@user_passes_test(lambda u: u.tipo_usuario == 'experto', login_url='login')
@require_http_methods(["GET", "POST"])
def dashboard_experto(request):
    print(f"DEBUG dashboard_experto: Accediendo. User: {request.user.username}, Tipo: {request.user.tipo_usuario}")

    if request.method == 'POST':
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
                    print(f"❌ Conflicto de horario para {request.user.username} en {reserva.Fecha} {reserva.Hora}")
                    return redirect('dashboard_experto')  # 🚨 REDIRECCIÓN INMEDIATA
                else:
                    if not reserva.experto_asignado and reserva.idServicios in request.user.especialidad.all():
                        # Al aceptar, desvincula este servicio de cualquier otro experto
                        Reserva.objects.filter(
                            id=reserva.id
                        ).exclude(
                            experto_asignado=request.user
                        ).update(experto_asignado=None)
                        reserva.experto_asignado = request.user
                        estado_aceptada = Estado.objects.get(Nombre='Aceptada')
                        reserva.idEstado = estado_aceptada
                        reserva.save()
                        messages.success(request, "Has aceptado correctamente la reserva.")
                        print(f"✅ Reserva {reserva_id} aceptada por {request.user.username}")
                        # Notificar al cliente que su servicio fue aceptado
                        from doit_app.models import Notificacion
                        Notificacion.objects.create(
                            usuario=reserva.idUsuario,
                            mensaje=f'Tu servicio "{reserva.idServicios.NombreServicio}" fue aceptado por el experto {request.user.get_full_name() or request.user.username}.',
                            url=''  # Puedes poner la url de la reserva o dashboard
                        )
                        return redirect('dashboard_experto')  # 🚨 REDIRECCIÓN INMEDIATA

            elif accion == 'iniciar_servicio':
                if reserva.experto_asignado == request.user and not reserva.servicio_iniciado:
                    reserva.servicio_iniciado = True
                    reserva.save()
                    messages.info(request, "Has iniciado el servicio.")
                    return redirect('dashboard_experto')  # 🚨 REDIRECCIÓN INMEDIATA

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
                    messages.success(request, "Has finalizado correctamente el servicio.")
                    if reserva.idUsuario:
                        return redirect('calificar_reserva', reserva_id=reserva.id)
                    return redirect('dashboard_experto')  # Seguridad extra

            return redirect('dashboard_experto')  # Redirección por defecto si no entra en ninguno

        except Reserva.DoesNotExist:
            messages.error(request, "La reserva no existe.")
        except Estado.DoesNotExist:
            messages.error(request, "Estado no encontrado.")
        except Exception as e:
            print(f"⚠️ Error inesperado: {e}")
            messages.error(request, "Ocurrió un error inesperado.")

        return redirect('dashboard_experto')  # Redirección por error

    # --- Lógica GET (SIN CAMBIOS) ---
    reservas_pendientes = Reserva.objects.filter(
        experto_asignado__isnull=True,
        idServicios__in=request.user.especialidad.all()
    ).select_related('idUsuario', 'idServicios').order_by('Fecha', 'Hora')

    for reserva in reservas_pendientes:
        categorias_experto = set(request.user.especialidad.values_list('idCategorias', flat=True))
        categoria_reserva = reserva.idServicios.idCategorias_id
        reserva.especialidad_permitida = categoria_reserva in categorias_experto

    reservas_asignadas = Reserva.objects.filter(
        experto_asignado=request.user,
        motivo_cancelacion__isnull=True
    ).select_related('idUsuario', 'idServicios')

    reservas_canceladas = Reserva.objects.filter(
        experto_asignado=request.user,
        motivo_cancelacion__isnull=False
    ).order_by('-Fecha', '-Hora')

    mensajes_no_leidos = {}
    for reserva in reservas_asignadas:
        cliente = reserva.idUsuario
        count = Mensaje.objects.filter(emisor=cliente, receptor=request.user, leido=False).count()
        if count > 0:
            mensajes_no_leidos[cliente.id] = count

    puede_calificar_experto = {}
    for reserva in reservas_asignadas:
        if reserva.servicio_finalizado:
            ya_calificado = Calificaciones.objects.filter(
                reserva=reserva,
                calificado_por=request.user,
                tipo='experto_a_cliente'
            ).exists()
            puede_calificar_experto[reserva.id] = not ya_calificado
        else:
            puede_calificar_experto[reserva.id] = False

    promedio_calificacion = obtener_promedio_calificaciones_experto(request.user)
    estrellas = int(round(promedio_calificacion or 0))

    # Notificaciones no leídas para el usuario actual
    from doit_app.models import Notificacion
    notificaciones_no_leidas = Notificacion.objects.filter(usuario=request.user, leida=False).count()

    return render(request, 'experto/dashboard_experto.html', {
        'reservas_pendientes': reservas_pendientes,
        'reservas_asignadas': reservas_asignadas,
        'reservas_canceladas': reservas_canceladas,
        'user_especialidad': request.user.especialidad,
        'mensajes_no_leidos': mensajes_no_leidos,
        'puede_calificar_experto': puede_calificar_experto,
        'promedio_calificacion': promedio_calificacion,
        'estrellas': estrellas,
        'notificaciones_no_leidas': notificaciones_no_leidas,
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
    from doit_app.models import Calificaciones
    reservas_finalizadas = Reserva.objects.filter(
        experto_asignado=request.user,
        servicio_finalizado=True
    ).order_by('-Fecha', '-Hora')
    # Obtener calificaciones recibidas y realizadas para cada reserva
    historial = []
    for reserva in reservas_finalizadas:
        calif_cliente = Calificaciones.objects.filter(reserva=reserva, tipo='cliente_a_experto').first()
        calif_experto = Calificaciones.objects.filter(reserva=reserva, tipo='experto_a_cliente').first()
        historial.append({
            'reserva': reserva,
            'calif_cliente': calif_cliente,
            'calif_experto': calif_experto
        })
    return render(request, 'experto/historial_experto.html', {
        'historial': historial
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












def regisexperto(request):
    if request.user.is_authenticated:
        if request.user.tipo_usuario == 'experto':
            return redirect('dashboard_experto')
        else:
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
            user.tipo_usuario = 'experto'  # Aseguramos que sea experto
            user.save()
            auth_login(request, user)
            messages.success(request, '🎉 ¡Registro de experto exitoso! Bienvenido a DoIt.')
            return redirect('dashboard_experto')
        else:
            messages.error(request, 'Hubo un error al registrarte como experto. Por favor, revisa los datos.')
            print("Errores del formulario de registro de experto:", form.errors)
    else:
        form = RegistroForm(initial={'tipo_usuario': 'experto'})

    return render(request, 'regisexperto.html', {
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




