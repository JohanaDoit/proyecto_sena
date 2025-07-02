from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Reserva, Calificaciones
from .forms import CalificacionForm

@login_required
def calificar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    user = request.user
    # Solo permitir calificación del cliente hacia el experto
    if user == reserva.idUsuario:
        tipo = 'cliente_a_experto'
        calificado_a = reserva.experto_asignado
    else:
        messages.error(request, 'Solo el cliente puede calificar al experto en esta reserva.')
        return redirect('home')

    # Evitar doble calificación
    if Calificaciones.objects.filter(reserva=reserva, calificado_por=user, tipo=tipo).exists():
        messages.info(request, 'Ya has calificado esta reserva.')
        return redirect('home')


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
            return redirect('principal')
    else:
        form = CalificacionForm()

    return render(request, 'calificar_reserva.html', {
        'form': form,
        'reserva': reserva,
        'tipo': tipo,
        'calificado_a': calificado_a,
    })
