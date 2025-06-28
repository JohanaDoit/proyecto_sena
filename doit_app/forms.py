# doit_app/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

# Importa todos los modelos necesarios
# Asegúrate de que CustomUser es tu modelo de usuario personalizado que extiende AbstractUser o AbstractBaseUser
from .models import CustomUser, Genero, TipoDoc, Pais, Departamento, Ciudad, Servicios, Estado, Metodo, Reserva

# --- REGISTRO FORM ---
class RegistroForm(UserCreationForm):
    # NOTA: NO es necesario definir 'password' o 'password2' aquí,
    # UserCreationForm los provee automáticamente con sus validaciones.

    # Asegúrate de que 'email' sea requerido y único si lo usas como campo principal
    # UserCreationForm no hace el email requerido por defecto, pero tu lo has puesto.
    email = forms.EmailField(
        required=True,
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    # Campos adicionales del usuario (comunes a clientes y expertos)
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
    hojaVida_file = forms.FileField( # Archivo de CV
        required=False, 
        label="Subir Hoja de Vida (PDF, DOCX, etc.)", 
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    foto_perfil = forms.ImageField( 
        required=False, # Este campo DEBERÍA ser obligatorio para EXPERTOS si se quiere forzar una imagen de perfil
        label="Foto de Perfil", 
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    # Reemplaza tu campo actual por este:
    especialidad = forms.ModelChoiceField(
        queryset=Servicios.objects.all().order_by('NombreServicio'),
        required=False,  # o True si quieres forzarlo
        label="Especialidad (Servicio)",
        widget=forms.Select(attrs={'class': 'form-control'})
    )


    
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        # UserCreationForm.Meta.fields ya incluye 'username', 'password', 'password2'.
        # Asegúrate de que 'email' NO esté aquí si lo has definido explícitamente arriba,
        # para evitar duplicación. UserCreationForm.Meta.fields NO incluye 'email' por defecto.
        fields = UserCreationForm.Meta.fields + (
            'email', # Aseguramos que 'email' esté aquí, ya que no viene por defecto en UserCreationForm.Meta.fields
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
            'hojaVida_file', 
            'foto_perfil',
            'especialidad',
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
            'hojaVida_file': 'Archivo de Hoja de Vida',
            'foto_perfil': 'Foto de Perfil',
            'especialidad': 'Especialidad (Solo para Expertos)',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            # 'email': forms.EmailInput(attrs={'class': 'form-control'}), # Ya definido arriba
            # Los widgets para 'password' y 'password2' son manejados por UserCreationForm
        }

    def clean(self):
        cleaned_data = super().clean()
        tipo_usuario = cleaned_data.get('tipo_usuario')

        if tipo_usuario == 'experto':
            # Hacemos los campos de experto requeridos condicionalmente
            # NOTA: 'required=False' en la definición del campo es para el comportamiento por defecto,
            # aquí lo forzamos a ser requerido si el tipo de usuario es 'experto'.
            if not cleaned_data.get('evidenciaTrabajo'):
                self.add_error('evidenciaTrabajo', 'Este campo es obligatorio para expertos.')
            if not cleaned_data.get('experienciaTrabajo'):
                self.add_error('experienciaTrabajo', 'Este campo es obligatorio para expertos.')
            
            # Validación para hojaVida (uno de los dos debe estar)
            if not cleaned_data.get('hojaVida') and not cleaned_data.get('hojaVida_file'):
                # Añadimos un error no de campo (non_field_errors) o a un campo general si no quieres duplicar
                # self.add_error(None, 'Debe proporcionar un link o subir un archivo de Hoja de Vida para expertos.')
                self.add_error('hojaVida', 'Debe proporcionar un link o subir un archivo de Hoja de Vida.')
                self.add_error('hojaVida_file', 'Debe proporcionar un link o subir un archivo de Hoja de Vida.') # Este es un error duplicado, considera si quieres ambos.
            
            if not cleaned_data.get('foto_perfil'):
                self.add_error('foto_perfil', 'Este campo es obligatorio para expertos.')
            
            if not cleaned_data.get('especialidad'):
                self.add_error('especialidad', 'Este campo es obligatorio para expertos.')

        return cleaned_data

    # UserCreationForm ya tiene clean_username y clean_email, pero puedes sobreescribirlos si necesitas
    # lógica adicional o mensajes de error personalizados.
    # El clean_email de UserCreationForm por defecto no verifica unicidad si el campo no es `unique=True` en el modelo User.
    # Si CustomUser tiene email unique=True, Django ya lo validará. Si no, tu clean_email es útil.
    def clean_email(self):
        email = self.cleaned_data['email']
        # Verifica si el correo ya existe, excluyendo el usuario actual si es una actualización
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return email

    def save(self, commit=True):
        # UserCreationForm se encarga de crear el usuario base (username, password, email, first_name, last_name)
        # y de hashear la contraseña.
        user = super().save(commit=False)
        
        # Asignamos los campos adicionales del CustomUser
        user.genero = self.cleaned_data.get('genero')
        user.tipo_usuario = self.cleaned_data.get('tipo_usuario')
        user.nacionalidad = self.cleaned_data.get('nacionalidad')
        user.numDoc = self.cleaned_data.get('numDoc')
        user.telefono = self.cleaned_data.get('telefono')
        user.fechaNacimiento = self.cleaned_data.get('fechaNacimiento')
        user.tipo_documento = self.cleaned_data.get('tipo_documento')

        # Asigna los campos de experto solo si están presentes en cleaned_data
        # y si el tipo de usuario es experto.
        if user.tipo_usuario == 'experto':
            user.experienciaTrabajo = self.cleaned_data.get('experienciaTrabajo')
            user.evidenciaTrabajo = self.cleaned_data.get('evidenciaTrabajo')
            user.hojaVida = self.cleaned_data.get('hojaVida')
            user.hojaVida_file = self.cleaned_data.get('hojaVida_file')
            user.foto_perfil = self.cleaned_data.get('foto_perfil')
            user.especialidad = self.cleaned_data.get('especialidad').NombreServicio if self.cleaned_data.get('especialidad') else None


        else:
            # Si no es experto, asegúrate de que estos campos estén vacíos/nulos
            user.experienciaTrabajo = None
            user.evidenciaTrabajo = None
            user.hojaVida = None
            user.hojaVida_file = None
            user.foto_perfil = None
            user.especialidad = None

        if commit:
            user.save()
        return user


# --- PERFIL USUARIO FORM (para edición de perfil) ---
# Esta clase es para editar un usuario existente, no para crear uno nuevo.
class PerfilUsuarioForm(UserChangeForm): 
    # El campo 'tipo_usuario' es mejor que no sea editable en este formulario
    # si se decide que un usuario no puede cambiar su rol fácilmente.
    # Si se necesita cambiar, se requeriría una lógica de negocio más compleja.
    # Por ahora, se dejará readonly o se podría incluso excluir si el rol es fijo.
    
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
        # Si la instancia ya existe (es decir, estamos editando un usuario), haz el campo de sólo lectura.
        if self.instance and self.instance.pk:
            self.fields['tipo_usuario'].widget.attrs['readonly'] = True
            # self.fields['tipo_usuario'].widget.attrs['disabled'] = True # Esto impide que el valor se envíe

        # Ocultar campos de experto si el usuario es cliente
        # Asegúrate de que self.instance.tipo_usuario exista antes de acceder
        if self.instance and hasattr(self.instance, 'tipo_usuario') and self.instance.tipo_usuario == 'cliente':
            # Si el usuario es cliente, ocultamos y hacemos que los campos no sean requeridos.
            # No se necesitan los errores de "obligatorio" si el campo está oculto.
            self.fields['experienciaTrabajo'].required = False
            self.fields['evidenciaTrabajo'].required = False
            self.fields['hojaVida'].required = False
            self.fields['hojaVida_file'].required = False
            self.fields['especialidad'].required = False
            self.fields['foto_perfil'].required = False # Si la foto de perfil es solo para expertos
            
            self.fields['experienciaTrabajo'].widget = forms.HiddenInput()
            self.fields['evidenciaTrabajo'].widget = forms.HiddenInput()
            self.fields['hojaVida'].widget = forms.HiddenInput()
            self.fields['hojaVida_file'].widget = forms.HiddenInput()
            self.fields['especialidad'].widget = forms.HiddenInput()
            self.fields['foto_perfil'].widget = forms.HiddenInput()

        # Aplica la clase 'form-control' a la mayoría de los campos si no la tienen ya
        for field_name, field in self.fields.items():
            # Excluye tipos de widgets que ya tienen un manejo específico, o que no son de texto/select,
            # y los campos que ya tienen 'form-control' definido en el widget.
            if not isinstance(field.widget, (
                forms.widgets.DateInput, 
                forms.widgets.TimeInput, 
                forms.widgets.Textarea, 
                forms.widgets.ClearableFileInput, 
                forms.widgets.Select,
                forms.widgets.HiddenInput,
                forms.widgets.URLInput,
                forms.widgets.CheckboxInput, # Para campos booleanos si tuvieras
                forms.widgets.PasswordInput, # UserChangeForm los maneja de forma diferente
            )) and 'class' not in field.widget.attrs:
                field.widget.attrs.update({'class': 'form-control'})

    # Sobreescribe clean_email para PerfilUsuarioForm para permitir que el usuario mantenga su propio email
    def clean_email(self):
        email = self.cleaned_data['email']
        # Si el email ya existe en otro usuario (excluyendo el usuario que se está editando)
        if CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este correo electrónico ya está en uso por otro usuario.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        # Obtenemos el usuario original para comparar el tipo_usuario
        # Esto es importante si el tipo_usuario podría cambiarse (aunque lo hicimos readonly)
        # o si quieres limpiar los campos de experto al cambiar de experto a cliente.
        try:
            original_user = CustomUser.objects.get(pk=user.pk)
            original_tipo_usuario = original_user.tipo_usuario
        except CustomUser.DoesNotExist:
            original_tipo_usuario = None # O maneja el error como prefieras

        # Si el tipo de usuario cambia de experto a cliente (o ya era cliente), limpia los campos de experto
        # Esto es crucial para no mantener datos de experto en un cliente.
        if self.cleaned_data.get('tipo_usuario') == 'cliente' and original_tipo_usuario == 'experto':
            user.evidenciaTrabajo = None 
            user.experienciaTrabajo = ""
            user.hojaVida = ""
            user.especialidad = "" 
            
            # Borra el archivo físico si existe y el campo cambia a None
            if original_user.hojaVida_file:
                original_user.hojaVida_file.delete(save=False) 
            user.hojaVida_file = None 

            if original_user.foto_perfil and original_user.tipo_usuario == 'experto': # Asumiendo foto_perfil es solo para expertos
                original_user.foto_perfil.delete(save=False)
            user.foto_perfil = None
        
        if commit:
            user.save()
        return user


# --- RESERVA FORM ---
# Esta es la clase para el formulario de Reserva.
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
        }
        widgets = {
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'detallesAdicionales': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # No es estrictamente necesario redefinir los querysets aquí
        # si ya están definidos en los campos de arriba y no cambian dinámicamente.
        # self.fields['metodoDePago'].queryset = Metodo.objects.all().order_by('Nombre')
        # self.fields['pais'].queryset = Pais.objects.all().order_by('Nombre')
        # self.fields['ciudad'].queryset = Ciudad.objects.all().order_by('Nombre')
        # self.fields['idServicios'].queryset = Servicios.objects.all().order_by('NombreServicio')
        # self.fields['idEstado'].queryset = Estado.objects.all().order_by('Nombre')
        
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
                forms.widgets.NumberInput, # Para pago_ofrecido
                forms.widgets.URLInput,
            )) and 'class' not in field.widget.attrs:
                field.widget.attrs.update({'class': 'form-control'})