# doit_app/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
# Modelo Genero (SIN CAMBIOS)
class Genero(models.Model):
    Nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre del Género")

    class Meta:
        ordering = ['Nombre']
        verbose_name = "Género"
        verbose_name_plural = "Géneros"
        app_label = "doit_app"

    def __str__(self):
        return self.Nombre

# Modelo TipoDoc (SIN CAMBIOS)
class TipoDoc(models.Model):
    Nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre del tipo de documento")

    class Meta:
        verbose_name = "Tipo de Documento"
        verbose_name_plural = "Tipos de Documento"
        db_table = "TipoDoc"
        app_label = "doit_app"

    def __str__(self):
        return self.Nombre

# Modelo CustomUser (AJUSTES MENORES)
class CustomUser(AbstractUser):
    tipo_usuario_choices = [
        ('cliente', 'Cliente'),
        ('experto', 'Experto'),
    ]
    genero = models.ForeignKey(Genero, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Género")
    
    tipo_usuario = models.CharField(max_length=20, choices=tipo_usuario_choices, default='cliente', verbose_name="Tipo de Usuario")
    
    nacionalidad = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nacionalidad")
    numDoc = models.CharField(max_length=100, unique=True, blank=True, null=True, verbose_name="Número de Documento")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    fechaNacimiento = models.DateField(blank=True, null=True, verbose_name="Fecha de Nacimiento")
    
    evidenciaTrabajo = models.ImageField(
        upload_to='evidencia_trabajo/', 
        blank=True,
        null=True,
        verbose_name="Evidencia de Trabajo (Imagen)"
    )
    
    experienciaTrabajo = models.TextField(blank=True, null=True, verbose_name="Experiencia de Trabajo")
    
    hojaVida = models.CharField(max_length=300, blank=True, null=True, verbose_name="Link Hoja de Vida (URL)")
    hojaVida_file = models.FileField(
        upload_to='hojas_de_vida/', 
        blank=True,
        null=True,
        verbose_name="Archivo de Hoja de Vida"
    )
    
    foto_perfil = models.ImageField(upload_to='perfil/', null=True, blank=True, verbose_name="Foto de Perfil")
    
    tipo_documento = models.ForeignKey(TipoDoc, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tipo de Documento")

    # Nuevo campo para la especialidad del experto (lo añadimos para el perfil del experto)
    especialidad = models.CharField(max_length=100, blank=True, null=True, verbose_name="Especialidad")

    categoria_especialidad = models.ForeignKey(
        'doit_app.Categorias',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Categoría de Especialidad"
    )


    class Meta:
        verbose_name = "Usuario Personalizado"
        verbose_name_plural = "Usuarios Personalizados"
        app_label = "doit_app"

    def __str__(self):
        return self.username

    def is_usuario_normal(self):
        return self.tipo_usuario == 'cliente'

    def is_experto(self):
        return self.tipo_usuario == 'experto'
    





# Categorias (SIN CAMBIOS)
class Categorias(models.Model):
    Nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre de la categoría")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        db_table = "Categorias"
        app_label = "doit_app"

    def __str__(self):
        return self.Nombre

class Servicios(models.Model):
    NombreServicio = models.CharField(max_length=50, verbose_name="Nombre del servicio")
    idCategorias = models.ForeignKey(Categorias, on_delete=models.CASCADE, verbose_name="Categoría del servicio")

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"
        db_table = "Servicios"
        app_label = "doit_app"

    def __str__(self):
        return self.NombreServicio





# Metodo (SIN CAMBIOS)
class Metodo(models.Model):
    Nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre del método de pago")

    class Meta:
        verbose_name = "Método de Pago"
        verbose_name_plural = "Métodos de Pago"
        db_table = "Metodo"
        app_label = "doit_app"

    def __str__(self):
        return self.Nombre

# Estado (SIN CAMBIOS)
class Estado(models.Model):
    Nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre del estado")

    class Meta:
        verbose_name = "Estado"
        verbose_name_plural = "Estados"
        db_table = "Estado"
        app_label = "doit_app"

    def __str__(self):
        return self.Nombre

# Pagos (SIN CAMBIOS)
class Pagos(models.Model):
    Monto = models.FloatField(verbose_name="Valor del servicio")
    estado_pago_texto = models.CharField(max_length=40, verbose_name="Estado del pago (texto)")
    Fecha = models.DateField(verbose_name="Fecha de pago")
    idMetodo = models.ForeignKey(Metodo, on_delete=models.CASCADE, verbose_name="Método de pago")
    idestado = models.ForeignKey(Estado, on_delete=models.CASCADE, related_name='pagos_estado', verbose_name="Estado del servicio")

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        db_table = "Pagos"
        app_label = "doit_app"

    def __str__(self):
        return f"Pago #{self.id} - Monto: {self.Monto} - Estado: {self.estado_pago_texto}"

# Profesion (SIN CAMBIOS)
class Profesion(models.Model):
    Nombre = models.CharField(max_length=50, verbose_name="Nombre de la profesión")
    Descripcion = models.CharField(max_length=100, verbose_name="Descripción de la profesión")
    idUsuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Usuario")

    class Meta:
        verbose_name = "Profesión"
        verbose_name_plural = "Profesiones"
        db_table = "Profesion"
        app_label = "doit_app"

    def __str__(self):
        return self.Nombre

# Servicios (SIN CAMBIOS)

# Calificaciones (SIN CAMBIOS)
class Calificaciones(models.Model):
    puntuacion = models.CharField(max_length=50, verbose_name="Puntuación del servicio")
    Comentario = models.CharField(max_length=150, verbose_name="Comentario del servicio")
    Fecha = models.DateField(verbose_name="Fecha del comentario")
    idUsuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='calificaciones_recibidas', verbose_name="Usuario que recibe la calificación")
    idServicios = models.ForeignKey(Servicios, on_delete=models.CASCADE, verbose_name="Servicio calificado")

    class Meta:
        verbose_name = "Calificación"
        verbose_name_plural = "Calificaciones"
        db_table = "Calificaciones"
        app_label = "doit_app"

    def __str__(self):
        return f"Calificación #{self.id} - Puntuación: {self.puntuacion}"

# Pais (SIN CAMBIOS)
class Pais(models.Model):
    Nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "País"
        verbose_name_plural = "Países"
        app_label = "doit_app"

    def __str__(self):
        return self.Nombre

# Departamento (SIN CAMBIOS)
class Departamento(models.Model):
    Nombre = models.CharField(max_length=100)
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE, related_name='departamentos')

    class Meta:
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"
        app_label = "doit_app"

    def __str__(self):
        return self.Nombre

# Ciudad (SIN CAMBIOS)
class Ciudad(models.Model):
    Nombre = models.CharField(max_length=100)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, related_name='ciudades')

    class Meta:
        verbose_name = "Ciudad"
        verbose_name_plural = "Ciudades"
        app_label = "doit_app"

    def __str__(self):
        return self.Nombre


# Modelo Reserva (MANTENIDO, PERO CON CAMPOS ADICIONALES PARA SOLICITUDES DE EXPERTO)
class Reserva(models.Model):
    # Campos existentes
    Fecha = models.DateField(verbose_name="Fecha de Reserva")
    Hora = models.TimeField(verbose_name="Hora de Reserva")
    direccion = models.CharField(max_length=255, verbose_name="Dirección del Servicio")
    descripcion = models.TextField(verbose_name="Descripción del Servicio")
    detallesAdicionales = models.TextField(blank=True, null=True, verbose_name="Detalles Adicionales")
    ciudad = models.ForeignKey(Ciudad, on_delete=models.CASCADE, verbose_name="Ciudad del Servicio")
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE, verbose_name="País del Servicio")

    metodoDePago = models.ForeignKey(
        Metodo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Método de Pago Preferido"
    )

    idUsuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reservas_realizadas',
        verbose_name="Cliente que Reserva"
    )
    idServicios = models.ForeignKey(Servicios, on_delete=models.CASCADE, verbose_name="Servicio Solicitado")

    idEstado = models.ForeignKey(
        Estado,
        on_delete=models.SET_DEFAULT,
        default=1,
        verbose_name="Estado de la Reserva"
    )

    # 🔴 NUEVO CAMPO agregado
    motivo_cancelacion = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Motivo de Cancelación"
    )

    # Experto asignado
    experto_asignado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reservas_aceptadas',
        limit_choices_to={'tipo_usuario': 'experto'},
        verbose_name="Experto Asignado"
    )

    pago_ofrecido = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Pago Ofrecido por el Cliente"
    )

    # Auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        db_table = "Reserva"
        app_label = "doit_app"

    def __str__(self):
        return f"Reserva #{self.id} de {self.idServicios.NombreServicio} por {self.idUsuario.username} - Estado: {self.idEstado.Nombre}"
