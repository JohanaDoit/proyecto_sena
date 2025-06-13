from django.contrib import admin
from django.urls import path, include
from django.conf import settings  # <--- ¡Esta línea es crucial!
from django.conf.urls.static import static # <--- ¡Esta línea también es crucial!

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('doit_app.urls')),
]

# Esto solo sirve archivos de medios en modo de desarrollo (DEBUG = True)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)