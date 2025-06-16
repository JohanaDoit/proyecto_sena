import tkinter as tk

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
        ('cliente', 'Cliente'),
        ('experto', 'Experto'),
    ]
    tipo_usuario = forms.ChoiceField(
        choices=tipo_usuario_choices,
        initial='usuario',
        label="Tipo de Usuario",
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
    # CAMBIADO: evidenciaTrabajo ahora es un ImageField en el formulario
    evidenciaTrabajo = forms.ImageField(
        required=False, # Puede ser opcional
        label="Evidencia de Trabajo (Imagen)",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    nacionalidad = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    numDoc = forms.CharField(max_length=100, required=False, label="Número de Documento", widget=forms.TextInput(attrs={'class': 'form-control'}))
    telefono = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    fechaNacimiento = forms.DateField(required=False, label="Fecha de Nacimiento", widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    evidenciaTrabajo = forms.CharField(max_length=200, required=False, label="Evidencia de Trabajo (URL/Descripción)", widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    experienciaTrabajo = forms.CharField(required=False, label="Experiencia de Trabajo", widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))

    tipo_documento = forms.ModelChoiceField(
        queryset=TipoDoc.objects.all().order_by('Nombre'), # <--- CORREGIDO: 'Nombre' (N mayúscula)
        empty_label="Selecciona tipo de documento",
        required=False,
        label="Tipo de Documento",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            'tipo_usuario',
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
            'experienciaTrabajo',
            'evidenciaTrabajo', # Asegúrate de que esté aquí
            'hojaVida_file',
            'foto_perfil',
        )
        labels = {
            # ... (tus labels existentes) ...
            'evidenciaTrabajo': 'Evidencia de Trabajo (Imagen)', # Actualiza el label
            # ... (el resto de tus labels) ...
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
    user = super().save(commit=False)  # Primero se define user
    user.genero = self.cleaned_data.get('genero')
    user.tipo_usuario = self.cleaned_data.get('tipo_usuario')
    user.nacionalidad = self.cleaned_data.get('nacionalidad')
    user.numDoc = self.cleaned_data.get('numDoc')
    user.telefono = self.cleaned_data.get('telefono')
    user.fechaNacimiento = self.cleaned_data.get('fechaNacimiento')
    user.tipo_documento = self.cleaned_data.get('tipo_documento')

    if user.tipo_usuario == 'experto':  # Aquí sí se puede usar
        user.hojaVida_file = self.cleaned_data.get('hojaVida_file')
        user.foto_perfil = self.cleaned_data.get('foto_perfil')
        user.evidenciaTrabajo = self.cleaned_data.get('evidenciaTrabajo')

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
    # CAMBIADO: evidenciaTrabajo ahora es un ImageField en el formulario
    evidenciaTrabajo = forms.ImageField(
        required=False,
        label="Evidencia de Trabajo (Imagen)",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
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
            # ... (tus labels existentes) ...
            'evidenciaTrabajo': 'Evidencia de Trabajo (Imagen)', # Actualiza el label
            # ... (el resto de tus labels) ...
        }
        widgets = {
            'fechaNacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            # 'evidenciaTrabajo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), # ¡ELIMINAR ESTO! Ahora es ImageField
            'experienciaTrabajo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            # 'hojaVida': forms.TextInput(attrs={'class': 'form-control'}), # Eliminar si ya no usas el CharField
        }
        
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.tipo_usuario == 'cliente':
            self.fields['tipo_usuario'].disabled = True

            # Ocultar campos específicos de experto
            self.fields['experienciaTrabajo'].widget = forms.HiddenInput()
            self.fields['evidenciaTrabajo'].widget = forms.HiddenInput() # Ocultar evidenciaTrabajo
            self.fields['hojaVida_file'].widget = forms.HiddenInput()


        # Aplica 'form-control' a la mayoría de los campos
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (
                forms.widgets.DateInput,
                forms.widgets.Textarea,
                forms.widgets.ClearableFileInput, # IMPORTANTE: Excluir ClearableFileInput
                forms.widgets.Select,
                forms.widgets.HiddenInput
            )) and 'class' not in field.widget.attrs:
                field.widget.attrs.update({'class': 'form-control'})

        if 'password' in self.fields:
            del self.fields['password']

    def save(self, commit=True):
        user = super().save(commit=False)
        original_user = CustomUser.objects.get(pk=user.pk)

        # Lógica para manejar la eliminación de archivos si el tipo de usuario cambia de experto a cliente
        if original_user.tipo_usuario == 'experto' and user.tipo_usuario == 'cliente':
            user.evidenciaTrabajo = None # Establece el campo a None para que use la lógica de borrado de ClearableFileInput
            user.experienciaTrabajo = ""
            if original_user.hojaVida_file:
                original_user.hojaVida_file.delete(save=False) # Borra el archivo físico
            user.hojaVida_file = None

            # Si quieres que la foto de perfil también se elimine al pasar a 'cliente'
            # if original_user.foto_perfil and original_user.foto_perfil.url != original_user.foto_perfil.field.default:
            #     original_user.foto_perfil.delete(save=False)
            # user.foto_perfil = original_user.foto_perfil.field.default # O establecer a None

        if commit:
            user.save()
        return user


# ... (ReservaForm no cambia si no está relacionado con evidenciaTrabajo) ...
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
            'detallesAdicionales', 'metodoDePago', 'pais', 'ciudad'
        ]
        widgets = {
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'detallesAdicionales': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }