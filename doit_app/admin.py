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

# Registra CustomUser (tu modelo de usuario personalizado)
@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    # fieldsets y add_fieldsets para organizar los campos en el formulario de edición/creación del admin
    fieldsets = BaseUserAdmin.fieldsets + (
        (('Información Adicional', {'fields': (
            'genero',
            'tipo_usuario',
            'nacionalidad',
            'numDoc',
            'telefono',
            'fechaNacimiento',
            'evidenciaTrabajo',
            'experienciaTrabajo',
            'hojaVida',
            'tipo_documento',
            'foto_perfil'
        )}),)
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (('Información Adicional', {'fields': (
            'genero',
            'tipo_usuario',
            'nacionalidad',
            'numDoc',
            'telefono',
            'fechaNacimiento',
            'evidenciaTrabajo',
            'experienciaTrabajo',
            'hojaVida',
            'tipo_documento',
            'foto_perfil'
        )}),)
    )

    # list_display para las columnas que se muestran en la lista de usuarios
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'tipo_usuario',
        'genero' # Muestra el género directamente en la lista
    )
    # search_fields para la barra de búsqueda
    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
        'numDoc'
    )
    # list_filter para los filtros laterales
    list_filter = (
        'is_staff',
        'is_superuser',
        'is_active',
        'groups', # Si usas grupos de Django
        'tipo_usuario',
        'genero' # Permite filtrar por género
    )
    # ordering para el orden por defecto
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
    list_display = ('puntuacion', 'Comentario', 'Fecha', 'idUsuario', 'idServicios')
    list_filter = ('puntuacion', 'Fecha', 'idServicios', 'idUsuario')
    search_fields = ('Comentario', 'idUsuario__username', 'idServicios__NombreServicio')

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('Fecha', 'Hora', 'direccion', 'idUsuario', 'idServicios', 'metodoDePago', 'ciudad')
    list_filter = ('Fecha', 'metodoDePago', 'idServicios', 'ciudad', 'pais')
    search_fields = (
        'direccion',
        'descripcion',
        'idUsuario__username',
        'idServicios__NombreServicio',
        'ciudad__Nombre',
        'pais__Nombre'
    )
    # Si añades un campo de estado para Reserva, agrégalo a list_display y list_filter


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