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
        # Incluye la categoría en la representación del servicio
        return f"{self.NombreServicio} ({self.idCategorias.Nombre})"
    




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

    foto_perfil = models.ImageField(upload_to='perfil/', null=True, blank=True, verbose_name="Foto de Perfil")
    tipo_documento = models.ForeignKey(TipoDoc, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tipo de Documento")

    especialidad = models.ManyToManyField(
        Servicios,
        blank=True,
        verbose_name="Servicios que ofrece el experto"
    )
    
    direccion = models.CharField(max_length=255, blank=True, null=True, verbose_name="Dirección de Residencia")
    barrio = models.CharField(max_length=100, blank=True, null=True, verbose_name="Barrio")
    documento_identidad_pdf = models.FileField(upload_to='documentos_identidad/', blank=True, null=True, verbose_name="Documento de Identidad (PDF)")

    # 👉 CAMPO AGREGADO: verificación de expertos
    verificado = models.CharField(
        max_length=20,
        choices=[('pendiente', 'Pendiente'), ('aprobado', 'Aprobado'), ('rechazado', 'Rechazado')],
        default='pendiente',
        verbose_name="Estado de verificación del experto"
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
    CALIFICADOR_CHOICES = [
        ("cliente_a_experto", "Cliente a Experto"),
        ("experto_a_cliente", "Experto a Cliente"),
    ]
    reserva = models.ForeignKey('Reserva', on_delete=models.CASCADE, verbose_name="Reserva calificada")
    calificado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='calificaciones_realizadas', verbose_name="Usuario que califica")
    calificado_a = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='calificaciones_recibidas', verbose_name="Usuario calificado")
    tipo = models.CharField(max_length=20, choices=CALIFICADOR_CHOICES, verbose_name="Tipo de calificación")
    puntuacion = models.PositiveSmallIntegerField(verbose_name="Puntuación (1-5)")
    comentario = models.CharField(max_length=150, verbose_name="Comentario del servicio", blank=True, null=True)
    fecha = models.DateField(auto_now_add=True, verbose_name="Fecha del comentario")

    class Meta:
        verbose_name = "Calificación"
        verbose_name_plural = "Calificaciones"
        db_table = "Calificaciones"
        app_label = "doit_app"

    def __str__(self):
        return f"Calificación #{self.id} - {self.calificado_por} a {self.calificado_a} - Puntuación: {self.puntuacion}"

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


    motivo_cancelacion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Motivo de Cancelación"
    )

    servicio_iniciado = models.BooleanField(default=False, verbose_name="Servicio Iniciado")
    servicio_finalizado = models.BooleanField(default=False, verbose_name="Servicio Finalizado")
    comentario_durante_servicio = models.TextField(blank=True, null=True, verbose_name="Comentario del Experto")
    duracion_estimada = models.CharField(max_length=50, null=True, blank=True, verbose_name="duracion del servicio")
    comentario_cliente = models.TextField(blank=True, null=True, verbose_name="Comentario del Cliente")

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






class Mensaje(models.Model):
    emisor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='mensajes_enviados', on_delete=models.CASCADE)
    receptor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='mensajes_recibidos', on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)  # NUEVO CAMPO

    def __str__(self):
        return f"{self.emisor} → {self.receptor}: {self.contenido[:30]}"

class Notificacion(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notificaciones')
    mensaje = models.CharField(max_length=255)
    url = models.CharField(max_length=255, blank=True, null=True)
    leida = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'

    def __str__(self):
        return f"Notificación para {self.usuario.username}: {self.mensaje[:30]}..."
    


class Disponibilidad(models.Model):
    experto = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    idEstado = models.ForeignKey(Estado, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.experto.username} - {self.fecha} de {self.hora_inicio} a {self.hora_fin} ({self.idEstado.Nombre})"
