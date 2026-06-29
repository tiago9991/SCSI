from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from claims.models import Claim


class ClaimForm(forms.ModelForm):
    """ModelForm for creating/updating a tenanted ``Claim``.

    Per PRD §20.5 the claim must reference a ``Policy`` and one of its
    ``PolicyCoveredItem``s. The view scopes FK choices to the current tenant
    via ``TenantFormMixin.restrict_form_choices``; here we additionally
    validate that the selected covered item really belongs to the selected
    policy and that the client matches the policy's client.
    """

    class Meta:
        model = Claim
        fields = [
            'policy',
            'covered_item',
            'client',
            'number',
            'occurrence_date',
            'description',
            'status',
            'amount',
        ]
        widgets = {
            'policy': forms.Select(attrs={'class': 'select'}),
            'covered_item': forms.Select(attrs={'class': 'select'}),
            'client': forms.Select(attrs={'class': 'select'}),
            'number': forms.TextInput(attrs={'autocomplete': 'off',
                                             'placeholder': _('Número do sinistro')}),
            'occurrence_date': forms.DateInput(attrs={'type': 'date', 'autocomplete': 'off'}),
            'description': forms.Textarea(attrs={'rows': 4,
                                                'placeholder': _('Descreva a ocorrência...')}),
            'status': forms.Select(attrs={'class': 'select'}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0,00'}),
        }
        labels = {
            'policy': _('Apólice'),
            'covered_item': _('Item coberto'),
            'client': _('Cliente'),
            'number': _('Número'),
            'occurrence_date': _('Data da ocorrência'),
            'description': _('Descrição'),
            'status': _('Status'),
            'amount': _('Valor'),
        }

    def clean(self):
        cleaned = super().clean()
        policy = cleaned.get('policy')
        covered_item = cleaned.get('covered_item')
        client = cleaned.get('client')
        if policy and covered_item and covered_item.policy_id != policy.id:
            raise ValidationError({
                'covered_item': _('O item coberto selecionado não pertence à apólice selecionada.'),
            })
        if policy and client and policy.client_id != client.id:
            raise ValidationError({
                'client': _('O cliente selecionado não corresponde ao cliente da apólice.'),
            })
        return cleaned