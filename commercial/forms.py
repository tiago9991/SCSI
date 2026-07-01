"""Forms for the commercial app (Agent, Producer, Commission)."""
from django import forms
from django.utils.translation import gettext_lazy as _

from commercial.models import Agent, Commission, Producer


class AgentForm(forms.ModelForm):
    """ModelForm for creating/updating a tenanted ``Agent``."""

    class Meta:
        model = Agent
        fields = ['name', 'document', 'type', 'commission_percent', 'contact']
        widgets = {
            'name': forms.TextInput(attrs={'autocomplete': 'off',
                                            'placeholder': _('Nome do agente')}),
            'document': forms.TextInput(attrs={'autocomplete': 'off',
                                                'placeholder': _('CPF/CNPJ')}),
            'type': forms.Select(attrs={'class': 'select'}),
            'commission_percent': forms.NumberInput(attrs={'step': '0.01', 'min': 0, 'max': 100, 'placeholder': '0,00'}),
            'contact': forms.TextInput(attrs={'autocomplete': 'off',
                                              'placeholder': _('E-mail / telefone')}),
        }
        labels = {
            'name': _('Nome'),
            'document': _('Documento'),
            'type': _('Tipo'),
            'commission_percent': _('% Comissão'),
            'contact': _('Contato'),
        }


class ProducerForm(forms.ModelForm):
    """ModelForm for creating/updating a tenanted ``Producer``.

    ``agent`` is nullable so a producer can be direct to the brokerage (PRD
    §21.2). The ``agent`` queryset is scoped to the current tenant via the
    view's ``restrict_form_choices``.
    """

    class Meta:
        model = Producer
        fields = ['name', 'agent', 'document', 'commission_percent', 'contact']
        widgets = {
            'name': forms.TextInput(attrs={'autocomplete': 'off',
                                            'placeholder': _('Nome do produtor')}),
            'agent': forms.Select(attrs={'class': 'select'}),
            'document': forms.TextInput(attrs={'autocomplete': 'off',
                                                'placeholder': _('CPF')}),
            'commission_percent': forms.NumberInput(attrs={'step': '0.01', 'min': 0, 'max': 100, 'placeholder': '0,00'}),
            'contact': forms.TextInput(attrs={'autocomplete': 'off',
                                              'placeholder': _('E-mail / telefone')}),
        }
        labels = {
            'name': _('Nome'),
            'agent': _('Agente'),
            'document': _('Documento'),
            'commission_percent': _('% Comissão'),
            'contact': _('Contato'),
        }


class CommissionForm(forms.ModelForm):
    """ModelForm for creating/updating a tenanted ``Commission`` (Sprint 20).

    Shares are computed automatically in ``clean`` from the configured
    percentuais of the selected ``agent`` / ``producer`` so the rendered screen
    always reflects the brokerage / agent / producer split (PRD §21.3).
    """

    class Meta:
        model = Commission
        fields = [
            'amount', 'policy', 'proposal', 'agent', 'producer', 'reference_date',
        ]
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0,00'}),
            'policy': forms.Select(attrs={'class': 'select'}),
            'proposal': forms.Select(attrs={'class': 'select'}),
            'agent': forms.Select(attrs={'class': 'select'}),
            'producer': forms.Select(attrs={'class': 'select'}),
            'reference_date': forms.DateInput(attrs={'type': 'date', 'autocomplete': 'off'}),
        }
        labels = {
            'amount': _('Valor total'),
            'policy': _('Apólice'),
            'proposal': _('Proposta'),
            'agent': _('Agente'),
            'producer': _('Produtor'),
            'reference_date': _('Data de referência'),
        }

    def clean(self):
        cleaned = super().clean()
        amount = cleaned.get('amount') or 0
        agent = cleaned.get('agent')
        producer = cleaned.get('producer')
        from commercial.services import calculate_shares
        b, a, p = calculate_shares(amount, agent, producer)
        cleaned['brokerage_share'] = b
        cleaned['agent_share'] = a
        cleaned['producer_share'] = p
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.brokerage_share = self.cleaned_data['brokerage_share']
        instance.agent_share = self.cleaned_data['agent_share']
        instance.producer_share = self.cleaned_data['producer_share']
        if commit:
            instance.save()
        return instance