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
    Reserva,   # <--- Si quieres gestionar Reservas
    PQR        # <--- Nuevo modelo PQR
)
from django.utils.html import format_html

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
                'mostrar_foto_perfil',  # ✅ vista previa
                'documento_identidad_pdf',
                'mostrar_documento_identidad_pdf',  # ✅ vista previa
                'hoja_vida_file',
                'mostrar_hoja_vida_file',  # ✅ vista previa
                'especialidad',
                'verificado',
                'aprobado_cliente',
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
                'documento_identidad_pdf',
                'hoja_vida_file',
                'especialidad',
                'verificado',
                'aprobado_cliente',
            )
        }),
    )

    readonly_fields = (
        'mostrar_foto_perfil',
        'mostrar_documento_identidad_pdf',
        'mostrar_hoja_vida_file',
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
        'numDoc',
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

    # ✅ Vista previa: foto de perfil
    def mostrar_foto_perfil(self, obj):
        if obj.foto_perfil:
            return format_html('<img src="{}" width="100" height="100" style="object-fit:cover; border-radius:8px;" />', obj.foto_perfil.url)
        return "Sin foto"
    mostrar_foto_perfil.short_description = "Foto de Perfil"

    # ✅ Vista previa: documento de identidad
    def mostrar_documento_identidad_pdf(self, obj):
        if obj.documento_identidad_pdf:
            return format_html('<a href="{}" target="_blank">📄 Ver Documento</a>', obj.documento_identidad_pdf.url)
        return "No cargado"
    mostrar_documento_identidad_pdf.short_description = "Documento de Identidad"

    # ✅ Vista previa: hoja de vida
    def mostrar_hoja_vida_file(self, obj):
        if obj.hoja_vida_file:
            return format_html('<a href="{}" target="_blank">📄 Ver Hoja de Vida</a>', obj.hoja_vida_file.url)
        return "No cargada"
    mostrar_hoja_vida_file.short_description = "Hoja de Vida"



    

    


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


@admin.register(PQR)
class PQRAdmin(admin.ModelAdmin):
    list_display = ['id', 'tipo', 'asunto', 'usuario', 'fecha_creacion', 'respondido']
    list_filter = ['tipo', 'respondido', 'fecha_creacion']
    search_fields = ['asunto', 'descripcion', 'usuario__username', 'usuario__email']
    readonly_fields = ['usuario', 'tipo', 'asunto', 'descripcion', 'fecha_creacion']
    fieldsets = (
        ('Información del PQR', {
            'fields': ('usuario', 'tipo', 'asunto', 'descripcion', 'fecha_creacion')
        }),
        ('Gestión de Respuesta', {
            'fields': ('respondido', 'respuesta', 'fecha_respuesta'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if change and obj.respondido and not obj.fecha_respuesta:
            from django.utils import timezone
            obj.fecha_respuesta = timezone.now()
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('usuario')
    
    actions = ['marcar_como_respondido', 'marcar_como_pendiente']
    
    def marcar_como_respondido(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(respondido=True, fecha_respuesta=timezone.now())
        self.message_user(request, f'{updated} PQRs marcados como respondidos.')
    marcar_como_respondido.short_description = "Marcar PQRs seleccionados como respondidos"
    
    def marcar_como_pendiente(self, request, queryset):
        updated = queryset.update(respondido=False, fecha_respuesta=None)
        self.message_user(request, f'{updated} PQRs marcados como pendientes.')
    marcar_como_pendiente.short_description = "Marcar PQRs seleccionados como pendientes"