import json

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from policies.models import Endorsement, Policy, PolicyCoveredItem, Renewal


class PolicyForm(forms.ModelForm):
    """ModelForm for creating/updating a tenanted ``Policy``.

    FK choices (proposal, client, insurance_company, branch) are scoped to the
    current tenant from the view via ``TenantFormMixin.restrict_form_choices``.
    The ``proposal`` field is optional (a policy may be created standalone or
    originate from the "Gerar apólice" flow in Sprint 12).
    """

    class Meta:
        model = Policy
        fields = [
            'proposal',
            'client',
            'insurance_company',
            'branch',
            'number',
            'status',
            'start_date',
            'end_date',
            'premium',
        ]
        widgets = {
            'proposal': forms.Select(attrs={'class': 'select'}),
            'client': forms.Select(attrs={'class': 'select'}),
            'insurance_company': forms.Select(attrs={'class': 'select'}),
            'branch': forms.Select(attrs={'class': 'select'}),
            'number': forms.TextInput(attrs={'autocomplete': 'off',
                                             'placeholder': _('Número da apólice')}),
            'status': forms.Select(attrs={'class': 'select'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'autocomplete': 'off'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'autocomplete': 'off'}),
            'premium': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0,00'}),
        }
        labels = {
            'proposal': _('Proposta'),
            'client': _('Cliente'),
            'insurance_company': _('Seguradora'),
            'branch': _('Ramo'),
            'number': _('Número'),
            'status': _('Status'),
            'start_date': _('Início da vigência'),
            'end_date': _('Fim da vigência'),
            'premium': _('Prêmio'),
        }


class PolicyCoveredItemForm(forms.ModelForm):
    """ModelForm for creating/updating a tenanted ``PolicyCoveredItem``.

    The ``policy`` FK is stamped from the URL on create (see the view) and the
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
        model = PolicyCoveredItem
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


class EndorsementForm(forms.ModelForm):
    """ModelForm for creating/updating a tenanted ``Endorsement`` (Sprint 18).

    The ``policy`` FK is stamped from the URL on create (see the nested view)
    and excluded from the rendered form.
    """

    class Meta:
        model = Endorsement
        fields = ['number', 'type', 'description', 'effective_date']
        widgets = {
            'number': forms.TextInput(attrs={'autocomplete': 'off',
                                              'placeholder': _('Número do endosso')}),
            'type': forms.Select(attrs={'class': 'select'}),
            'description': forms.Textarea(attrs={'rows': 4,
                                                  'placeholder': _('Descreva o endosso...')}),
            'effective_date': forms.DateInput(attrs={'type': 'date', 'autocomplete': 'off'}),
        }
        labels = {
            'number': _('Número'),
            'type': _('Tipo'),
            'description': _('Descrição'),
            'effective_date': _('Data de eficácia'),
        }


class RenewalForm(forms.ModelForm):
    """ModelForm for creating/updating a tenanted ``Renewal`` (Sprint 17).

    When used from the top-level create view, ``policy`` is rendered as a
    tenant-scoped select (the view's ``restrict_form_choices`` narrows the
    queryset). When the renewal is created from a policy detail page, the
    nested view excludes ``policy`` from the form and stamps it from the URL.
    """

    class Meta:
        model = Renewal
        fields = ['policy', 'due_date', 'status', 'notes']
        widgets = {
            'policy': forms.Select(attrs={'class': 'select'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'autocomplete': 'off'}),
            'status': forms.Select(attrs={'class': 'select'}),
            'notes': forms.Textarea(attrs={'rows': 4,
                                            'placeholder': _('Observações sobre a renovação...')}),
        }
        labels = {
            'policy': _('Apólice'),
            'due_date': _('Vencimento'),
            'status': _('Status'),
            'notes': _('Observações'),
        }


class RenewalNestedForm(forms.ModelForm):
    """Nested renewal form (no ``policy`` field — stamped from the URL)."""

    class Meta:
        model = Renewal
        fields = ['due_date', 'status', 'notes']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date', 'autocomplete': 'off'}),
            'status': forms.Select(attrs={'class': 'select'}),
            'notes': forms.Textarea(attrs={'rows': 4,
                                            'placeholder': _('Observações sobre a renovação...')}),
        }
        labels = {
            'due_date': _('Vencimento'),
            'status': _('Status'),
            'notes': _('Observações'),
        }