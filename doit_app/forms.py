from django import forms
# Importa todos los modelos necesarios para los ChoiceFields y el Meta.model
from .models import CustomUser, Genero, TipoDoc, Pais, Departamento, Ciudad, Servicios, Estado, Metodo, Reserva

from django.contrib.auth.forms import UserCreationForm, UserChangeForm

class RegistroForm(UserCreationForm):
    # Aquí puedes añadir campos adicionales que no estén en UserCreationForm.Meta.fields
    genero = forms.ModelChoiceField(
        queryset=Genero.objects.all().order_by('Nombre'), # <--- CORREGIDO: 'Nombre' (N mayúscula)
        empty_label="Selecciona tu género",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    tipo_usuario_choices = [
        ('usuario', 'Usuario'),
        ('experto', 'Experto'),
    ]
    tipo_usuario = forms.ChoiceField(
        choices=tipo_usuario_choices,
        initial='usuario',
        label="Tipo de Usuario",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    nacionalidad = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    numDoc = forms.CharField(max_length=100, required=False, label="Número de Documento", widget=forms.TextInput(attrs={'class': 'form-control'}))
    telefono = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    fechaNacimiento = forms.DateField(required=False, label="Fecha de Nacimiento", widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    evidenciaTrabajo = forms.CharField(max_length=200, required=False, label="Evidencia de Trabajo (URL/Descripción)", widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    experienciaTrabajo = forms.CharField(required=False, label="Experiencia de Trabajo", widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    hojaVida = forms.CharField(max_length=300, required=False, label="Link Hoja de Vida", widget=forms.TextInput(attrs={'class': 'form-control'}))
    tipo_documento = forms.ModelChoiceField(
        queryset=TipoDoc.objects.all().order_by('Nombre'), # <--- CORREGIDO: 'Nombre' (N mayúscula)
        empty_label="Selecciona tipo de documento",
        required=False,
        label="Tipo de Documento",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + (
            'first_name', 'last_name', 'email',
            'genero', 'tipo_usuario', 'nacionalidad', 'numDoc', 'telefono', 'fechaNacimiento',
            'evidenciaTrabajo', 'experienciaTrabajo', 'hojaVida', 'tipo_documento',
        )
        labels = {
            'username': 'Nombre de Usuario',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo Electrónico',
            'password2': 'Confirmación de Contraseña',
        }

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
        user = super().save(commit=False)
        user.genero = self.cleaned_data.get('genero')
        user.tipo_usuario = self.cleaned_data.get('tipo_usuario')
        user.nacionalidad = self.cleaned_data.get('nacionalidad')
        user.numDoc = self.cleaned_data.get('numDoc')
        user.telefono = self.cleaned_data.get('telefono')
        user.fechaNacimiento = self.cleaned_data.get('fechaNacimiento')
        user.evidenciaTrabajo = self.cleaned_data.get('evidenciaTrabajo')
        user.experienciaTrabajo = self.cleaned_data.get('experienciaTrabajo')
        user.hojaVida = self.cleaned_data.get('hojaVida')
        user.tipo_documento = self.cleaned_data.get('tipo_documento')

        if commit:
            user.save()
        return user


class PerfilUsuarioForm(UserChangeForm):
    genero = forms.ModelChoiceField(
        queryset=Genero.objects.all().order_by('Nombre'), # <--- CORREGIDO: 'Nombre' (N mayúscula)
        empty_label="Selecciona tu género",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    tipo_documento = forms.ModelChoiceField(
        queryset=TipoDoc.objects.all().order_by('Nombre'), # <--- CORREGIDO: 'Nombre' (N mayúscula)
        empty_label="Selecciona tipo de documento",
        required=False,
        label="Tipo de Documento",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class Meta:
        model = CustomUser
        fields = (
            'username', 'first_name', 'last_name', 'email',
            'genero', 'tipo_usuario', 'nacionalidad', 'numDoc', 'telefono',
            'fechaNacimiento', 'evidenciaTrabajo', 'experienciaTrabajo', 'hojaVida',
            'tipo_documento',
            'foto_perfil',
        )
        labels = {
            'username': 'Nombre de Usuario',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo Electrónico',
            'genero': 'Género',
            'tipo_usuario': 'Tipo de Usuario',
            'nacionalidad': 'Nacionalidad',
            'numDoc': 'Número de Documento',
            'telefono': 'Teléfono',
            'fechaNacimiento': 'Fecha de Nacimiento',
            'evidenciaTrabajo': 'Evidencia de Trabajo',
            'experienciaTrabajo': 'Experiencia de Trabajo',
            'hojaVida': 'Link Hoja de Vida',
            'tipo_documento': 'Tipo de Documento',
            'foto_perfil': 'Foto de Perfil',
        }
        widgets = {
            'fechaNacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'evidenciaTrabajo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'experienciaTrabajo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'hojaVida': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.tipo_usuario == 'usuario':
            self.fields['tipo_usuario'].disabled = True

        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.widgets.DateInput, forms.widgets.Textarea, forms.widgets.ClearableFileInput, forms.widgets.Select)) and \
               'class' not in field.widget.attrs:
                field.widget.attrs.update({'class': 'form-control'})

        if 'password' in self.fields:
            del self.fields['password']


class ReservaForm(forms.ModelForm):
    metodoDePago = forms.ModelChoiceField(
        queryset=Metodo.objects.all().order_by('Nombre'), # <--- CORREGIDO: 'Nombre' (N mayúscula)
        empty_label="Selecciona un método de pago",
        required=True,
        label="Método de Pago",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    pais = forms.ModelChoiceField(
        queryset=Pais.objects.all().order_by('Nombre'), # <--- CORREGIDO: 'Nombre' (N mayúscula)
        empty_label="Selecciona un país",
        required=True,
        label="País",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    ciudad = forms.ModelChoiceField(
        queryset=Ciudad.objects.all().order_by('Nombre'), # <--- CORREGIDO: 'Nombre' (N mayúscula)
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
            'detallesAdicionales', 'metodoDePago', 'pais', 'ciudad'
        ]
        widgets = {
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'detallesAdicionales': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }