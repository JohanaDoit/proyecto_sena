from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Reserva, Calificaciones
from .forms import CalificacionForm
from .views import usuario_aprobado_required

@login_required
@usuario_aprobado_required
def calificar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    user = request.user
    # Permitir que tanto el cliente como el experto califiquen
    if user == reserva.idUsuario:
        tipo = 'cliente_a_experto'
        calificado_a = reserva.experto_asignado
        redir = 'principal'
    elif user == reserva.experto_asignado:
        tipo = 'experto_a_cliente'
        calificado_a = reserva.idUsuario
        redir = 'dashboard_experto'
    else:
        messages.error(request, 'No tienes permiso para calificar esta reserva.')
        return redirect('home')

    # Evitar doble calificación
    calificacion_existente = Calificaciones.objects.filter(reserva=reserva, calificado_por=user, tipo=tipo).first()
    if calificacion_existente:
        messages.info(request, f'Ya has calificado esta reserva con {calificacion_existente.puntuacion} estrellas.')
        return redirect(redir)

    if request.method == 'POST':
        form = CalificacionForm(request.POST)
        if form.is_valid():
            calificacion = form.save(commit=False)
            calificacion.reserva = reserva
            calificacion.calificado_por = user
            calificacion.calificado_a = calificado_a
            calificacion.tipo = tipo
            calificacion.save()
            
            # Marcar la notificación de calificar como descartada si es el cliente
            if tipo == 'cliente_a_experto':
                reserva.notificacion_calificar_descartada = True
                reserva.save()
            
            messages.success(request, '¡Calificación registrada exitosamente!')
            return redirect(redir)
    else:
        form = CalificacionForm()

    return render(request, 'calificar_reserva.html', {
        'form': form,
        'reserva': reserva,
        'tipo': tipo,
        'calificado_a': calificado_a,
    })
