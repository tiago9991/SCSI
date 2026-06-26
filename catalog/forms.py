from django import forms
from django.utils.translation import gettext_lazy as _

from catalog.models import Branch, Coverage, InsuranceCompany


class InsuranceCompanyForm(forms.ModelForm):
    """ModelForm for creating/updating a tenanted ``InsuranceCompany``."""

    class Meta:
        model = InsuranceCompany
        fields = ['name', 'code', 'document', 'contact']
        widgets = {
            'name': forms.TextInput(attrs={'autocomplete': 'off',
                                           'placeholder': _('Nome da seguradora')}),
            'code': forms.TextInput(attrs={'autocomplete': 'off',
                                           'placeholder': _('Código interno')}),
            'document': forms.TextInput(attrs={'autocomplete': 'off',
                                              'placeholder': '00.000.000/0000-00'}),
            'contact': forms.TextInput(attrs={'autocomplete': 'off',
                                              'placeholder': _('Telefone / e-mail / representante')}),
        }
        labels = {
            'name': _('Nome'),
            'code': _('Código'),
            'document': 'CNPJ',
            'contact': _('Contato'),
        }


class BranchForm(forms.ModelForm):
    """ModelForm for creating/updating a tenanted ``Branch``."""

    BRANCH_SUGGESTIONS = [
        ('Auto', _('Auto')),
        ('Residencial', _('Residencial')),
        ('Vida', _('Vida')),
        ('Viagem', _('Viagem')),
        ('Empresarial', _('Empresarial')),
        ('Frota', _('Frota')),
        ('Outros', _('Outros')),
    ]

    name = forms.CharField(
        label=_('Nome'),
        widget=forms.TextInput(attrs={'autocomplete': 'off',
                                       'placeholder': _('Ex.: Auto, Residencial, Vida...'),
                                       'list': 'branch-suggestions'}),
        help_text=_('Sugestões: auto, residencial, vida, viagem, empresarial, frota, outros.'),
    )

    class Meta:
        model = Branch
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4,
                                                 'placeholder': _('Descrição livre do ramo de seguro.')}),
        }
        labels = {
            'description': _('Descrição'),
        }


class CoverageForm(forms.ModelForm):
    """ModelForm for creating/updating a tenanted ``Coverage``.

    The ``branch`` field queryset is restricted to the current tenant from the
    view via ``TenantFormMixin.restrict_form_choices`` (see ``base.views``).
    """

    class Meta:
        model = Coverage
        fields = ['branch', 'name', 'description']
        widgets = {
            'branch': forms.Select(attrs={'class': 'select'}),
            'name': forms.TextInput(attrs={'autocomplete': 'off',
                                           'placeholder': _('Nome da cobertura')}),
            'description': forms.Textarea(attrs={'rows': 4,
                                                 'placeholder': _('Descrição livre da cobertura.')}),
        }
        labels = {
            'branch': _('Ramo'),
            'name': _('Nome'),
            'description': _('Descrição'),
        }