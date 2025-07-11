# Generated by Django 5.1.6 on 2025-07-08 01:45

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Categorias',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Nombre', models.CharField(max_length=50, unique=True, verbose_name='Nombre de la categoría')),
            ],
            options={
                'verbose_name': 'Categoría',
                'verbose_name_plural': 'Categorías',
                'db_table': 'Categorias',
            },
        ),
        migrations.CreateModel(
            name='Departamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Nombre', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Departamento',
                'verbose_name_plural': 'Departamentos',
            },
        ),
        migrations.CreateModel(
            name='Estado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Nombre', models.CharField(max_length=50, unique=True, verbose_name='Nombre del estado')),
            ],
            options={
                'verbose_name': 'Estado',
                'verbose_name_plural': 'Estados',
                'db_table': 'Estado',
            },
        ),
        migrations.CreateModel(
            name='Genero',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Nombre', models.CharField(max_length=50, unique=True, verbose_name='Nombre del Género')),
            ],
            options={
                'verbose_name': 'Género',
                'verbose_name_plural': 'Géneros',
                'ordering': ['Nombre'],
            },
        ),
        migrations.CreateModel(
            name='Metodo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Nombre', models.CharField(max_length=100, unique=True, verbose_name='Nombre del método de pago')),
            ],
            options={
                'verbose_name': 'Método de Pago',
                'verbose_name_plural': 'Métodos de Pago',
                'db_table': 'Metodo',
            },
        ),
        migrations.CreateModel(
            name='Pais',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Nombre', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'verbose_name': 'País',
                'verbose_name_plural': 'Países',
            },
        ),
        migrations.CreateModel(
            name='TipoDoc',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Nombre', models.CharField(max_length=50, unique=True, verbose_name='Nombre del tipo de documento')),
            ],
            options={
                'verbose_name': 'Tipo de Documento',
                'verbose_name_plural': 'Tipos de Documento',
                'db_table': 'TipoDoc',
            },
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('tipo_usuario', models.CharField(choices=[('cliente', 'Cliente'), ('experto', 'Experto')], default='cliente', max_length=20, verbose_name='Tipo de Usuario')),
                ('nacionalidad', models.CharField(blank=True, max_length=100, null=True, verbose_name='Nacionalidad')),
                ('numDoc', models.CharField(blank=True, max_length=100, null=True, unique=True, verbose_name='Número de Documento')),
                ('telefono', models.CharField(blank=True, max_length=20, null=True, verbose_name='Teléfono')),
                ('fechaNacimiento', models.DateField(blank=True, null=True, verbose_name='Fecha de Nacimiento')),
                ('foto_perfil', models.ImageField(blank=True, null=True, upload_to='perfil/', verbose_name='Foto de Perfil')),
                ('direccion', models.CharField(blank=True, max_length=255, null=True, verbose_name='Dirección de Residencia')),
                ('barrio', models.CharField(blank=True, max_length=100, null=True, verbose_name='Barrio')),
                ('documento_identidad_pdf', models.FileField(blank=True, null=True, upload_to='documentos_identidad/', verbose_name='Documento de Identidad (PDF)')),
                ('verificado', models.CharField(choices=[('pendiente', 'Pendiente'), ('aprobado', 'Aprobado'), ('rechazado', 'Rechazado')], default='pendiente', max_length=20, verbose_name='Estado de verificación del experto')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
                ('genero', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='doit_app.genero', verbose_name='Género')),
            ],
            options={
                'verbose_name': 'Usuario Personalizado',
                'verbose_name_plural': 'Usuarios Personalizados',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Ciudad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Nombre', models.CharField(max_length=100)),
                ('departamento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ciudades', to='doit_app.departamento')),
            ],
            options={
                'verbose_name': 'Ciudad',
                'verbose_name_plural': 'Ciudades',
            },
        ),
        migrations.CreateModel(
            name='Disponibilidad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('hora_inicio', models.TimeField()),
                ('hora_fin', models.TimeField()),
                ('experto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('idEstado', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='doit_app.estado')),
            ],
        ),
        migrations.CreateModel(
            name='Mensaje',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contenido', models.TextField()),
                ('fecha_envio', models.DateTimeField(auto_now_add=True)),
                ('leido', models.BooleanField(default=False)),
                ('emisor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mensajes_enviados', to=settings.AUTH_USER_MODEL)),
                ('receptor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mensajes_recibidos', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Notificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mensaje', models.CharField(max_length=255)),
                ('url', models.CharField(blank=True, max_length=255, null=True)),
                ('leida', models.BooleanField(default=False)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notificaciones', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Notificación',
                'verbose_name_plural': 'Notificaciones',
                'ordering': ['-fecha'],
            },
        ),
        migrations.CreateModel(
            name='Pagos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Monto', models.FloatField(verbose_name='Valor del servicio')),
                ('estado_pago_texto', models.CharField(max_length=40, verbose_name='Estado del pago (texto)')),
                ('Fecha', models.DateField(verbose_name='Fecha de pago')),
                ('idMetodo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doit_app.metodo', verbose_name='Método de pago')),
                ('idestado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pagos_estado', to='doit_app.estado', verbose_name='Estado del servicio')),
            ],
            options={
                'verbose_name': 'Pago',
                'verbose_name_plural': 'Pagos',
                'db_table': 'Pagos',
            },
        ),
        migrations.AddField(
            model_name='departamento',
            name='pais',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='departamentos', to='doit_app.pais'),
        ),
        migrations.CreateModel(
            name='Profesion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Nombre', models.CharField(max_length=50, verbose_name='Nombre de la profesión')),
                ('Descripcion', models.CharField(max_length=100, verbose_name='Descripción de la profesión')),
                ('idUsuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Usuario')),
            ],
            options={
                'verbose_name': 'Profesión',
                'verbose_name_plural': 'Profesiones',
                'db_table': 'Profesion',
            },
        ),
        migrations.CreateModel(
            name='Reserva',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Fecha', models.DateField(verbose_name='Fecha de Reserva')),
                ('Hora', models.TimeField(verbose_name='Hora de Reserva')),
                ('direccion', models.CharField(max_length=255, verbose_name='Dirección del Servicio')),
                ('descripcion', models.TextField(verbose_name='Descripción del Servicio')),
                ('detallesAdicionales', models.TextField(blank=True, null=True, verbose_name='Detalles Adicionales')),
                ('pago_ofrecido', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Pago Ofrecido por el Cliente')),
                ('motivo_cancelacion', models.TextField(blank=True, null=True, verbose_name='Motivo de Cancelación')),
                ('servicio_iniciado', models.BooleanField(default=False, verbose_name='Servicio Iniciado')),
                ('servicio_finalizado', models.BooleanField(default=False, verbose_name='Servicio Finalizado')),
                ('comentario_durante_servicio', models.TextField(blank=True, null=True, verbose_name='Comentario del Experto')),
                ('duracion_estimada', models.CharField(blank=True, max_length=50, null=True, verbose_name='duracion del servicio')),
                ('comentario_cliente', models.TextField(blank=True, null=True, verbose_name='Comentario del Cliente')),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('actualizado_en', models.DateTimeField(auto_now=True)),
                ('ciudad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doit_app.ciudad', verbose_name='Ciudad del Servicio')),
                ('experto_asignado', models.ForeignKey(blank=True, limit_choices_to={'tipo_usuario': 'experto'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reservas_aceptadas', to=settings.AUTH_USER_MODEL, verbose_name='Experto Asignado')),
                ('experto_solicitado', models.ForeignKey(blank=True, limit_choices_to={'tipo_usuario': 'experto'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reservas_solicitadas', to=settings.AUTH_USER_MODEL, verbose_name='Experto Solicitado')),
                ('idEstado', models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, to='doit_app.estado', verbose_name='Estado de la Reserva')),
                ('idUsuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservas_realizadas', to=settings.AUTH_USER_MODEL, verbose_name='Cliente que Reserva')),
                ('metodoDePago', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='doit_app.metodo', verbose_name='Método de Pago Preferido')),
                ('pais', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doit_app.pais', verbose_name='País del Servicio')),
            ],
            options={
                'verbose_name': 'Reserva',
                'verbose_name_plural': 'Reservas',
                'db_table': 'Reserva',
            },
        ),
        migrations.CreateModel(
            name='Calificaciones',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('cliente_a_experto', 'Cliente a Experto'), ('experto_a_cliente', 'Experto a Cliente')], max_length=20, verbose_name='Tipo de calificación')),
                ('puntuacion', models.PositiveSmallIntegerField(verbose_name='Puntuación (1-5)')),
                ('comentario', models.CharField(blank=True, max_length=150, null=True, verbose_name='Comentario del servicio')),
                ('fecha', models.DateField(auto_now_add=True, verbose_name='Fecha del comentario')),
                ('calificado_a', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='calificaciones_recibidas', to=settings.AUTH_USER_MODEL, verbose_name='Usuario calificado')),
                ('calificado_por', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='calificaciones_realizadas', to=settings.AUTH_USER_MODEL, verbose_name='Usuario que califica')),
                ('reserva', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doit_app.reserva', verbose_name='Reserva calificada')),
            ],
            options={
                'verbose_name': 'Calificación',
                'verbose_name_plural': 'Calificaciones',
                'db_table': 'Calificaciones',
            },
        ),
        migrations.CreateModel(
            name='Servicios',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('NombreServicio', models.CharField(max_length=50, verbose_name='Nombre del servicio')),
                ('idCategorias', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doit_app.categorias', verbose_name='Categoría del servicio')),
            ],
            options={
                'verbose_name': 'Servicio',
                'verbose_name_plural': 'Servicios',
                'db_table': 'Servicios',
            },
        ),
        migrations.AddField(
            model_name='reserva',
            name='idServicios',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doit_app.servicios', verbose_name='Servicio Solicitado'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='especialidad',
            field=models.ManyToManyField(blank=True, to='doit_app.servicios', verbose_name='Servicios que ofrece el experto'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='tipo_documento',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='doit_app.tipodoc', verbose_name='Tipo de Documento'),
        ),
    ]
