from .models import Notificacion

def notificaciones_context(request):
    """Context processor para agregar el contador de notificaciones a todos los templates"""
    context = {}
    
    try:
        if request.user.is_authenticated:
            notificaciones_no_leidas = Notificacion.objects.filter(usuario=request.user, leida=False).count()
            context['notificaciones_no_leidas'] = notificaciones_no_leidas
            
            # Si es un experto, agregar el promedio de calificaciones
            if hasattr(request.user, 'tipo_usuario') and request.user.tipo_usuario == 'experto':
                try:
                    from .utils import obtener_promedio_calificaciones_experto
                    promedio_calificacion = obtener_promedio_calificaciones_experto(request.user)
                    context['promedio_calificacion'] = promedio_calificacion
                except Exception:
                    context['promedio_calificacion'] = 0
        else:
            context['notificaciones_no_leidas'] = 0
            context['promedio_calificacion'] = 0
            
    except Exception:
        context = {
            'notificaciones_no_leidas': 0,
            'promedio_calificacion': 0
        }
    
    return context
