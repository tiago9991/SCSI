"""URL configuration for the core project."""
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path


def health(request):
    """Lightweight liveness probe: no DB, no auth. Used by container HEALTHCHECK and Traefik."""
    return HttpResponse('ok', content_type='text/plain')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health, name='health'),
]