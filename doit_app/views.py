from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistroForm, PerfilUsuarioForm
from django.contrib.auth.decorators import login_required # Mantén esta importación para otras vistas
from django.contrib import messages
from .forms import ReservaForm
from .models import Estado
from .models import Servicios , Categorias

def home(request): 
    return render(request, 'home.html')

@login_required
def principal(request):
    categorias = Categorias.objects.all()
    servicios = Servicios.objects.all()
    
    # Agrupamos los servicios por categoría (clave: id o nombre de categoría)
    servicios_por_categoria = {}
    for cat in categorias:
        servicios_por_categoria[cat.Nombre] = list(servicios.filter(idCategorias=cat))
    
    return render(request, 'principal.html', {
        'categorias': categorias,
        'servicios_por_categoria': servicios_por_categoria,
    })

@login_required
def busc_experto(request):
    return render(request, 'busc_experto.html')

@login_required
def modificar(request):
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
    servicio_id = request.GET.get('servicio_id') or request.session.get('servicio_id')

    if servicio_id:
        request.session['servicio_id'] = servicio_id  # guardamos en sesión para mantener entre peticiones
    else:
        messages.error(request, "Servicio no seleccionado. Por favor, selecciona un servicio primero.")
        return redirect('principal')  # Cambia por el nombre real de tu url principal

    servicio = Servicios.objects.filter(id=servicio_id).first()
    if not servicio:
        messages.error(request, "Servicio inválido.")
        return redirect('principal')

    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.idUsuario = request.user
            reserva.idEstado_id = 1  # estado inicial
            reserva.idServicios = servicio
            reserva.save()
            messages.info(request,  f"✅ Reserva pendiente para {request.user.get_full_name() or request.user.username}\n"
                                    f"🛎️ Servicio: {servicio.NombreServicio}\n"
                                    f"📅 Fecha: {reserva.Fecha}\n"
                                    f"🕒 Hora: {reserva.Hora}\n"
                                    f"📍 Dirección: {reserva.direccion}"
            )
            return redirect('principal')  # O a donde quieras redirigir luego de reservar
    else:
        form = ReservaForm()
    return render(request, 'reserva.html', {'form': form, 'servicio': servicio})






@login_required
def servicioAceptado(request):
    return render(request, 'servicioAceptado.html')

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
        if form.is_valid():
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
        if form.is_valid():
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

@login_required
def editar_perfil_view(request):
    user = request.user
    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Tu perfil ha sido actualizado con éxito!')
            return redirect('perfil')
        else:
            messages.error(request, 'Hubo un error al actualizar tu perfil. Por favor, revisa los datos.')
            print("El formulario de perfil no es válido. Errores:", form.errors)
    else:
        form = PerfilUsuarioForm(instance=user)
    return render(request, 'modificar.html', {'form': form})

def nosotros(request):
    return render(request, 'nosotros.html')

def terminos_condiciones(request):
    return render(request, 'terminos_condiciones.html')

def tratamiento_datos(request):
    return render(request, 'tratamiento_datos.html')
