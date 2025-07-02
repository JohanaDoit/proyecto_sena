from django.db.models import Avg
from .models import Calificaciones

def obtener_promedio_calificaciones_experto(experto):
    resultado = Calificaciones.objects.filter(
        calificado_a=experto,
        tipo='cliente_a_experto'
    ).aggregate(promedio=Avg('puntuacion'))
    return resultado['promedio'] or 0
