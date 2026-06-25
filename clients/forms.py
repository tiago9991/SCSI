from django import forms
from django.utils.translation import gettext_lazy as _

from clients.models import Client


class ClientForm(forms.ModelForm):
    """ModelForm for creating/updating a tenanted ``Client``."""

    class Meta:
        model = Client
        fields = [
            'first_name',
            'last_name',
            'document',
            'email',
            'phone',
            'birth_date',
            'address',
            'notes',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'autocomplete': 'given-name',
                                                 'placeholder': _('Nome do cliente')}),
            'last_name': forms.TextInput(attrs={'autocomplete': 'family-name',
                                                'placeholder': _('Sobrenome')}),
            'document': forms.TextInput(attrs={'autocomplete': 'off',
                                               'placeholder': '000.000.000-00'}),
            'email': forms.EmailInput(attrs={'autocomplete': 'email'}),
            'phone': forms.TextInput(attrs={'autocomplete': 'tel',
                                            'placeholder': _('+55 (00) 0000-0000')}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'autocomplete': 'bday'}),
            'address': forms.TextInput(attrs={'autocomplete': 'street-address'}),
            'notes': forms.Textarea(attrs={'rows': 4,
                                           'placeholder': _('Observações livre do corretor.')}),
        }
        labels = {
            'first_name': _('Nome'),
            'last_name': _('Sobrenome'),
            'document': 'CPF/CNPJ',
            'email': _('E-mail'),
            'phone': _('Telefone'),
            'birth_date': _('Data de nascimento'),
            'address': _('Endereço'),
            'notes': _('Observações'),
        }