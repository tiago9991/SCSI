from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _


class EmailAuthenticationForm(AuthenticationForm):
    """Authentication form that uses the user's email instead of a username.

    Backed by the native Django auth backend (which authenticates against
    ``USERNAME_FIELD``), this only changes the rendered field label and widget
    so the UI asks for an e-mail address.
    """

    username = forms.EmailField(
        label=_('e-mail'),
        widget=forms.EmailInput(attrs={'autofocus': True, 'autocomplete': 'email'}),
        max_length=254,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # AuthenticationForm uses self.fields['username'] internally; the
        # custom field above overrides it. Keep the password widget consistent.
        self.fields['password'].widget.attrs.update({'autocomplete': 'current-password'})