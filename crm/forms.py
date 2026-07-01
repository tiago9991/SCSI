"""Forms for the ``crm`` app.

The ``stage`` FK on a Deal must belong to a pipeline of the same brokerage
— :class:`DealForm.clean` enforces that. ``PipelineStageForm`` scopes the
``pipeline`` choices to the current tenant via ``TenantFormMixin``.
"""
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from crm.models import Deal, Pipeline, PipelineStage


class PipelineForm(forms.ModelForm):
    """ModelForm for creating/updating a tenanted ``Pipeline``."""

    class Meta:
        model = Pipeline
        fields = ['name', 'is_default']
        widgets = {
            'name': forms.TextInput(attrs={'autocomplete': 'off',
                                           'placeholder': _('Ex.: Comercial padrão')}),
            'is_default': forms.CheckboxInput(),
        }
        labels = {
            'name': _('Nome'),
            'is_default': _('Pipeline padrão'),
        }
        help_texts = {
            'is_default': _('Apenas um pipeline pode ser o padrão por corretora.'),
        }


class PipelineStageForm(forms.ModelForm):
    """ModelForm for creating/updating a tenanted ``PipelineStage``.

    The ``pipeline`` FK is scoped to the current tenant via the view's
    ``restrict_form_choices`` helper.
    """

    class Meta:
        model = PipelineStage
        fields = ['pipeline', 'name', 'color', 'order']
        widgets = {
            'pipeline': forms.Select(attrs={'class': 'select'}),
            'name': forms.TextInput(attrs={'autocomplete': 'off',
                                           'placeholder': _('Ex.: Lead')}),
            'color': forms.TextInput(attrs={'type': 'color'}),
            'order': forms.NumberInput(attrs={'min': 0, 'step': 1, 'placeholder': '0'}),
        }
        labels = {
            'pipeline': _('Pipeline'),
            'name': _('Nome'),
            'color': _('Cor'),
            'order': _('Ordem'),
        }


class DealForm(forms.ModelForm):
    """ModelForm for creating/updating a tenanted ``Deal``.

    FK choices (client, stage, producer) are scoped to the current tenant from
    the view via ``TenantFormMixin.restrict_form_choices``.
    """

    class Meta:
        model = Deal
        fields = [
            'client',
            'stage',
            'producer',
            'title',
            'amount',
            'expected_close_date',
            'status',
        ]
        widgets = {
            'client': forms.Select(attrs={'class': 'select'}),
            'stage': forms.Select(attrs={'class': 'select'}),
            'producer': forms.Select(attrs={'class': 'select'}),
            'title': forms.TextInput(attrs={'autocomplete': 'off',
                                             'placeholder': _('Título da negociação')}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0,00'}),
            'expected_close_date': forms.DateInput(attrs={'type': 'date', 'autocomplete': 'off'}),
            'status': forms.Select(attrs={'class': 'select'}),
        }
        labels = {
            'client': _('Cliente'),
            'stage': _('Etapa'),
            'producer': _('Produtor'),
            'title': _('Título'),
            'amount': _('Valor'),
            'expected_close_date': _('Fechamento previsto'),
            'status': _('Status'),
        }

    def clean(self):
        cleaned = super().clean()
        client = cleaned.get('client')
        stage = cleaned.get('stage')
        if client and stage:
            # Both are tenant-scoped, but ensure the stage's pipeline matches
            # the brokerage of the client — they should already match since
            # both come from for_tenant(), but the cross-check protects against
            # form tampering.
            if client.brokerage_id != stage.brokerage_id:
                raise ValidationError(
                    _('O cliente e a etapa selecionados pertencem a corretoras diferentes.')
                )
        return cleaned