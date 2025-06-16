from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Modelo Genero
class Genero(models.Model):
    Nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre del Género")

    class Meta:
        ordering = ['Nombre']
        verbose_name = "Género"
        verbose_name_plural = "Géneros"
        app_label = "doit_app"

    def __str__(self): # ¡CORREGIDO!
        return self.Nombre

# Modelo CustomUser
class CustomUser(AbstractUser):
    tipo_usuario_choices = [
        ('cliente', 'Cliente'),
        ('experto', 'Experto'),
    ]
    genero = models.ForeignKey(Genero, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Género")
    tipo_usuario = models.CharField(max_length=20, choices=tipo_usuario_choices, default='usuario', verbose_name="Tipo de Usuario")
    nacionalidad = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nacionalidad")
    numDoc = models.CharField(max_length=100, unique=True, blank=True, null=True, verbose_name="Número de Documento")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    fechaNacimiento = models.DateField(blank=True, null=True, verbose_name="Fecha de Nacimiento")
    evidenciaTrabajo = models.CharField(max_length=200, blank=True, null=True, verbose_name="Evidencia de Trabajo")
    experienciaTrabajo = models.TextField(blank=True, null=True, verbose_name="Experiencia de Trabajo")
    hojaVida = models.CharField(max_length=300, blank=True, null=True, verbose_name="Hoja de Vida")
    
    foto_perfil = models.ImageField(upload_to='perfil/', null=True, blank=True, verbose_name="Foto de Perfil")
    
    tipo_documento = models.ForeignKey('TipoDoc', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tipo de Documento")

    evidenciaTrabajo = models.ImageField(
        upload_to='evidencia_trabajo/', # Directorio donde se guardarán las imágenes de evidencia
        blank=True,
        null=True,
        verbose_name="Evidencia de Trabajo (Imagen)"
    )

    hojaVida_file = models.FileField(
        upload_to='hojas_de_vida/', # Los archivos se guardarán en MEDIA_ROOT/hojas_de_vida/
        blank=True,
        null=True,
        verbose_name="Archivo de Hoja de Vida" # Nombre que se mostrará en el admin y formularios
    )
    class Meta:
        verbose_name = "Usuario Personalizado"
        verbose_name_plural = "Usuarios Personalizados"
        app_label = "doit_app"

    def _str_(self):
        return self.username

    def is_usuario_normal(self):
        return self.tipo_usuario == 'usuario'

    def is_experto(self):
        return self.tipo_usuario=='experto'

# TipoDoc
class TipoDoc(models.Model):
    Nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre del tipo de documento")

    class Meta:
        verbose_name = "Tipo de Documento"
        verbose_name_plural = "Tipos de Documento"
        db_table = "TipoDoc"
        app_label = "doit_app"

    def __str__(self): # ¡CORREGIDO!
        return self.Nombre

# Categorias
class Categorias(models.Model):
    Nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre de la categoría")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        db_table = "Categorias"
        app_label = "doit_app"

    def __str__(self): # ¡CORREGIDO!
        return self.Nombre

# Metodo
class Metodo(models.Model):
    Nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre del método de pago")

    class Meta:
        verbose_name = "Método de Pago"
        verbose_name_plural = "Métodos de Pago"
        db_table = "Metodo"
        app_label = "doit_app"

    def __str__(self): # ¡CORREGIDO!
        return self.Nombre

# Estado
class Estado(models.Model):
    Nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre del estado")

    class Meta:
        verbose_name = "Estado"
        verbose_name_plural = "Estados"
        db_table = "Estado"
        app_label = "doit_app"

    def __str__(self): # ¡CORREGIDO!
        return self.Nombre

# Pagos
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

    def __str__(self): # ¡CORREGIDO!
        return f"Pago #{self.id} - Monto: {self.Monto} - Estado: {self.estado_pago_texto}"

# Profesion
class Profesion(models.Model):
    Nombre = models.CharField(max_length=50, verbose_name="Nombre de la profesión")
    Descripcion = models.CharField(max_length=100, verbose_name="Descripción de la profesión")
    idUsuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Usuario")

    class Meta:
        verbose_name = "Profesión"
        verbose_name_plural = "Profesiones"
        db_table = "Profesion"
        app_label = "doit_app"

    def __str__(self): # ¡CORREGIDO!
        return self.Nombre

# Servicios
class Servicios(models.Model):
    NombreServicio = models.CharField(max_length=50, verbose_name="Nombre del servicio")
    idCategorias = models.ForeignKey(Categorias, on_delete=models.CASCADE, verbose_name="Categoría del servicio")

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"
        db_table = "Servicios"
        app_label = "doit_app"

    def __str__(self): # ¡CORREGIDO!
        return self.NombreServicio

# Calificaciones
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

    def __str__(self): # ¡CORREGIDO!
        return f"Calificación #{self.id} - Puntuación: {self.puntuacion}"

# Pais
class Pais(models.Model):
    Nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "País"
        verbose_name_plural = "Países"
        app_label = "doit_app"

    def __str__(self): # ¡CORREGIDO!
        return self.Nombre

# Departamento
class Departamento(models.Model):
    Nombre = models.CharField(max_length=100)
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE, related_name='departamentos')

    class Meta:
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"
        app_label = "doit_app"

    def __str__(self): # ¡CORREGIDO!
        return self.Nombre

# Ciudad
class Ciudad(models.Model):
    Nombre = models.CharField(max_length=100)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, related_name='ciudades')

    class Meta:
        verbose_name = "Ciudad"
        verbose_name_plural = "Ciudades"
        app_label = "doit_app"

    def __str__(self): # ¡CORREGIDO!
        return self.Nombre

# Reserva
class Reserva(models.Model):
    Fecha = models.DateField()
    Hora = models.TimeField()
    direccion = models.CharField(max_length=255)
    descripcion = models.CharField(max_length=255)
    detallesAdicionales = models.CharField(max_length=255)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.CASCADE)
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE, default=1) # El default=1 puede necesitar ajuste si los IDs de tus países no son fijos.
    metodoDePago = models.CharField(max_length=50, choices=[
        ('Efectivo', 'Efectivo'),
        ('Tarjeta', 'Tarjeta'),
        ('Transferencia', 'Transferencia'),
    ])
    idUsuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    idServicios = models.ForeignKey(Servicios, on_delete=models.CASCADE)
    # Considera añadir un campo de estado para la reserva, si aún no lo tienes, para gestionar su ciclo de vida
    # idEstado = models.ForeignKey(Estado, on_delete=models.SET_DEFAULT, default=1) # Por ejemplo, un estado inicial (si es que tienes un Estado con id=1 que signifique 'Pendiente' o similar)

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        app_label = "doit_app"

    def __str__(self): # ¡CORREGIDO!
        return f"Reserva #{self.id} - {self.Fecha} {self.Hora}"
    
