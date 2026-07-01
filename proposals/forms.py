import json

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from proposals.models import Proposal, ProposalCoveredItem


class ProposalForm(forms.ModelForm):
    """ModelForm for creating/updating a tenanted ``Proposal``.

    FK choices (client, insurance_company, branch, producer) are scoped to the
    current tenant from the view via ``TenantFormMixin.restrict_form_choices``.
    The ``producer`` FK (commercial.Producer, nullable per PRD §16.5) is
    optional.
    """

    class Meta:
        model = Proposal
        fields = [
            'client',
            'insurance_company',
            'branch',
            'producer',
            'status',
            'valid_until',
            'premium',
            'notes',
        ]
        widgets = {
            'client': forms.Select(attrs={'class': 'select'}),
            'insurance_company': forms.Select(attrs={'class': 'select'}),
            'branch': forms.Select(attrs={'class': 'select'}),
            'producer': forms.Select(attrs={'class': 'select'}),
            'status': forms.Select(attrs={'class': 'select'}),
            'valid_until': forms.DateInput(attrs={'type': 'date', 'autocomplete': 'off'}),
            'premium': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0,00'}),
            'notes': forms.Textarea(attrs={'rows': 4,
                                           'placeholder': _('Observações livre da proposta.')}),
        }
        labels = {
            'client': _('Cliente'),
            'insurance_company': _('Seguradora'),
            'branch': _('Ramo'),
            'producer': _('Produtor'),
            'status': _('Status'),
            'valid_until': _('Válido até'),
            'premium': _('Prêmio'),
            'notes': _('Observações'),
        }


class ProposalCoveredItemForm(forms.ModelForm):
    """ModelForm for creating/updating a tenanted ``ProposalCoveredItem``.

    The ``proposal`` FK is stamped from the URL on create (see the view) and the
    user must never choose it manually, so it is excluded from the rendered
    form. The flexible ``attributes`` JSON payload is edited through a textarea
    accepting valid JSON; non-JSON input is rejected with a friendly message.
    """

    attributes_text = forms.CharField(
        label=_('Atributos (JSON)'),
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': '{"placa": "ABC1D23", "cor": "preto"}',
        }),
        help_text=_('Atributos flexíveis em JSON (placa, endereço, lista de itens, destino, etc.).'),
    )

    class Meta:
        model = ProposalCoveredItem
        fields = ['kind', 'description', 'value']
        widgets = {
            'kind': forms.Select(attrs={'class': 'select'}),
            'description': forms.TextInput(attrs={'autocomplete': 'off',
                                                  'placeholder': _('Descrição do objeto segurado')}),
            'value': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0,00'}),
        }
        labels = {
            'kind': _('Tipo'),
            'description': _('Descrição'),
            'value': _('Valor'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Seed the textarea with the stored JSON (pretty-printed for editing).
        initial_json = ''
        if self.instance and self.instance.pk and self.instance.attributes:
            try:
                initial_json = json.dumps(self.instance.attributes, ensure_ascii=False, indent=2)
            except (TypeError, ValueError):
                initial_json = ''
        self.fields['attributes_text'].initial = initial_json

    def clean_attributes_text(self):
        raw = self.cleaned_data.get('attributes_text', '').strip()
        if not raw:
            return {}
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValidationError(_('JSON inválido: %(err)s') % {'err': exc.msg})
        if not isinstance(parsed, dict):
            raise ValidationError(_('O JSON deve ser um objeto (chaves/valores).'))
        return parsed

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.attributes = self.cleaned_data.get('attributes_text', {}) or {}
        if commit:
            instance.save()
        return instance