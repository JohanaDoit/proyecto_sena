from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Reserva, Calificaciones
from .forms import CalificacionForm

@login_required
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
    if Calificaciones.objects.filter(reserva=reserva, calificado_por=user, tipo=tipo).exists():
        messages.info(request, 'Ya has calificado esta reserva.')
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
