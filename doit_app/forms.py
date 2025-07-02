# doit_app/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

# Importa todos los modelos necesarios
# Asegúrate de que CustomUser es tu modelo de usuario personalizado que extiende AbstractUser o AbstractBaseUser
from .models import CustomUser, Genero, TipoDoc, Pais, Departamento, Ciudad, Servicios, Estado, Metodo, Reserva, Calificaciones
from datetime import datetime, timedelta, time, date



class RegistroForm(UserCreationForm):
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

    evidenciaTrabajo = forms.FileField(
        required=False,
        label="Evidencia de Trabajo",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
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
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['especialidad'].label_from_instance = str
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
            'evidenciaTrabajo',
            'hojaVida_file',
            'foto_perfil',
            'especialidad',
            'direccion',
            'barrio',
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
            'especialidad': 'Especialidades (Solo para Expertos)',
            'direccion': 'Dirección de Residencia',
            'barrio': 'Barrio',
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
            campos_requeridos = [
                'evidenciaTrabajo', 'hojaVida_file',
                'foto_perfil', 'especialidad'
            ]
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
            'fechaNacimiento', 'tipo_documento', 'direccion', 'barrio'
        ]:
            setattr(user, campo, self.cleaned_data.get(campo))

        if commit:
            user.save()

        # Guardar especialidades (ManyToMany) después de guardar el usuario
        if user.tipo_usuario == 'experto':
            user.especialidad.set(self.cleaned_data.get('especialidad'))

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
    
    # --- Campos de Dirección y Barrio para Edición ---
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
        # UserChangeForm incluye 'password' en sus fields por defecto como un enlace a la página de cambio de contraseña.
        # No incluyas 'password' o 'password2' como campos de entrada directa aquí para edición.
        # Usa campos específicos para cambio de contraseña si es necesario.
        fields = (
            'username', 'first_name', 'last_name', 'email',
            'genero', 'tipo_usuario', 'nacionalidad', 'numDoc', 'telefono',
            'fechaNacimiento', 'experienciaTrabajo', 'evidenciaTrabajo', 'hojaVida',
            'hojaVida_file', 'tipo_documento', 'foto_perfil', 'especialidad',
            'direccion', # Añadido aquí
            'barrio',    # Añadido aquí
        
        )
        
        labels = {
            'username': 'Nombre de Usuario',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo Electrónico',
            'evidenciaTrabajo': 'Evidencia de Trabajo (Imagen)',
            'hojaVida_file': 'Archivo de Hoja de Vida',
            'especialidad': 'Especialidad',
            'direccion': 'Dirección de Residencia',
            'barrio': 'Barrio',    # Añadido aquí
        
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
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'barrio': forms.TextInput(attrs={'class': 'form-control'}), # Añadido aquí
        
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
        choices=[],  # se llenará dinámicamente en __init__
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

        # Generar horas desde 00:00 hasta 23:30, cada 30 minutos
        opciones = []
        hora_actual = datetime.strptime("00:00", "%H:%M")
        fin = datetime.strptime("23:30", "%H:%M")
        while hora_actual <= fin:
            valor = hora_actual.strftime("%H:%M")          # Valor que se guarda
            etiqueta = hora_actual.strftime("%I:%M %p")    # Texto visible en el select (12h con AM/PM)
            opciones.append((valor, etiqueta))
            hora_actual += timedelta(minutes=30)

        self.fields['Hora'].choices = opciones










# --- FORMULARIO DE CALIFICACION ---
# Este formulario es para que los usuarios califiquen un servicio con estrellas y un comentario.
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