"""Forms for the onboarding app.

The signup form collects brokerage data (CNPJ + Razão Social required) and
the first admin user's data in a single step. A custom `UserCreationForm`
drives the password handling on top of the email-based ``core.User``.
"""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

from core.models import Brokerage

User = get_user_model()


class BrokerageSignupForm(forms.Form):
    """Public brokerage signup form.

    Captures the brokerage (CNPJ + Razão Social mandatory per RF-BR-02) and
    the administrator account (e-mail + name + password) to be created in a
    single transaction. The chosen ``plan`` is always ``free`` -- paid plans
    are not available during signup (RF-BR-03 / RF-LP-03).
    """

    # --- Brokerage ---
    legal_name = forms.CharField(
        label=_('razão social'),
        max_length=180,
        widget=forms.TextInput(attrs={'autocomplete': 'organization'}),
    )
    cnpj = forms.CharField(
        label='CNPJ',
        max_length=20,
        widget=forms.TextInput(attrs={'autocomplete': 'organization',
                                      'placeholder': '00.000.000/0000-00'}),
        help_text=_('Apenas uma corretora por CNPJ. Formato apenas 14 dígitos.'),
    )
    name = forms.CharField(
        label=_('nome fantasia'),
        max_length=120,
        required=False,
        widget=forms.TextInput(attrs={'autocomplete': 'organization'}),
    )
    email = forms.EmailField(
        label=_('e-mail da corretora'),
        required=False,
        widget=forms.EmailInput(attrs={'autocomplete': 'organization'}),
    )
    phone = forms.CharField(
        label=_('telefone'),
        max_length=32,
        required=False,
        widget=forms.TextInput(attrs={'autocomplete': 'tel'}),
    )
    address = forms.CharField(
        label=_('endereço'),
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'autocomplete': 'street-address'}),
    )

    # --- Administrator account ---
    admin_email = forms.EmailField(
        label=_('e-mail do administrador'),
        widget=forms.EmailInput(attrs={'autocomplete': 'email'}),
    )
    admin_first_name = forms.CharField(
        label=_('nome'),
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'autocomplete': 'given-name'}),
    )
    admin_last_name = forms.CharField(
        label=_('sobrenome'),
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'autocomplete': 'family-name'}),
    )
    admin_password = forms.CharField(
        label=_('senha'),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=_('Mínimo de 8 caracteres.'),
    )
    admin_password_confirm = forms.CharField(
        label=_('confirme a senha'),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )

    plan = forms.CharField(
        label=_('plano'),
        widget=forms.HiddenInput(),
        initial='free',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Render the password validators hint similar to Django auth forms.
        from django.contrib.auth import password_validation
        self.fields['admin_password'].help_text = (
            password_validation.password_validators_help_text_html()
            if password_validation.password_validators_help_texts() else
            self.fields['admin_password'].help_text
        )

    # --- Field validators -------------------------------------------------
    def clean_cnpj(self):
        cnpj = (self.cleaned_data.get('cnpj') or '').strip()
        digits = ''.join(c for c in cnpj if c.isdigit())
        if len(digits) != 14:
            raise forms.ValidationError(_('CNPJ deve conter 14 dígitos.'))
        normalized = f'{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:14]}'

        # Reject duplicates, normalizing both stored and supplied to digits.
        for existing in Brokerage.objects.values_list('cnpj', flat=True):
            if ''.join(c for c in existing if c.isdigit()) == digits:
                raise forms.ValidationError(_('Já existe uma corretora cadastrada com este CNPJ.'))
        return normalized

    def clean(self):
        cleaned = super().clean()

        if cleaned.get('admin_password') != cleaned.get('admin_password_confirm'):
            self.add_error('admin_password_confirm', _('As senhas não conferem.'))

        # Validate the supplied password using Django validators so the UI
        # surfaces errors before persisting anything. We run validation against
        # a transient User instance so unique-to-user similarity checks work.
        password = cleaned.get('admin_password')
        if password:
            temp_user = User(
                email=cleaned.get('admin_email') or '',
                first_name=cleaned.get('admin_first_name') or '',
                last_name=cleaned.get('admin_last_name') or '',
            )
            from django.contrib.auth import password_validation
            try:
                password_validation.validate_password(password, temp_user)
            except forms.ValidationError as err:
                self.add_error('admin_password', err)

        # Confirm that the requested plan actually exists and is available.
        plan_code = cleaned.get('plan') or 'free'
        try:
            plan = __import__('core.models', fromlist=['Plan']).Plan.objects.get(code=plan_code)
        except Exception:
            self.add_error('plan', _('Plano inválido.'))
            return cleaned
        if not plan.is_available:
            self.add_error('plan', _('Plano não disponível para cadastro.'))
        return cleaned