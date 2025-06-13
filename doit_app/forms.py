from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Genero, Reserva

class RegistroForm(UserCreationForm):
    genero = forms.ModelChoiceField(
        queryset=Genero.objects.all().order_by('nombre'),
        required=False,
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

    nacionalidad = forms.CharField(
        max_length=100, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    numDoc = forms.CharField(
        max_length=100, required=False, label="Número de Documento",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    telefono = forms.CharField(
        max_length=15, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    fechaNacimiento = forms.DateField(
        required=False, label="Fecha de Nacimiento",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    evidenciaTrabajo = forms.CharField(
        max_length=200, required=False, label="Evidencia de Trabajo (URL/Descripción)",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    experienciaTrabajo = forms.CharField(
        required=False, label="Experiencia de Trabajo",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    hojaVida = forms.CharField(
        max_length=300, required=False, label="Link Hoja de Vida",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CustomUser
        fields = (
            'username', 'password1', 'password2', 'first_name', 'last_name', 'email',
            'genero', 'tipo_usuario', 'nacionalidad', 'numDoc',
            'telefono', 'fechaNacimiento', 'evidenciaTrabajo',
            'experienciaTrabajo', 'hojaVida',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            if field_name not in ['password1', 'password2']:
                self.fields[field_name].widget.attrs.update({'class': 'form-control'})
