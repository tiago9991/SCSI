from django.db import models
from django.utils.translation import gettext_lazy as _

from base.models import BaseCoveredItem, BaseTenantModel


class Policy(BaseTenantModel):
    """Tenanted insurance policy.

    Per PRD §16.6: holds number, vigência (start/end), premium and status. May
    originate from a ``proposal`` (Sprint 12 "Gerar apólice") or be created
    standalone. Covered items (the Sprint 9 focus) attach 1:N via
    ``PolicyCoveredItem``; endossos and renovações land in Sprint 18 / Sprint 17.

    Status options: vigente (ativa), vencida, cancelada, suspensa, rascunho.
    """

    STATUS_DRAFT = 'rascunho'
    STATUS_ACTIVE = 'vigente'
    STATUS_EXPIRED = 'vencida'
    STATUS_CANCELED = 'cancelada'
    STATUS_SUSPENDED = 'suspensa'

    STATUS_CHOICES = [
        (STATUS_DRAFT, _('Rascunho')),
        (STATUS_ACTIVE, _('Vigente')),
        (STATUS_EXPIRED, _('Vencida')),
        (STATUS_CANCELED, _('Cancelada')),
        (STATUS_SUSPENDED, _('Suspensa')),
    ]

    proposal = models.ForeignKey(
        'proposals.Proposal',
        on_delete=models.SET_NULL,
        related_name='policies',
        verbose_name=_('proposta'),
        null=True,
        blank=True,
        help_text=_('Proposta que originou a apólice, quando aplicável.'),
    )
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.PROTECT,
        related_name='policies',
        verbose_name=_('cliente'),
    )
    insurance_company = models.ForeignKey(
        'catalog.InsuranceCompany',
        on_delete=models.PROTECT,
        related_name='policies',
        verbose_name=_('seguradora'),
    )
    branch = models.ForeignKey(
        'catalog.Branch',
        on_delete=models.PROTECT,
        related_name='policies',
        verbose_name=_('ramo'),
    )
    number = models.CharField(
        _('número'),
        max_length=64,
        blank=True,
        help_text=_('Número da apólice definido pela seguradora.'),
    )
    start_date = models.DateField(_('início da vigência'), null=True, blank=True)
    end_date = models.DateField(_('fim da vigência'), null=True, blank=True)
    premium = models.DecimalField(
        _('prêmio'),
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
    )
    status = models.CharField(
        _('status'),
        max_length=32,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
    )
    ai_summary = models.TextField(_('resumo com IA'), blank=True, null=True)

    class Meta:
        verbose_name = _('apólice')
        verbose_name_plural = _('apólices')
        ordering = ('-id',)
        indexes = [
            models.Index(fields=('brokerage', 'id')),
            models.Index(fields=('brokerage', 'status')),
            models.Index(fields=('brokerage', 'number')),
        ]

    def __str__(self):
        return f'{self.number or f"#{self.pk}"} · {self.client}'


class PolicyCoveredItem(BaseCoveredItem):
    """Tenanted covered item attached to a policy (Sprint 9).

    Per PRD §16.6 / §20.4: mirrors ``ProposalCoveredItem`` but bound to a
    ``Policy``. During the "Gerar apólice" flow (Sprint 12) the proposal's
    covered items are copied here. A ``Claim`` (Sprint 13) always references a
    ``PolicyCoveredItem``.
    """

    policy = models.ForeignKey(
        Policy,
        on_delete=models.CASCADE,
        related_name='covered_items',
        verbose_name=_('apólice'),
    )

    class Meta:
        verbose_name = _('item coberto da apólice')
        verbose_name_plural = _('itens cobertos da apólice')
        ordering = ('-id',)
        indexes = [
            models.Index(fields=('brokerage', 'id')),
            models.Index(fields=('brokerage', 'policy', 'id')),
        ]

    def __str__(self):
        return f'{self.kind_label} · {self.description or f"#{self.pk}"}'