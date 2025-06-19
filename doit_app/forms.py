from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

# Importa todos los modelos necesarios para los ChoiceFields y el Meta.model
from .models import CustomUser, Genero, TipoDoc, Pais, Departamento, Ciudad, Servicios, Estado, Metodo, Reserva

# --- REGISTRO FORM ---
class RegistroForm(UserCreationForm):
    # Campos adicionales del usuario, no específicos de experto/cliente
    genero = forms.ModelChoiceField(
        queryset=Genero.objects.all().order_by('Nombre'),
        empty_label="Selecciona tu género",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # --- CORRECCIÓN 1: 'initial' para tipo_usuario ---
    tipo_usuario_choices = [
        ('cliente', 'Cliente'),
        ('experto', 'Experto'),
    ]
    tipo_usuario = forms.ChoiceField(
        choices=tipo_usuario_choices,
        initial='cliente', # Cambiado a 'cliente' para coincidir con el modelo
        label="Tipo de Usuario",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_tipo_usuario'}) # Agregado ID para JS
    )
    
    nacionalidad = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    numDoc = forms.CharField(max_length=100, required=False, label="Número de Documento", widget=forms.TextInput(attrs={'class': 'form-control'}))
    telefono = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    fechaNacimiento = forms.DateField(required=False, label="Fecha de Nacimiento", widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    tipo_documento = forms.ModelChoiceField(
        queryset=TipoDoc.objects.all().order_by('Nombre'),
        empty_label="Selecciona tipo de documento",
        required=False,
        label="Tipo de Documento",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # --- CAMPOS ESPECÍFICOS PARA EXPERTOS ---
    # Todos deben ser required=False aquí; la validación se hace en clean()
    evidenciaTrabajo = forms.ImageField( # CORREGIDO: Ahora solo es ImageField
        required=False, 
        label="Evidencia de Trabajo (Imagen)",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    experienciaTrabajo = forms.CharField(
        required=False, 
        label="Experiencia de Trabajo", 
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    hojaVida = forms.CharField( # Agregado para el link de la hoja de vida
        max_length=300, 
        required=False, 
        label="Link Hoja de Vida (URL)", 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    hojaVida_file = forms.FileField( # Para el archivo de la hoja de vida
        required=False, 
        label="Subir Hoja de Vida (PDF, DOCX, etc.)", 
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    foto_perfil = forms.ImageField( # Para la foto de perfil
        required=False, 
        label="Foto de Perfil", 
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            'tipo_usuario', # Este campo DEBE ir primero para la lógica JS
            'username',
            'first_name',
            'last_name',
            'genero',
            'email',
            'nacionalidad',
            'fechaNacimiento',
            'tipo_documento',
            'numDoc',
            'telefono',
            # Campos de experto (incluidos aquí, su obligatoriedad es por clean())
            'experienciaTrabajo',
            'evidenciaTrabajo',
            'hojaVida',       # Incluye el link de la hoja de vida
            'hojaVida_file',  # Incluye el archivo de la hoja de vida
            'foto_perfil',
        )
        labels = {
            'username': 'Nombre de Usuario',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo Electrónico',
            'password2': 'Confirmación de Contraseña',
            'evidenciaTrabajo': 'Evidencia de Trabajo (Imagen)', # Asegura el label correcto
            'hojaVida': 'Link Hoja de Vida (URL)',
            'hojaVida_file': 'Archivo de Hoja de Vida',
        }

    def clean(self):
        cleaned_data = super().clean()
        tipo_usuario = cleaned_data.get('tipo_usuario')

        if tipo_usuario == 'experto':
            # Si el usuario es un experto, estos campos son obligatorios
            if not cleaned_data.get('evidenciaTrabajo'):
                self.add_error('evidenciaTrabajo', 'Este campo es obligatorio para expertos.')
            if not cleaned_data.get('experienciaTrabajo'):
                self.add_error('experienciaTrabajo', 'Este campo es obligatorio para expertos.')
            
            # Al menos uno de hojaVida (link) o hojaVida_file (archivo) debe estar presente
            if not cleaned_data.get('hojaVida') and not cleaned_data.get('hojaVida_file'):
                self.add_error('hojaVida', 'Debe proporcionar un link o subir un archivo de Hoja de Vida.')
                self.add_error('hojaVida_file', 'Debe proporcionar un link o subir un archivo de Hoja de Vida.')
            
            if not cleaned_data.get('foto_perfil'):
                self.add_error('foto_perfil', 'Este campo es obligatorio para expertos.')

        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data['username']
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya está en uso.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return email

    def save(self, commit=True):
        # Llama al save original de UserCreationForm, que ya maneja muchos campos
        user = super().save(commit=False)
        
        # Asigna los campos adicionales que no son manejados por UserCreationForm automáticamente
        user.genero = self.cleaned_data.get('genero')
        user.tipo_usuario = self.cleaned_data.get('tipo_usuario') # Este ya debería venir del form
        user.nacionalidad = self.cleaned_data.get('nacionalidad')
        user.numDoc = self.cleaned_data.get('numDoc')
        user.telefono = self.cleaned_data.get('telefono')
        user.fechaNacimiento = self.cleaned_data.get('fechaNacimiento')
        user.tipo_documento = self.cleaned_data.get('tipo_documento')

        # Asigna los campos específicos de experto si existen en cleaned_data
        # Django maneja FileField e ImageField si se pasan en request.FILES
        user.experienciaTrabajo = self.cleaned_data.get('experienciaTrabajo')
        user.evidenciaTrabajo = self.cleaned_data.get('evidenciaTrabajo')
        user.hojaVida = self.cleaned_data.get('hojaVida')
        user.hojaVida_file = self.cleaned_data.get('hojaVida_file')
        user.foto_perfil = self.cleaned_data.get('foto_perfil')

        if commit:
            user.save()
        return user


# --- PERFIL USUARIO FORM (para edición de perfil) ---
class PerfilUsuarioForm(UserChangeForm):
    genero = forms.ModelChoiceField(
        queryset=Genero.objects.all().order_by('Nombre'),
        empty_label="Selecciona tu género",
        required=False,
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
    hojaVida = forms.CharField( # Para el link de la hoja de vida
        max_length=300, 
        required=False, 
        label="Link Hoja de Vida (URL)", 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    hojaVida_file = forms.FileField( # Para el archivo de la hoja de vida
        required=False, 
        label="Subir Hoja de Vida (PDF, DOCX, etc.)", 
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    foto_perfil = forms.ImageField(
        required=False, 
        label="Foto de Perfil", 
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    evidenciaTrabajo = forms.ImageField( # CORREGIDO: Es ImageField
        required=False, 
        label="Evidencia de Trabajo (Imagen)", 
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    experienciaTrabajo = forms.CharField( # Es TextField en modelo, CharField en form para Textarea
        required=False, 
        label="Experiencia de Trabajo", 
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    class Meta:
        model = CustomUser
        fields = (
            'username', 'first_name', 'last_name', 'email',
            'genero', 'tipo_usuario', 'nacionalidad', 'numDoc', 'telefono',
            'fechaNacimiento', 'experienciaTrabajo', 'evidenciaTrabajo', 'hojaVida',
            'hojaVida_file', 'tipo_documento', 'foto_perfil',
        )
        labels = {
            'username': 'Nombre de Usuario',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo Electrónico',
            'evidenciaTrabajo': 'Evidencia de Trabajo (Imagen)',
            'hojaVida': 'Link Hoja de Vida (URL)',
            'hojaVida_file': 'Archivo de Hoja de Vida',
        }
        widgets = {
            'fechaNacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            # 'experienciaTrabajo' y 'evidenciaTrabajo' (ImageField), 'hojaVida' (CharField),
            # 'hojaVida_file' (FileField), 'foto_perfil' (ImageField)
            # ya tienen su widget definido en la declaración del campo.
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Deshabilitar el campo tipo_usuario si ya está establecido (para que no cambie en edición)
        # O podrías ocultarlo completamente si no quieres que sea visible
        if self.instance and self.instance.pk:
            self.fields['tipo_usuario'].widget.attrs['readonly'] = True
            # Si quieres que el usuario pueda cambiarlo (con advertencia), remueve la línea de arriba.
            # O podrías hacer self.fields['tipo_usuario'].disabled = True

        # Ocultar campos específicos de experto si el usuario es 'cliente'
        if self.instance and self.instance.tipo_usuario == 'cliente':
            # Hazlos HiddenInput para que se envíe el valor, pero no se muestre el campo
            self.fields['experienciaTrabajo'].widget = forms.HiddenInput()
            self.fields['evidenciaTrabajo'].widget = forms.HiddenInput()
            self.fields['hojaVida'].widget = forms.HiddenInput()
            self.fields['hojaVida_file'].widget = forms.HiddenInput()
            # La foto de perfil podría ser común a ambos, así que no la ocultamos por defecto aquí.
            # Si decides que foto_perfil es SOLO para expertos, la ocultarías aquí también.

        # Aplica 'form-control' a la mayoría de los campos si no tienen ya un widget específico
        for field_name, field in self.fields.items():
            # Excluye widgets que ya tienen una clase o que manejan su propio estilo (ej. FileInput)
            if not isinstance(field.widget, (
                forms.widgets.DateInput, 
                forms.widgets.Textarea, 
                forms.widgets.ClearableFileInput, # IMPORTANTE: Excluir para no sobrescribir su estilo
                forms.widgets.Select,
                forms.widgets.HiddenInput,
            )) and 'class' not in field.widget.attrs:
                field.widget.attrs.update({'class': 'form-control'})

        # Elimina el campo de contraseña ya que UserChangeForm incluye 'password' por defecto
        if 'password' in self.fields:
            del self.fields['password']

    def save(self, commit=True):
        user = super().save(commit=False)
        original_user = CustomUser.objects.get(pk=user.pk)

        # Lógica para manejar la limpieza/eliminación de campos si el tipo de usuario cambia
        # de experto a cliente (esto es raro que suceda en un PerfilUsuarioForm,
        # pero es una buena defensa)
        if original_user.tipo_usuario == 'experto' and user.tipo_usuario == 'cliente':
            # Limpiar campos de experto cuando se cambia a cliente
            user.evidenciaTrabajo = None # Establece el campo a None para que use la lógica de borrado
            user.experienciaTrabajo = ""
            user.hojaVida = ""
            
            if original_user.hojaVida_file:
                original_user.hojaVida_file.delete(save=False) # Borra el archivo físico
            user.hojaVida_file = None

            # Si quieres que la foto de perfil también se elimine/restablezca al pasar a 'cliente'
            # if original_user.foto_perfil and original_user.foto_perfil.url != original_user.foto_perfil.field.default:
            #     original_user.foto_perfil.delete(save=False)
            # user.foto_perfil = None # O establecer a None o a un valor por defecto si existe

        if commit:
            user.save()
        return user

# --- RESERVA FORM (sin cambios significativos para este contexto) ---
class ReservaForm(forms.ModelForm):
    metodoDePago = forms.ModelChoiceField(
        queryset=Metodo.objects.all().order_by('Nombre'),
        empty_label="Selecciona un método de pago",
        required=True,
        label="Método de Pago",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    pais = forms.ModelChoiceField(
        queryset=Pais.objects.all().order_by('Nombre'),
        empty_label="Selecciona un país",
        required=True,
        label="País",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    ciudad = forms.ModelChoiceField(
        queryset=Ciudad.objects.all().order_by('Nombre'),
        empty_label="Selecciona una ciudad",
        required=True,
        label="Ciudad",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    Fecha = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        input_formats=['%Y-%m-%d'],
        label='Fecha'
    )
    Hora = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        input_formats=['%H:%M'],
        label='Hora'
    )

    class Meta:
        model = Reserva
        fields = [
            'Fecha', 'Hora', 'direccion', 'descripcion',
            'detallesAdicionales', 'metodoDePago', 'pais', 'ciudad', 'idEstado' # Asegúrate de incluir 'idEstado'
        ]
        widgets = {
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'detallesAdicionales': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }