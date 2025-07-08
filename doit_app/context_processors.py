from .models import Notificacion

def notificaciones_context(request):
    """Context processor para agregar el contador de notificaciones a todos los templates"""
    if request.user.is_authenticated:
        notificaciones_no_leidas = Notificacion.objects.filter(usuario=request.user, leida=False).count()
        return {
            'notificaciones_no_leidas': notificaciones_no_leidas,
        }
    return {}
