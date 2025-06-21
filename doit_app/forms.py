from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError # Importar para validaciones personalizadas

# Importa todos los modelos necesarios
# Asegúrate de que CustomUser es tu modelo de usuario personalizado que extiende AbstractUser o AbstractBaseUser
from .models import CustomUser, Genero, TipoDoc, Pais, Departamento, Ciudad, Servicios, Estado, Metodo, Reserva

# --- REGISTRO FORM ---
class RegistroForm(UserCreationForm):
    # NOTA: NO es necesario definir 'password' o 'password2' aquí,
    # UserCreationForm los provee automáticamente con sus validaciones.

    # Asegúrate de que 'email' sea requerido y único si lo usas como campo principal
    email = forms.EmailField(
        required=True,
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    # Campos adicionales del usuario (comunes a clientes y expertos)
    genero = forms.ModelChoiceField(
        queryset=Genero.objects.all().order_by('Nombre'),
        empty_label="Selecciona tu género",
        required=False, # Puede ser True si es obligatorio
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
        required=False, # Puede ser True si es obligatorio
        label="Nacionalidad",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    numDoc = forms.CharField(
        max_length=100, 
        required=False, # Puede ser True si es obligatorio
        label="Número de Documento", 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    telefono = forms.CharField(
        max_length=20, # Ajustado al max_length del modelo
        required=False, # Puede ser True si es obligatorio
        label="Teléfono", 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    fechaNacimiento = forms.DateField(
        required=False, # Puede ser True si es obligatorio
        label="Fecha de Nacimiento", 
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    tipo_documento = forms.ModelChoiceField(
        queryset=TipoDoc.objects.all().order_by('Nombre'),
        empty_label="Selecciona tipo de documento",
        required=False, # Puede ser True si es obligatorio
        label="Tipo de Documento",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # --- CAMPOS ESPECÍFICOS PARA EXPERTOS ---
    evidenciaTrabajo = forms.ImageField( 
        required=False, 
        label="Evidencia de Trabajo (Imagen)",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    experienciaTrabajo = forms.CharField(
        required=False, 
        label="Experiencia de Trabajo", 
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    hojaVida = forms.CharField( # Link a CV
        max_length=300, 
        required=False, 
        label="Link Hoja de Vida (URL)", 
        widget=forms.URLInput(attrs={'class': 'form-control'}) 
    )
    hojaVida_file = forms.FileField( # Archivo de CV
        required=False, 
        label="Subir Hoja de Vida (PDF, DOCX, etc.)", 
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    foto_perfil = forms.ImageField( 
        required=False, 
        label="Foto de Perfil", 
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    especialidad = forms.CharField(
        max_length=100,
        required=False, 
        label="Especialidad (ej. Electricista, Plomero)",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        # 'email' está aquí para que ModelForm lo incluya, aunque ya lo definas explícitamente.
        # UserCreationForm.Meta.fields ya incluye 'username', 'password', 'password2'.
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
            'experienciaTrabajo',
            'evidenciaTrabajo',
            'hojaVida', 
            'hojaVida_file', 
            'foto_perfil',
            'especialidad',
            # NO incluyas 'is_active' ni 'approval_status' aquí. 
            # Esos campos deben ser manejados por el modelo y la lógica de aprobación.
        )
        labels = {
            'username': 'Nombre de Usuario',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo Electrónico',
            'password': 'Contraseña', 
            'password2': 'Confirmación de Contraseña',
            'tipo_usuario': 'Tipo de Usuario',
            'evidenciaTrabajo': 'Evidencia de Trabajo (Imagen)',
            'hojaVida': 'Link Hoja de Vida (URL)',
            'hojaVida_file': 'Archivo de Hoja de Vida',
            'foto_perfil': 'Foto de Perfil',
            'especialidad': 'Especialidad (Solo para Expertos)',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            # 'email': forms.EmailInput(attrs={'class': 'form-control'}), # Ya definido explícitamente
            # Los widgets para 'password' y 'password2' son manejados por UserCreationForm
        }

    def clean(self):
        cleaned_data = super().clean()
        tipo_usuario = cleaned_data.get('tipo_usuario')

        if tipo_usuario == 'experto':
            # Hacemos los campos de experto requeridos condicionalmente
            if not cleaned_data.get('evidenciaTrabajo'):
                self.add_error('evidenciaTrabajo', 'Este campo es obligatorio para expertos.')
            if not cleaned_data.get('experienciaTrabajo'):
                self.add_error('experienciaTrabajo', 'Este campo es obligatorio para expertos.')
            
            # Validación para hojaVida (uno de los dos debe estar)
            if not cleaned_data.get('hojaVida') and not cleaned_data.get('hojaVida_file'):
                # Error de campo no específico para 'hojaVida' y 'hojaVida_file'
                # Puedes elegir dónde mostrar el error en tu template.
                self.add_error('hojaVida', 'Debe proporcionar un link o subir un archivo de Hoja de Vida.')
                self.add_error('hojaVida_file', 'Debe proporcionar un link o subir un archivo de Hoja de Vida.')
            
            if not cleaned_data.get('foto_perfil'):
                self.add_error('foto_perfil', 'Este campo es obligatorio para expertos.')
            
            if not cleaned_data.get('especialidad'):
                self.add_error('especialidad', 'Este campo es obligatorio para expertos.')

        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data['email']
        # Verifica si el correo ya existe en cualquier otro usuario
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Este correo electrónico ya está registrado.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Asignamos los campos adicionales del CustomUser
        user.genero = self.cleaned_data.get('genero')
        user.tipo_usuario = self.cleaned_data.get('tipo_usuario')
        user.nacionalidad = self.cleaned_data.get('nacionalidad')
        user.numDoc = self.cleaned_data.get('numDoc')
        user.telefono = self.cleaned_data.get('telefono')
        user.fechaNacimiento = self.cleaned_data.get('fechaNacimiento')
        user.tipo_documento = self.cleaned_data.get('tipo_documento')

        # Asigna los campos de experto solo si el tipo de usuario es experto.
        # Es crucial que estos campos se limpien si el usuario cambia de 'experto' a 'cliente'
        # Esto sucede en PerfilUsuarioForm. Aquí en RegistroForm, simplemente los asignamos.
        if user.tipo_usuario == 'experto':
            user.experienciaTrabajo = self.cleaned_data.get('experienciaTrabajo')
            user.evidenciaTrabajo = self.cleaned_data.get('evidenciaTrabajo')
            user.hojaVida = self.cleaned_data.get('hojaVida')
            user.hojaVida_file = self.cleaned_data.get('hojaVida_file')
            user.foto_perfil = self.cleaned_data.get('foto_perfil')
            user.especialidad = self.cleaned_data.get('especialidad')
        else:
            # Asegúrate de que estos campos estén vacíos/nulos si se registra como cliente
            user.experienciaTrabajo = None
            user.evidenciaTrabajo = None
            user.hojaVida = None
            user.hojaVida_file = None
            user.foto_perfil = None
            user.especialidad = None
        
        # ¡IMPORTANTE! No sobrescribas `is_active` o `approval_status` aquí.
        # Sus valores por defecto en el modelo (is_active=False, approval_status='PENDING')
        # son correctos para el flujo de aprobación.

        if commit:
            user.save()
        return user


# --- PERFIL USUARIO FORM (para edición de perfil) ---
class PerfilUsuarioForm(UserChangeForm): 
    # El campo 'tipo_usuario' es mejor que no sea editable directamente
    # si se decide que un usuario no puede cambiar su rol fácilmente.
    # Por ahora, se dejará readonly.
    
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
    
    # Campos específicos de experto para el PerfilUsuarioForm
    hojaVida = forms.CharField( 
        max_length=300, 
        required=False, 
        label="Link Hoja de Vida (URL)", 
        widget=forms.URLInput(attrs={'class': 'form-control'}) 
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
    evidenciaTrabajo = forms.ImageField( 
        required=False, 
        label="Evidencia de Trabajo (Imagen)", 
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    experienciaTrabajo = forms.CharField( 
        required=False, 
        label="Experiencia de Trabajo", 
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    especialidad = forms.CharField( 
        max_length=100,
        required=False,
        label="Especialidad",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CustomUser
        # UserChangeForm incluye 'password' en sus fields por defecto como un enlace a la página de cambio de contraseña.
        # No incluyas 'password' o 'password2' como campos de entrada directa aquí para edición.
        # Usa campos específicos para cambio de contraseña si es necesario.
        fields = (
            'username', 'first_name', 'last_name', 'email',
            'genero', 'tipo_usuario', 'nacionalidad', 'numDoc', 'telefono',
            'fechaNacimiento', 'experienciaTrabajo', 'evidenciaTrabajo', 'hojaVida',
            'hojaVida_file', 'tipo_documento', 'foto_perfil', 'especialidad'
        )
        labels = {
            'username': 'Nombre de Usuario',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo Electrónico',
            'evidenciaTrabajo': 'Evidencia de Trabajo (Imagen)',
            'hojaVida': 'Link Hoja de Vida (URL)',
            'hojaVida_file': 'Archivo de Hoja de Vida',
            'especialidad': 'Especialidad',
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
            'experienciaTrabajo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'hojaVida': forms.URLInput(attrs={'class': 'form-control'}),
            'especialidad': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # El campo tipo_usuario debe ser inmutable o manejado con cuidado en PerfilUsuarioForm.
        if self.instance and self.instance.pk:
            # Hacer el campo de solo lectura (el valor se enviará con el formulario)
            self.fields['tipo_usuario'].widget.attrs['readonly'] = True
            # Alternativa: si no quieres que el campo se envíe, usa 'disabled'
            # self.fields['tipo_usuario'].widget.attrs['disabled'] = True

        # Ocultar campos de experto si el usuario es cliente
        if self.instance and self.instance.tipo_usuario == 'cliente':
            # Si el usuario es cliente, ocultamos y hacemos que los campos no sean requeridos.
            for field_name in ['experienciaTrabajo', 'evidenciaTrabajo', 'hojaVida', 'hojaVida_file', 'especialidad', 'foto_perfil']:
                if field_name in self.fields: # Asegúrate de que el campo existe
                    self.fields[field_name].required = False
                    self.fields[field_name].widget = forms.HiddenInput()
        
        # Aplicar la clase 'form-control' a la mayoría de los campos si no la tienen ya
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

    # Sobreescribe clean_email para PerfilUsuarioForm para permitir que el usuario mantenga su propio email
    def clean_email(self):
        email = self.cleaned_data['email']
        # Si el email ya existe en otro usuario (excluyendo el usuario que se está editando)
        if CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Este correo electrónico ya está en uso por otro usuario.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Obtener el tipo de usuario original antes de cualquier cambio en el formulario
        original_user = None
        if user.pk: # Si el usuario ya existe en la base de datos
            original_user = CustomUser.objects.get(pk=user.pk)
        
        # Si el tipo de usuario cambia de experto a cliente (o ya era cliente y se limpia en caso de reenvío),
        # limpia los campos de experto.
        # Esto es crucial para no mantener datos de experto en un cliente.
        # IMPORTANTE: self.cleaned_data.get('tipo_usuario') te da el valor que EL USUARIO INTENTA ENVIAR.
        # Si el campo 'tipo_usuario' es readonly o disabled, este valor será el original del usuario.
        if original_user and original_user.tipo_usuario == 'experto' and self.cleaned_data.get('tipo_usuario') == 'cliente':
            # Limpia los campos de experto al cambiar de tipo
            user.evidenciaTrabajo = None 
            user.experienciaTrabajo = ""
            user.hojaVida = ""
            user.hojaVida_file = None # Los FileFields se limpian a None
            user.foto_perfil = None
            user.especialidad = "" 

            # Opcional: Borra los archivos físicos asociados si cambian a None
            # Asegúrate de importar `default_storage` si lo usas
            # from django.core.files.storage import default_storage
            # if original_user.evidenciaTrabajo and default_storage.exists(original_user.evidenciaTrabajo.name):
            #     default_storage.delete(original_user.evidenciaTrabajo.name)
            # if original_user.hojaVida_file and default_storage.exists(original_user.hojaVida_file.name):
            #     default_storage.delete(original_user.hojaVida_file.name)
            # if original_user.foto_perfil and default_storage.exists(original_user.foto_perfil.name):
            #     default_storage.delete(original_user.foto_perfil.name)

        if commit:
            user.save()
        return user


# --- RESERVA FORM ---
class ReservaForm(forms.ModelForm):
    # Campos ModelChoiceField con sus querysets y empty_label
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
    idEstado = forms.ModelChoiceField(
        queryset=Estado.objects.all().order_by('Nombre'),
        empty_label="Selecciona el estado de la reserva",
        required=True,
        label="Estado de la Reserva",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Campos de Fecha y Hora con sus widgets
    Fecha = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        input_formats=['%Y-%m-%d'],
        label='Fecha del Servicio'
    )
    Hora = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        input_formats=['%H:%M'],
        label='Hora del Servicio'
    )
    
    pago_ofrecido = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        label="Pago Ofrecido por el Cliente (ej. 50000.00 CLP)", 
        help_text="Monto que el cliente está dispuesto a pagar por el servicio.",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
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
            'idEstado',
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
            'idEstado': 'Estado de la Reserva'
        }
        widgets = {
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'detallesAdicionales': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Aplicar form-control a todos los campos por defecto si no lo tienen
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (
                forms.widgets.DateInput, 
                forms.widgets.TimeInput, 
                forms.widgets.Textarea, 
                forms.widgets.ClearableFileInput, 
                forms.widgets.Select,
                forms.widgets.CheckboxInput,
                forms.widgets.RadioSelect,
                forms.widgets.NumberInput, 
                forms.widgets.URLInput,
            )) and 'class' not in field.widget.attrs:
                field.widget.attrs.update({'class': 'form-control'})