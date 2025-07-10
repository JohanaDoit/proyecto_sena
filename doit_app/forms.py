from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Genero, TipoDoc, Pais, Departamento, Ciudad, Servicios, Estado, Metodo, Reserva, Calificaciones, PQR, PQR
from datetime import datetime, timedelta, time, date
from .models import Disponibilidad
from django.conf import settings
from django.contrib.auth import get_user_model
class RegistroForm(UserCreationForm):
    acepta_terminos = forms.BooleanField(
        required=True,
        label="Acepto los ",
        error_messages={
            'required': 'Debes aceptar los términos y condiciones para continuar.'
        },
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    acepta_tratamiento_datos = forms.BooleanField(
        required=True,
        label="Acepto la ",
        error_messages={
            'required': 'Debes aceptar la política de tratamiento de datos para continuar.'
        },
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    email = forms.EmailField(
        required=True,
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    genero = forms.ModelChoiceField(
        queryset=Genero.objects.all().order_by('Nombre'),
        empty_label="Selecciona tu género",
        required=False,
        label="Género",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    tipo_usuario = forms.ChoiceField(
        choices=CustomUser.tipo_usuario_choices,
        initial='cliente',
        label="Tipo de Usuario",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_tipo_usuario'})
    )
    nacionalidad = forms.CharField(
        max_length=100,
        required=False,
        label="Nacionalidad",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    numDoc = forms.CharField(
        max_length=100,
        required=False,
        label="Número de Documento",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    telefono = forms.CharField(
        max_length=100,
        required=False,
        label="Teléfono",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    fechaNacimiento = forms.DateField(
        required=False,
        label="Fecha de Nacimiento",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    tipo_documento = forms.ModelChoiceField(
        queryset=TipoDoc.objects.all().order_by('Nombre'),
        empty_label="Selecciona tipo de documento",
        required=False,
        label="Tipo de Documento",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    hojaVida_file = forms.FileField(
        required=False,
        label="Subir Hoja de Vida (PDF, DOCX, etc.)",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    foto_perfil = forms.ImageField(
        required=False,
        label="Foto de Perfil",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    especialidad = forms.ModelMultipleChoiceField(
        queryset=Servicios.objects.select_related('idCategorias').order_by('NombreServicio'),
        required=False,
        label="Especialidades (máximo 3)",
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        help_text="Puedes seleccionar hasta 3 especialidades."
    )
    direccion = forms.CharField(
        max_length=255,
        required=False,
        label="Dirección de Residencia",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    barrio = forms.CharField(
        max_length=100,
        required=False,
        label="Barrio",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    documento_identidad_pdf = forms.FileField(
        required=False,
        label="Documento de Identidad (PDF)",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + (
            'email',
            'tipo_usuario',
            'first_name',
            'last_name',
            'genero',
            'nacionalidad',
            'fechaNacimiento',
            'tipo_documento',
            'numDoc',
            'telefono',
            'hojaVida_file',
            'foto_perfil',
            'especialidad',
            'direccion',
            'barrio',
            'documento_identidad_pdf',
        )
        labels = {
            'username': 'Nombre de Usuario',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo Electrónico',
            'password': 'Contraseña',
            'password2': 'Confirmación de Contraseña',
            'tipo_usuario': 'Tipo de Usuario',
            'hojaVida_file': 'Archivo de Hoja de Vida',
            'foto_perfil': 'Foto de Perfil',
            'especialidad': 'Especialidades (Solo para Expertos)',
            'direccion': 'Dirección de Residencia',
            'barrio': 'Barrio',
            'documento_identidad_pdf': 'Documento de Identidad (PDF)',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        tipo_usuario = cleaned_data.get('tipo_usuario')
        if tipo_usuario == 'experto':
            campos_requeridos = ['hojaVida_file', 'foto_perfil', 'especialidad', 'documento_identidad_pdf']
            for campo in campos_requeridos:
                if not cleaned_data.get(campo):
                    self.add_error(campo, 'Este campo es obligatorio para expertos.')
        return cleaned_data
    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return email
    def clean_especialidad(self):
        especialidades = self.cleaned_data.get('especialidad')
        tipo_usuario = self.cleaned_data.get('tipo_usuario')
        if tipo_usuario == 'experto':
            if not especialidades or len(especialidades) == 0:
                raise forms.ValidationError("Debes seleccionar al menos un servicio.")
            if len(especialidades) > 3:
                raise forms.ValidationError("Solo puedes seleccionar hasta 3 servicios.")
        return especialidades
    def save(self, commit=True):
        user = super().save(commit=False)
        for campo in [
            'genero', 'tipo_usuario', 'nacionalidad', 'numDoc', 'telefono',
            'fechaNacimiento', 'tipo_documento', 'direccion', 'barrio', 'documento_identidad_pdf'
        ]:
            setattr(user, campo, self.cleaned_data.get(campo))
        if commit:
            user.save()
        if user.tipo_usuario == 'experto':
            user.especialidad.set(self.cleaned_data.get('especialidad'))
        return user
class PerfilUsuarioForm(UserChangeForm):
    genero = forms.ModelChoiceField(
        queryset=Genero.objects.all().order_by('Nombre'),
        empty_label="Selecciona tu género",
        required=False,
        label="Género",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    tipo_documento = forms.ModelChoiceField(
        queryset=TipoDoc.objects.all().order_by('Nombre'),
        empty_label="Selecciona tipo de documento",
        required=False,
        label="Tipo de Documento",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    foto_perfil = forms.ImageField(
        required=False,
        label="Foto de Perfil",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    direccion = forms.CharField(
        max_length=255,
        required=False,
        label="Dirección de Residencia",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    barrio = forms.CharField(
        max_length=100,
        required=False,
        label="Barrio",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    class Meta:
        model = CustomUser
        fields = (
            'username', 'first_name', 'last_name', 'email',
            'genero', 'tipo_usuario', 'nacionalidad', 'numDoc', 'telefono',
            'fechaNacimiento', 'tipo_documento', 'foto_perfil',
            'direccion', 'barrio',
        )
        labels = {
            'username': 'Nombre de Usuario',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo Electrónico',
            'especialidad': 'Especialidad',
            'direccion': 'Dirección de Residencia',
            'barrio': 'Barrio',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'nacionalidad': forms.TextInput(attrs={'class': 'form-control'}),
            'numDoc': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'fechaNacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'barrio': forms.TextInput(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['tipo_usuario'].widget.attrs['readonly'] = True
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (
                forms.widgets.DateInput,
                forms.widgets.TimeInput,
                forms.widgets.Textarea,
                forms.widgets.ClearableFileInput,
                forms.widgets.Select,
                forms.widgets.HiddenInput,
                forms.widgets.URLInput,
                forms.widgets.CheckboxInput,
                forms.widgets.PasswordInput,
            )) and 'class' not in field.widget.attrs:
                field.widget.attrs.update({'class': 'form-control'})
    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este correo electrónico ya está en uso por otro usuario.")
        return email
    def save(self, commit=True):
        user = super().save(commit=False)
        try:
            original_user = CustomUser.objects.get(pk=user.pk)
            original_tipo_usuario = original_user.tipo_usuario
        except CustomUser.DoesNotExist:
            original_tipo_usuario = None
        if self.cleaned_data.get('tipo_usuario') == 'cliente' and original_tipo_usuario == 'experto':
            user.especialidad = ""
            if original_user.hojaVida_file:
                original_user.hojaVida_file.delete(save=False)
            user.hojaVida_file = None
            if original_user.foto_perfil and original_user.tipo_usuario == 'experto':
                original_user.foto_perfil.delete(save=False)
            user.foto_perfil = None
        if commit:
            user.save()
        return user
class ReservaForm(forms.ModelForm):
    metodoDePago = forms.ModelChoiceField(
        queryset=Metodo.objects.all().order_by('Nombre'),
        empty_label="Selecciona un método de pago",
        required=True,
        label="Método de Pago Preferido",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    pais = forms.ModelChoiceField(
        queryset=Pais.objects.all().order_by('Nombre'),
        empty_label="Selecciona un país",
        required=True,
        label="País del Servicio",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    ciudad = forms.ModelChoiceField(
        queryset=Ciudad.objects.all().order_by('Nombre'),
        empty_label="Selecciona una ciudad",
        required=True,
        label="Ciudad del Servicio",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    idServicios = forms.ModelChoiceField(
        queryset=Servicios.objects.all().order_by('NombreServicio'),
        empty_label="Selecciona el tipo de servicio",
        required=True,
        label="Tipo de Servicio Solicitado",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    Fecha = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        input_formats=['%Y-%m-%d'],
        label='Fecha del Servicio'
    )
    Hora = forms.ChoiceField(
        choices=[],
        label='Hora del Servicio',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    pago_ofrecido = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        label="Pago Ofrecido por el Cliente (ej. 50000.00 CLP)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    experto_solicitado = forms.ModelChoiceField(
        queryset=get_user_model().objects.filter(tipo_usuario='experto', is_active=True).order_by('username'),
        required=False,
        label="Solicitar un experto específico (opcional)",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class Meta:
        model = Reserva
        fields = [
            'Fecha',
            'Hora',
            'direccion',
            'descripcion',
            'detallesAdicionales',
            'metodoDePago',
            'pais',
            'ciudad',
            'idServicios',
            'pago_ofrecido',
            'experto_solicitado',
        ]
        labels = {
            'Fecha': 'Fecha Preferida del Servicio',
            'Hora': 'Hora Preferida del Servicio',
            'direccion': 'Dirección del Servicio',
            'descripcion': 'Describe lo que necesitas',
            'detallesAdicionales': 'Añade más detalles (opcional)',
            'metodoDePago': 'Método de Pago Preferido',
            'pais': 'País del Servicio',
            'ciudad': 'Ciudad del Servicio',
            'idServicios': 'Tipo de Servicio',
            'pago_ofrecido': 'Pago Ofrecido',
            'experto_solicitado': 'Experto Específico (opcional)',
        }
        widgets = {
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'detallesAdicionales': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    def __init__(self, *args, **kwargs):
        experto_id = kwargs.pop('experto_id', None)
        super().__init__(*args, **kwargs)
        opciones = []
        hora_actual = datetime.strptime("06:00", "%H:%M")
        fin = datetime.strptime("21:00", "%H:%M")
        while hora_actual <= fin:
            valor = hora_actual.strftime("%H:%M")
            etiqueta = hora_actual.strftime("%I:%M %p")
            opciones.append((valor, etiqueta))
            hora_actual += timedelta(minutes=30)
        self.fields['Hora'].choices = opciones
        if experto_id:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                experto = User.objects.get(id=experto_id, tipo_usuario='experto')
                servicios_experto = experto.especialidad.all()
                if servicios_experto.exists():
                    self.fields['idServicios'].queryset = servicios_experto.order_by('NombreServicio')
                    self.fields['idServicios'].empty_label = "Selecciona un servicio del experto"
                else:
                    self.fields['idServicios'].queryset = Servicios.objects.none()
                    self.fields['idServicios'].empty_label = "Este experto no tiene servicios registrados"
            except (User.DoesNotExist, ValueError):
                pass
class CalificacionForm(forms.ModelForm):
    class Meta:
        model = Calificaciones
        fields = ['puntuacion', 'comentario']
        widgets = {
            'puntuacion': forms.RadioSelect(choices=[(i, f'{i} estrella' if i == 1 else f'{i} estrellas') for i in range(1, 6)]),
            'comentario': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Comentario (opcional)'}),
        }
        labels = {
            'puntuacion': 'Calificación',
            'comentario': 'Comentario',
        }
class DisponibilidadForm(forms.ModelForm):
    HORA_CHOICES = []
    for hour in range(6, 21 + 1):
        for minute in [0, 30]:
            time_obj = time(hour, minute)
            time_str = time_obj.strftime('%H:%M')
            display_str = time_obj.strftime('%I:%M %p')
            HORA_CHOICES.append((time_str, display_str))
    hora_inicio = forms.ChoiceField(
        choices=HORA_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Hora de inicio'
    )
    hora_fin = forms.ChoiceField(
        choices=HORA_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Hora de fin'
    )
    class Meta:
        model = Disponibilidad
        fields = ['fecha', 'hora_inicio', 'hora_fin', 'idEstado']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'idEstado': forms.Select(attrs={'class': 'form-select'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')
        if hora_inicio and hora_fin:
            hora_inicio_obj = time.fromisoformat(hora_inicio)
            hora_fin_obj = time.fromisoformat(hora_fin)
            if hora_inicio_obj >= hora_fin_obj:
                raise forms.ValidationError("La hora de fin debe ser posterior a la hora de inicio.")
        return cleaned_data
class PQRForm(forms.ModelForm):
    class Meta:
        model = PQR
        fields = ['tipo', 'asunto', 'descripcion']
        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_tipo'
            }),
            'asunto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Escribe el asunto de tu PQR',
                'maxlength': '200'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe detalladamente tu petición, queja, reclamo o sugerencia...',
                'rows': 5
            })
        }
        labels = {
            'tipo': 'Tipo de PQR',
            'asunto': 'Asunto',
            'descripcion': 'Descripción detallada'
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': field.widget.attrs.get('class', '') + ' mb-3'})
    def clean_asunto(self):
        asunto = self.cleaned_data.get('asunto')
        if len(asunto.strip()) < 5:
            raise forms.ValidationError("El asunto debe tener al menos 5 caracteres.")
        return asunto.strip()
    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')
        if len(descripcion.strip()) < 20:
            raise forms.ValidationError("La descripción debe tener al menos 20 caracteres para poder ayudarte mejor.")
        return descripcion.strip()