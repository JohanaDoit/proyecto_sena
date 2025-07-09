from django.contrib import admin
# Importa TODOS tus modelos necesarios desde .models
from .models import (
    Genero,
    CustomUser,
    Servicios,
    Estado,
    Categorias,
    Pais,
    Departamento,
    Ciudad,
    TipoDoc,  # <--- Asegúrate de que TipoDoc está aquí
    Metodo,   # <--- Si quieres gestionar Métodos de Pago
    Pagos,    # <--- Si quieres gestionar Pagos
    Profesion, # <--- Si quieres gestionar Profesiones
    Calificaciones, # <--- Si quieres gestionar Calificaciones
    Reserva   # <--- Si quieres gestionar Reservas
)

# Importa UserAdmin del módulo de autenticación de Django para tu CustomUser
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# ---------------------------------------------------------------------
# Registros de Modelos Personalizados
# ---------------------------------------------------------------------

# Registra Genero
@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display = ('Nombre',)
    search_fields = ('Nombre',)
    # Opcional: Para añadir un filtro lateral
    # list_filter = () # Puedes añadir filtros si el modelo tuviera más campos para ello

# Registra TipoDoc (¡Este era el que faltaba en tu lista anterior!)
@admin.register(TipoDoc)
class TipoDocAdmin(admin.ModelAdmin):
    list_display = ('Nombre',)
    search_fields = ('Nombre',)





@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': (
                'genero',
                'tipo_usuario',
                'nacionalidad',
                'numDoc',
                'telefono',
                'fechaNacimiento',
                'tipo_documento',
                'foto_perfil',
                'especialidad',
                'verificado',
                'aprobado_cliente',  # 👈 Ahora es CharField (desplegable)
            )
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Información Adicional', {
            'fields': (
                'genero',
                'tipo_usuario',
                'nacionalidad',
                'numDoc',
                'telefono',
                'fechaNacimiento',
                'tipo_documento',
                'foto_perfil',
                'especialidad',
                'verificado',
                'aprobado_cliente',
            )
        }),
    )

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'tipo_usuario',
        'genero',
        'verificado',
        'aprobado_cliente',
    )

    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
        'numDoc'
    )

    list_filter = (
        'is_staff',
        'is_superuser',
        'is_active',
        'groups',
        'tipo_usuario',
        'genero',
        'verificado',
        'aprobado_cliente',
    )

    ordering = ('username',)

    

    


# ---------------------------------------------------------------------
# Registros de Otros Modelos de tu Aplicación
# ---------------------------------------------------------------------

@admin.register(Servicios)
class ServiciosAdmin(admin.ModelAdmin):
    list_display = ('NombreServicio', 'idCategorias')
    search_fields = ('NombreServicio',)
    list_filter = ('idCategorias',) # Permite filtrar por categoría

@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ('Nombre',)
    search_fields = ('Nombre',)

@admin.register(Categorias)
class CategoriasAdmin(admin.ModelAdmin):
    list_display = ('Nombre',)
    search_fields = ('Nombre',)

@admin.register(Metodo)
class MetodoAdmin(admin.ModelAdmin):
    list_display = ('Nombre',)
    search_fields = ('Nombre',)

@admin.register(Pagos)
class PagosAdmin(admin.ModelAdmin):
    list_display = ('Monto', 'estado_pago_texto', 'Fecha', 'idMetodo', 'idestado')
    list_filter = ('idMetodo', 'idestado', 'Fecha')
    search_fields = ('estado_pago_texto',)
    # Puedes añadir inlines si quieres ver detalles de reservas asociadas, etc.

@admin.register(Profesion)
class ProfesionAdmin(admin.ModelAdmin):
    list_display = ('Nombre', 'Descripcion', 'idUsuario')
    search_fields = ('Nombre', 'Descripcion', 'idUsuario__username') # Búsqueda por nombre de usuario
    list_filter = ('idUsuario',)

@admin.register(Calificaciones)
class CalificacionesAdmin(admin.ModelAdmin):
    list_display = ('puntuacion', 'comentario', 'fecha', 'calificado_por', 'calificado_a', 'reserva', 'tipo')
    list_filter = ('puntuacion', 'fecha', 'calificado_por', 'calificado_a', 'tipo')
    search_fields = ('comentario', 'calificado_por__username', 'calificado_a__username', 'reserva__id')

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = (
        'Fecha', 'Hora', 'direccion', 'idUsuario', 'idServicios',
        'metodoDePago', 'ciudad', 'idEstado', 'experto_asignado'
    )
    list_filter = ('Fecha', 'metodoDePago', 'idServicios', 'ciudad', 'pais', 'idEstado')
    search_fields = (
        'direccion',
        'descripcion',
        'idUsuario__username',
        'idServicios__NombreServicio',
        'ciudad__Nombre',
        'pais__Nombre',
        'idEstado__Nombre',
        'experto_asignado__username',
    )


@admin.register(Pais)
class PaisAdmin(admin.ModelAdmin):
    list_display = ['id', 'Nombre']
    search_fields = ['Nombre']

@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ['id', 'Nombre', 'pais']
    list_filter = ['pais']
    search_fields = ['Nombre', 'pais__Nombre'] # Permite buscar departamentos por el nombre de su país

@admin.register(Ciudad)
class CiudadAdmin(admin.ModelAdmin):
    list_display = ['id', 'Nombre', 'departamento']
    list_filter = ['departamento__pais', 'departamento'] # Filtra por país y luego por departamento
    search_fields = ['Nombre', 'departamento__Nombre', 'departamento__pais__Nombre']