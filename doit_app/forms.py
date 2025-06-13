# asistencia/forms.py

from django import forms
from .models import CustomUser, Genero
from .models import Reserva
from django.contrib.auth.forms import UserCreationForm # Importa UserCreationForm para RegistroForm
from django.contrib.auth.forms import UserChangeForm # ¡NECESITARÁS ESTA IMPORTACIÓN para PerfilUsuarioForm!


class RegistroForm(UserCreationForm):
    # Aquí puedes añadir campos adicionales que no estén en UserCreationForm.Meta.fields
    genero = forms.ModelChoiceField(
        queryset=Genero.objects.all().order_by('nombre'),
        empty_label="Selecciona tu género",
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

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + (
            'first_name', 'last_name', 'email',
            'genero', 'tipo_usuario', 'nacionalidad', 'numDoc', 'telefono', 'fechaNacimiento',
            'evidenciaTrabajo', 'experienciaTrabajo', 'hojaVida',
        )
        labels = {
            'username': 'Nombre de Usuario',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo Electrónico',
        }

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

        if commit:
            user.save()
        return user


class PerfilUsuarioForm(UserChangeForm): # UserChangeForm es un buen punto de partida para editar usuarios existentes
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = (
            'username', 'first_name', 'last_name', 'email',
            'genero', 'tipo_usuario', 'nacionalidad', 'numDoc', 'telefono',
            'fechaNacimiento', 'evidenciaTrabajo', 'experienciaTrabajo', 'hojaVida',
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
        }

# Puedes personalizar el widget de cada campo si lo necesitas, similar a RegistroForm
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
    Fecha = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        input_formats=['%Y-%m-%d'],
        label='Fecha'
    )
    Hora = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
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