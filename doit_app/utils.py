from django.db.models import Avg
from .models import Calificaciones

def obtener_promedio_calificaciones_experto(experto):
    resultado = Calificaciones.objects.filter(
        calificado_a=experto,
        tipo='cliente_a_experto'
    ).aggregate(promedio=Avg('puntuacion'))
    promedio = resultado['promedio'] or 0
    # Redondear a 1 decimal para mostrar formato limpio (ej: 3.2, 4.3)
    return round(promedio, 1) if promedio > 0 else 0
