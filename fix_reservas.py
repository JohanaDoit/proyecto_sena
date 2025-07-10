#!/usr/bin/env python
"""
Script para limpiar datos inconsistentes en reservas.
Ejecutar con: python manage.py shell < fix_reservas.py
"""

from doit_app.models import Reserva, Estado

print("🔧 Iniciando limpieza de datos inconsistentes en reservas...")

# Buscar reservas que están marcadas como finalizadas pero sin experto asignado
reservas_inconsistentes = Reserva.objects.filter(
    servicio_finalizado=True,
    experto_asignado__isnull=True
)

print(f"📊 Encontradas {reservas_inconsistentes.count()} reservas con datos inconsistentes")

# Obtener el estado "Cancelado"
try:
    estado_cancelado = Estado.objects.get(Nombre='Cancelado')
except Estado.DoesNotExist:
    print("❌ Error: No se encontró el estado 'Cancelado' en la base de datos")
    exit(1)

# Corregir cada reserva inconsistente
for reserva in reservas_inconsistentes:
    print(f"🔧 Corrigiendo reserva {reserva.id}:")
    print(f"   - Servicio: {reserva.idServicios.NombreServicio}")
    print(f"   - Estado anterior: {reserva.idEstado.Nombre}")
    print(f"   - servicio_finalizado: {reserva.servicio_finalizado} → False")
    
    # Si la reserva está en estado "Cancelado", no debería estar marcada como finalizada
    if reserva.idEstado.Nombre == 'Cancelado':
        reserva.servicio_finalizado = False
        reserva.servicio_iniciado = False
        reserva.save()
        print(f"   ✅ Corregida: Estado=Cancelado, servicio_finalizado=False")
    else:
        # Si no está cancelada, investigar más
        print(f"   ⚠️  Estado actual: {reserva.idEstado.Nombre} - Requiere revisión manual")

print("\n✅ Limpieza completada!")
print("📋 Resumen:")
print(f"   - Reservas procesadas: {reservas_inconsistentes.count()}")
print("   - Las reservas canceladas ya no aparecerán como 'Finalizadas'")
print("   - Solo las reservas realmente finalizadas por un experto mostrarán estado 'Finalizado'")
