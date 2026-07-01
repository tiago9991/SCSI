from django.db import models
from django.utils.translation import gettext_lazy as _

from base.models import BaseCoveredItem, BaseTenantModel


class Proposal(BaseTenantModel):
    """Tenanted insurance proposal.

    Per PRD §16.5: holds client, insurer, branch, producer and premium
    metadata; covered items (the Sprint 9 focus) attach 1:N via
    ``ProposalCoveredItem``. The ``producer`` FK to ``commercial.Producer`` is
    nullable per spec.

    Status flow (PRD §20.1): rascunho → enviada → (aceita | recusada) → expirada.
    The "Gerar apólice" action (Sprint 12) requires ``status=aceita``.
    """

    STATUS_DRAFT = 'rascunho'
    STATUS_SENT = 'enviada'
    STATUS_ACCEPTED = 'aceita'
    STATUS_REFUSED = 'recusada'
    STATUS_EXPIRED = 'expirada'

    STATUS_CHOICES = [
        (STATUS_DRAFT, _('Rascunho')),
        (STATUS_SENT, _('Enviada')),
        (STATUS_ACCEPTED, _('Aceita')),
        (STATUS_REFUSED, _('Recusada')),
        (STATUS_EXPIRED, _('Expirada')),
    ]

    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.PROTECT,
        related_name='proposals',
        verbose_name=_('cliente'),
    )
    insurance_company = models.ForeignKey(
        'catalog.InsuranceCompany',
        on_delete=models.PROTECT,
        related_name='proposals',
        verbose_name=_('seguradora'),
    )
    branch = models.ForeignKey(
        'catalog.Branch',
        on_delete=models.PROTECT,
        related_name='proposals',
        verbose_name=_('ramo'),
    )
    producer = models.ForeignKey(
        'commercial.Producer',
        on_delete=models.SET_NULL,
        related_name='proposals',
        verbose_name=_('produtor'),
        null=True,
        blank=True,
    )
    status = models.CharField(
        _('status'),
        max_length=32,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
    )
    valid_until = models.DateField(_('válido até'), null=True, blank=True)
    premium = models.DecimalField(
        _('prêmio'),
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
    )
    notes = models.TextField(_('observações'), blank=True)
    ai_summary = models.TextField(_('resumo com IA'), blank=True, null=True)

    class Meta:
        verbose_name = _('proposta')
        verbose_name_plural = _('propostas')
        ordering = ('-id',)
        indexes = [
            models.Index(fields=('brokerage', 'id')),
            models.Index(fields=('brokerage', 'status')),
        ]

    def __str__(self):
        return f'{self.pk} · {self.client} · {self.insurance_company}'


class ProposalCoveredItem(BaseCoveredItem):
    """Tenanted covered item attached to a proposal (Sprint 9).

    Per PRD §16.5 / §20.4: ``kind`` (auto, casa, frota, viagem, vida,
    empresarial, outros), ``description``, ``value`` and a flexible ``attributes``
    JSON payload (placa, endereço, lista de itens, destino, etc.). Relates 1:N
    with ``Proposal`` — when a policy is generated (Sprint 12) the items are
    copied to ``PolicyCoveredItem``.
    """

    proposal = models.ForeignKey(
        Proposal,
        on_delete=models.CASCADE,
        related_name='covered_items',
        verbose_name=_('proposta'),
    )

    class Meta:
        verbose_name = _('item coberto da proposta')
        verbose_name_plural = _('itens cobertos da proposta')
        ordering = ('-id',)
        indexes = [
            models.Index(fields=('brokerage', 'id')),
            models.Index(fields=('brokerage', 'proposal', 'id')),
        ]

    def __str__(self):
        return f'{self.kind_label} · {self.description or f"#{self.pk}"}'