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


class Endorsement(BaseTenantModel):
    """Tenanted endorsement bound to a policy (PRD §16.6 / §9.11 / Sprint 18).

    An endorsement (endosso) is an alteration to an existing ``Policy``: типа
    (type), descrição e data de eficácia. Endossos are always scoped to the
    brokerage of the parent policy via ``BaseTenantModel``.
    """

    TYPE_CHANGE = 'alteracao'
    TYPE_INCLUSION = 'inclusao'
    TYPE_EXCLUSION = 'exclusao'
    TYPE_CANCELLATION = 'cancelamento'
    TYPE_OTHER = 'outros'

    TYPE_CHOICES = [
        (TYPE_CHANGE, _('Alteração')),
        (TYPE_INCLUSION, _('Inclusão')),
        (TYPE_EXCLUSION, _('Exclusão')),
        (TYPE_CANCELLATION, _('Cancelamento')),
        (TYPE_OTHER, _('Outros')),
    ]

    policy = models.ForeignKey(
        Policy,
        on_delete=models.CASCADE,
        related_name='endorsements',
        verbose_name=_('apólice'),
    )
    number = models.CharField(
        _('número'),
        max_length=64,
        blank=True,
        help_text=_('Número do endosso definido pela seguradora.'),
    )
    type = models.CharField(
        _('tipo'),
        max_length=32,
        choices=TYPE_CHOICES,
        default=TYPE_CHANGE,
    )
    description = models.TextField(_('descrição'), blank=True)
    effective_date = models.DateField(_('data de eficácia'), null=True, blank=True)

    class Meta:
        verbose_name = _('endosso')
        verbose_name_plural = _('endossos')
        ordering = ('-id',)
        indexes = [
            models.Index(fields=('brokerage', 'id')),
            models.Index(fields=('brokerage', 'policy', 'id')),
            models.Index(fields=('brokerage', 'effective_date')),
        ]

    def __str__(self):
        return f'{self.number or f"#{self.pk}"} · {self.get_type_display()}'


class Renewal(BaseTenantModel):
    """Tenanted policy renewal (PRD §16.6 / §8.8 / §9.10 / Sprint 17).

    Tracks the renewal lifecycle of an existing ``Policy``: due date
    (``due_date``) and status. Alertas de renovações próximas (30/60/90 dias)
    are computed from ``due_date`` and surfaced in the renewal list (and later
    in the dashboard, Sprint 22).
    """

    STATUS_PENDING = 'pendente'
    STATUS_IN_PROGRESS = 'em_andamento'
    STATUS_RENEWED = 'renovada'
    STATUS_EXPIRED = 'vencida'
    STATUS_CANCELED = 'cancelada'

    STATUS_CHOICES = [
        (STATUS_PENDING, _('Pendente')),
        (STATUS_IN_PROGRESS, _('Em andamento')),
        (STATUS_RENEWED, _('Renovada')),
        (STATUS_EXPIRED, _('Vencida')),
        (STATUS_CANCELED, _('Cancelada')),
    ]

    policy = models.ForeignKey(
        Policy,
        on_delete=models.CASCADE,
        related_name='renewals',
        verbose_name=_('apólice'),
    )
    due_date = models.DateField(_('vencimento'), null=True, blank=True)
    status = models.CharField(
        _('status'),
        max_length=32,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    notes = models.TextField(_('observações'), blank=True)

    class Meta:
        verbose_name = _('renovação')
        verbose_name_plural = _('renovações')
        ordering = ('due_date', '-id')
        indexes = [
            models.Index(fields=('brokerage', 'id')),
            models.Index(fields=('brokerage', 'status')),
            models.Index(fields=('brokerage', 'due_date')),
            models.Index(fields=('brokerage', 'policy', 'id')),
        ]

    def __str__(self):
        return f'{self.policy} · {self.due_date or f"#{self.pk}"}'