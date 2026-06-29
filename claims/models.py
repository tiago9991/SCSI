from django.db import models
from django.utils.translation import gettext_lazy as _

from base.models import BaseTenantModel


class Claim(BaseTenantModel):
    """Tenanted insurance claim.

    Per PRD §16.7 / §20.5: a claim is always bound to a ``Policy`` **and** to a
    ``PolicyCoveredItem`` of that policy (the object actually being claimed).
    Status flow: aberto → em análise → (aprovado | recusado) → pago. Resumo com
    IA via ``ai_summary`` lands in Sprint 23 and anexos in Sprint 14.
    """

    STATUS_OPEN = 'aberto'
    STATUS_ANALYSIS = 'analise'
    STATUS_APPROVED = 'aprovado'
    STATUS_REFUSED = 'recusado'
    STATUS_PAID = 'pago'

    STATUS_CHOICES = [
        (STATUS_OPEN, _('Aberto')),
        (STATUS_ANALYSIS, _('Em análise')),
        (STATUS_APPROVED, _('Aprovado')),
        (STATUS_REFUSED, _('Recusado')),
        (STATUS_PAID, _('Pago')),
    ]

    policy = models.ForeignKey(
        'policies.Policy',
        on_delete=models.PROTECT,
        related_name='claims',
        verbose_name=_('apólice'),
    )
    covered_item = models.ForeignKey(
        'policies.PolicyCoveredItem',
        on_delete=models.PROTECT,
        related_name='claims',
        verbose_name=_('item coberto'),
    )
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.PROTECT,
        related_name='claims',
        verbose_name=_('cliente'),
    )
    number = models.CharField(
        _('número'),
        max_length=64,
        blank=True,
        help_text=_('Número do sinistro definido pela seguradora.'),
    )
    occurrence_date = models.DateField(_('data da ocorrência'), null=True, blank=True)
    description = models.TextField(_('descrição'), blank=True)
    status = models.CharField(
        _('status'),
        max_length=32,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
    )
    amount = models.DecimalField(
        _('valor'),
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
    )
    ai_summary = models.TextField(_('resumo com IA'), blank=True, null=True)

    class Meta:
        verbose_name = _('sinistro')
        verbose_name_plural = _('sinistros')
        ordering = ('-id',)
        indexes = [
            models.Index(fields=('brokerage', 'id')),
            models.Index(fields=('brokerage', 'status')),
            models.Index(fields=('brokerage', 'policy', 'id')),
        ]

    def __str__(self):
        return f'{self.number or f"#{self.pk}"} · {self.client}'