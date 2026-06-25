"""Authentication views for the SCSI project.

All views are Class Based Views reusing the native Django auth machinery
(`django.contrib.auth.views`). They override the login form to ask for the
user's e-mail (matching ``AUTH_USER_MODEL``'s ``USERNAME_FIELD = 'email'``)
and render pt-br templates following the design system.
"""
from django.contrib.auth import views as auth_views

from core.forms import EmailAuthenticationForm


class LoginView(auth_views.LoginView):
    """Login by e-mail + password."""

    template_name = 'accounts/login.html'
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True
    extra_context = {'title': 'Acessar'}


class LogoutView(auth_views.LogoutView):
    """Logout via POST (native Django auth)."""

    template_name = 'accounts/logged_out.html'
    extra_context = {'title': 'Sair'}


class PasswordResetView(auth_views.PasswordResetView):
    """Request a password reset link by e-mail (native Django)."""

    template_name = 'accounts/password_reset_form.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = '/accounts/password-reset/done/'
    extra_context = {'title': 'Recuperar senha'}


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    """Confirmation page shown after the reset e-mail is sent."""

    template_name = 'accounts/password_reset_done.html'
    extra_context = {'title': 'E-mail enviado'}


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    """Set a new password using the token sent by e-mail."""

    template_name = 'accounts/password_reset_confirm.html'
    success_url = '/accounts/reset/done/'
    extra_context = {'title': 'Nova senha'}


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    """Final confirmation page after the password has been changed."""

    template_name = 'accounts/password_reset_complete.html'
    extra_context = {'title': 'Senha redefinida'}