"""URL configuration for the core project."""
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path

from core.views import (
    LoginView,
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)


def health(request):
    """Lightness probe: no DB, no auth. Used by container HEALTHCHECK and Traefik."""
    return HttpResponse('ok', content_type='text/plain')


urlpatterns = [
    # --- Landing + Onboarding (root ``/`` and `/cadastro/`) ---
    path('', include(('onboarding.urls', 'onboarding'), namespace='onboarding')),

    path('admin/', admin.site.urls),
    path('health/', health, name='health'),

    # --- Auth (e-mail based login + native password reset flow) ---
    path('accounts/login/', LoginView.as_view(), name='login'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('accounts/password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('accounts/password-reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # --- Domain apps ---
    path('', include('clients.urls')),
    path('', include('catalog.urls')),
    path('', include('proposals.urls')),
    path('', include('policies.urls')),
    path('', include('claims.urls')),
    path('', include('attachments.urls')),
    path('', include('crm.urls')),
    path('', include('commercial.urls')),
]