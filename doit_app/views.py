from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistroForm, PerfilUsuarioForm # Asegúrate de que PerfilUsuarioForm está importado
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ReservaForm
from .models import Estado, Servicios, Categorias 
from .models import Reserva
from django.conf import settings
import requests
# Asegúrate de que todos los modelos necesarios están importados

# --- Vistas Generales ---
def home(request):
    return render(request, 'home.html')

@login_required
def principal(request):
    categorias = Categorias.objects.all()
    servicios = Servicios.objects.all()

    # Agrupar servicios por categoría
    servicios_por_categoria = {}
    for cat in categorias:
        servicios_por_categoria[cat.Nombre] = list(servicios.filter(idCategorias=cat))

    # Obtener las últimas 3 reservas del usuario autenticado, ordenadas por fecha más reciente
    ultimas_reservas = Reserva.objects.filter(
        idUsuario=request.user
    ).order_by('-Fecha', '-Hora')[:3]

    return render(request, 'principal.html', {
        'categorias': categorias,
        'servicios_por_categoria': servicios_por_categoria,
        'ultimas_reservas': ultimas_reservas,
    })


@login_required
def busc_experto(request):
    return render(request, 'busc_experto.html')

@login_required
def modificar(request):
    # Esta vista 'modificar' parece ser solo un render de una plantilla.
    # Si quieres que desde aquí se vaya a la edición de perfil, deberías redirigir:
    # return redirect('nombre_de_la_url_para_editar_perfil')
    return render(request, 'modificar.html')

@login_required
def servicioAceptado(request):
    return render(request, 'servicioAceptado.html')

@login_required
def servicioAceptadoexpe(request):
    return render(request, 'servicioAceptadoexpe.html')

@login_required
def chat(request):
    return render(request, 'chat.html')

@login_required
def servicioCancelado(request):
    return render(request, 'servicioCancelado.html')

@login_required
def servicioCanceladoexpe(request):
    return render(request, 'servicioCanceladoexpe.html')

@login_required
def experto(request):
    return render(request, 'experto.html')

@login_required
def historial_experto(request):
    return render(request, 'historial_experto.html')

@login_required
def fin(request):
    return render(request, 'fin.html')

@login_required
def normalizacion(request):
    return render(request, 'normalizacion.html')

@login_required
def modelo_relacional(request):
    return render(request, 'modelo_relacional.html')

@login_required
def sentenciasddl(request):
    return render(request, 'sentenciasddl.html')

@login_required
def sentencias_dml(request):
    return render(request, 'sentencias_dml.html')

@login_required
def diccionario_de_datos(request):
    return render(request, 'diccionario_de_datos.html')

@login_required
def diagrama_de_clases(request):
    return render(request, 'diagrama_de_clases.html')

@login_required
def admin_principal(request):
    return render(request, 'admin_principal.html')

@login_required
def solicitudes_admin(request):
    return render(request, 'solicitudes_admin.html')


@login_required
def reserva(request):
    # Obtener el ID del servicio desde GET o sesión
    servicio_id = request.GET.get('servicio_id') or request.session.get('servicio_id')

    # Verificar si hay ID de servicio
    if not servicio_id:
        messages.error(request, "⚠️ Servicio no seleccionado. Por favor, elige un servicio.")
        return redirect('principal')

    # Guardar el ID del servicio en la sesión
    request.session['servicio_id'] = servicio_id

    # Buscar el servicio
    servicio = Servicios.objects.filter(id=servicio_id).first()

    # Validar que el servicio exista
    if not servicio:
        messages.error(request, "❌ El servicio seleccionado no existe.")
        return redirect('principal')

    # Si el formulario fue enviado (POST)
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.idUsuario = request.user
            reserva.idEstado_id = 1  # Estado inicial
            reserva.idServicios = servicio
            reserva.save()

            messages.info(
                request,
                f"✅ Reserva pendiente para {request.user.get_full_name() or request.user.username}\n"
                f"🛎️ Servicio: {servicio.NombreServicio}\n"
                f"📅 Fecha: {reserva.Fecha}\n"
                f"🕒 Hora: {reserva.Hora}\n"
                f"📍 Dirección: {reserva.direccion}"
            )
            return redirect('principal')
    else:
        form = ReservaForm()

    return render(request, 'reserva.html', {
        'form': form,
        'servicio': servicio
    })


# --- Vistas de Autenticación y Registro (NO deben tener @login_required) ---

def user_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect(reverse_lazy('principal'))
    else:
        form = AuthenticationForm()
    return render(request, 'sign-in/login.html', {'form': form})

def user_logout_view(request):
    auth_logout(request)
    return redirect(reverse_lazy('home'))

def login_experto(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'experto':
                auth_login(request, user)
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect(reverse_lazy('experto'))
            else:
                form.add_error(None, "Las credenciales no corresponden a un experto.")
        return render(request, 'sign-in/login_experto.html', {'form': form})
    else:
        form = AuthenticationForm()
    return render(request, 'sign-in/login_experto.html', {'form': form})

def login_admin(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'admin':
                auth_login(request, user)
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect(reverse_lazy('admin_principal'))
            else:
                form.add_error(None, "Las credenciales no corresponden a un administrador.")
        return render(request, 'sign-in/login_admin.html', {'form': form})
    else:
        form = AuthenticationForm()
    return render(request, 'sign-in/login_admin.html', {'form': form})

# --- Vistas de Registro (NO deben tener @login_required) ---
def registrarse(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)

        # Validar reCAPTCHA
        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.RECAPTCHA_PRIVATE_KEY,
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        if not result.get('success'):
            messages.error(request, '⚠️ Debes verificar que no eres un robot.')
        elif form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect(reverse_lazy('principal'))
        else:
            print(form.errors)
    else:
        form = RegistroForm(initial={'tipo_usuario': 'usuario'})
    return render(request, 'registrarse.html', {'form': form})

def regisexperto(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)

        # Validar reCAPTCHA
        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.RECAPTCHA_PRIVATE_KEY,
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        if not result.get('success'):
            messages.error(request, '⚠️ Debes verificar que no eres un robot.')
        elif form.is_valid():
            user = form.save(commit=False)
            user.tipo_usuario = 'experto'
            user.save()
            auth_login(request, user)
            return redirect(reverse_lazy('experto'))
        else:
            print(form.errors)
    else:
        form = RegistroForm(initial={'tipo_usuario': 'experto'})
    return render(request, 'regisexperto.html', {'form': form})

# --- Vistas de Perfil de Usuario (la que estamos depurando) ---
@login_required
def editar_perfil_view(request): # Nombre de la función tal como está en tu urls.py
    user = request.user
    if request.method == 'POST':
        # --- LÍNEAS DE DEPURACIÓN CLAVE ---
        print("\n--- INICIO DE DEPURACIÓN DE FORMULARIO DE PERFIL ---")
        print("request.POST:", request.POST)
        print("request.FILES:", request.FILES) # Esto es vital para la subida de archivos

        form = PerfilUsuarioForm(request.POST, request.FILES, instance=user) # ¡request.FILES es crucial aquí!

        if form.is_valid():
            print("Formulario de Perfil es VÁLIDO.")
            try:
                user_instance = form.save()
                # Verifica si la foto de perfil existe y tiene una URL para imprimirla
                photo_url = user_instance.foto_perfil.url if user_instance.foto_perfil else 'No hay foto'
                print(f"Formulario guardado exitosamente. Foto de perfil actual: {photo_url}")
                messages.success(request, '¡Tu perfil ha sido actualizado con éxito!')
                print("--- FIN DE DEPURACIÓN (ÉXITO) ---\n")
                # Redirige a la página principal o a donde se muestre el perfil actualizado.
                # Asegúrate de que 'principal' es el nombre de la URL de tu página principal.
                return redirect('principal') 
            except Exception as e:
                print(f"ERROR al guardar el formulario de perfil: {e}")
                messages.error(request, f'Hubo un error al guardar el perfil: {e}')
                print("--- FIN DE DEPURACIÓN (ERROR DE GUARDADO) ---\n")
        else:
            print("Formulario de Perfil NO es VÁLIDO.")
            print("Errores del formulario:", form.errors) # <-- ¡Esto es CRÍTICO para ver qué falla!
            messages.error(request, 'Hubo un error al actualizar tu perfil. Por favor, revisa los datos.')
            print("--- FIN DE DEPURACIÓN (VALIDACIÓN FALLIDA) ---\n")
    else:
        form = PerfilUsuarioForm(instance=user)

    # --- RUTA DE LA PLANTILLA CORREGIDA ---
    # Si la plantilla está directamente en doit_app/templates/, no necesita 'doit_app/' antes.
    return render(request, 'modificar.html', {'form': form})


# Vistas de contenido estático
def nosotros(request):
    return render(request, 'nosotros.html')

def terminos_condiciones(request):
    return render(request, 'terminos_condiciones.html')

def tratamiento_datos(request):
    return render(request, 'tratamiento_datos.html')