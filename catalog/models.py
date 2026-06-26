from django.db import models
from django.utils.translation import gettext_lazy as _

from base.models import BaseTenantModel


class InsuranceCompany(BaseTenantModel):
    """Tenanted insurer (seguradora).

    Per PRD §16.4 / RF-SR-01: insurers are managed per brokerage and relate
    to proposals and policies downstream. Manual registration only — no
    external API integration (out of scope, see §6).
    """

    name = models.CharField(_('nome'), max_length=180)
    code = models.CharField(
        _('código'),
        max_length=64,
        blank=True,
        help_text=_('Código interno ou identificador da seguradora.'),
    )
    document = models.CharField(
        'CNPJ',
        max_length=32,
        blank=True,
        help_text=_('CNPJ da seguradora.'),
    )
    contact = models.CharField(
        _('contato'),
        max_length=255,
        blank=True,
        help_text=_('Descrição de contato (telefone/e-mail/representante).'),
    )

    class Meta:
        verbose_name = _('seguradora')
        verbose_name_plural = _('seguradoras')
        ordering = ('-id',)
        indexes = [
            models.Index(fields=('brokerage', 'id')),
            models.Index(fields=('brokerage', 'name')),
        ]

    def __str__(self):
        return self.name or f'#{self.pk}'


class Branch(BaseTenantModel):
    """Tenanted insurance branch (ramo de seguro).

    Per PRD §16.4 / RF-SR-02: examples — auto, residencial, vida, viagem,
    empresarial, frota, outros.
    """

    name = models.CharField(_('nome'), max_length=120)
    description = models.TextField(_('descrição'), blank=True)

    class Meta:
        verbose_name = _('ramo')
        verbose_name_plural = _('ramos')
        ordering = ('-id',)
        indexes = [
            models.Index(fields=('brokerage', 'id')),
            models.Index(fields=('brokerage', 'name')),
        ]

    def __str__(self):
        return self.name or f'#{self.pk}'


class Coverage(BaseTenantModel):
    """Tenanted coverage (cobertura) scoped by branch.

    Per PRD §16.4 / RF-SR-03: coverages belong to a branch and are referenced
    by proposals/policies items downstream.
    """

    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name='coverages',
        verbose_name=_('ramo'),
    )
    name = models.CharField(_('nome'), max_length=120)
    description = models.TextField(_('descrição'), blank=True)

    class Meta:
        verbose_name = _('cobertura')
        verbose_name_plural = _('coberturas')
        ordering = ('-id',)
        indexes = [
            models.Index(fields=('brokerage', 'id')),
            models.Index(fields=('brokerage', 'branch', 'id')),
        ]

    def __str__(self):
        return self.name or f'#{self.pk}'