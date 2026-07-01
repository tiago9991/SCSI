"""Commercial app models — Agent, Producer (PRD §16.10 / §21 / Sprint 19).

Hierarchy (PRD §21.1)::

    Brokerage
     ├── Agent (pessoa ou empresa parceira)
     │    └── Producer (corretor final)
     └── Producer (direto da corretora, sem agente)

Rules (PRD §21.2):
- Agente: pessoa ou empresa que vende para a corretora.
- Produtor: corretor final; pode trabalhar para um agente (``agent`` FK) ou
  diretamente para a corretora (``agent`` nullable).
- Um agente pode ter vários produtores (related_name='producers').

``Commission`` (PRD §16.10) lives here too and holds the brokerage / agent /
producer share split; its creation and screen land in Sprint 20.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _

from base.models import BaseTenantModel


class Agent(BaseTenantModel):
    """Tenanted commercial agent (parceiro pessoa/empresa). PRD §16.10 / §21.1."""

    TYPE_PERSON = 'pessoa'
    TYPE_COMPANY = 'empresa'

    TYPE_CHOICES = [
        (TYPE_PERSON, _('Pessoa')),
        (TYPE_COMPANY, _('Empresa')),
    ]

    name = models.CharField(_('nome'), max_length=200)
    document = models.CharField(_('documento'), max_length=32, blank=True)
    type = models.CharField(
        _('tipo'),
        max_length=16,
        choices=TYPE_CHOICES,
        default=TYPE_PERSON,
    )
    commission_percent = models.DecimalField(
        _('percentual de comissão'),
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text=_('Percentual de comissão do agente (0 a 100).'),
    )
    contact = models.CharField(_('contato'), max_length=200, blank=True)

    class Meta:
        verbose_name = _('agente')
        verbose_name_plural = _('agentes')
        ordering = ('-id',)
        indexes = [
            models.Index(fields=('brokerage', 'id')),
            models.Index(fields=('brokerage', 'name')),
        ]

    def __str__(self):
        return self.name or f'#{self.pk}'


class Producer(BaseTenantModel):
    """Tenanted commercial producer (corretor final). PRD §16.10 / §21.1.

    ``agent`` is nullable so a producer may work directly for the brokerage
    (PRD §21.2 "Produtor pode ser direto da corretora, sem agente"). When set,
    the producer belongs to the agent's hierarchy.
    """

    name = models.CharField(_('nome'), max_length=200)
    agent = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        related_name='producers',
        verbose_name=_('agente'),
        null=True,
        blank=True,
        help_text=_('Agente parceiro. Deixe em branco se o produtor é direto da corretora.'),
    )
    document = models.CharField(_('documento'), max_length=32, blank=True)
    commission_percent = models.DecimalField(
        _('percentual de comissão'),
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text=_('Percentual de comissão do produtor (0 a 100).'),
    )
    contact = models.CharField(_('contato'), max_length=200, blank=True)

    class Meta:
        verbose_name = _('produtor')
        verbose_name_plural = _('produtores')
        ordering = ('-id',)
        indexes = [
            models.Index(fields=('brokerage', 'id')),
            models.Index(fields=('brokerage', 'agent', 'id')),
        ]

    def __str__(self):
        return self.name or f'#{self.pk}'


class Commission(BaseTenantModel):
    """Tenanted commission record with share split. PRD §16.10 / §21.3.

    Bound to a ``policy`` (preferred) or a ``proposal`` — either is nullable so
    a manual commission can be registered without a policy in place. Shares are
    calculated by :func:`commercial.services.calculate_shares` from the
    configured percentuais of the brokerage / agent / producer.
    """

    amount = models.DecimalField(
        _('valor total'),
        max_digits=14,
        decimal_places=2,
        default=0,
    )
    policy = models.ForeignKey(
        'policies.Policy',
        on_delete=models.SET_NULL,
        related_name='commissions',
        verbose_name=_('apólice'),
        null=True,
        blank=True,
    )
    proposal = models.ForeignKey(
        'proposals.Proposal',
        on_delete=models.SET_NULL,
        related_name='commissions',
        verbose_name=_('proposta'),
        null=True,
        blank=True,
    )
    agent = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        related_name='commissions',
        verbose_name=_('agente'),
        null=True,
        blank=True,
    )
    producer = models.ForeignKey(
        Producer,
        on_delete=models.SET_NULL,
        related_name='commissions',
        verbose_name=_('produtor'),
        null=True,
        blank=True,
    )
    brokerage_share = models.DecimalField(
        _('repasse corretora'),
        max_digits=14,
        decimal_places=2,
        default=0,
    )
    agent_share = models.DecimalField(
        _('repasse agente'),
        max_digits=14,
        decimal_places=2,
        default=0,
    )
    producer_share = models.DecimalField(
        _('repasse produtor'),
        max_digits=14,
        decimal_places=2,
        default=0,
    )
    reference_date = models.DateField(
        _('data de referência'),
        null=True,
        blank=True,
        help_text=_('Data usada nos filtros por período da tela de comissões.'),
    )

    class Meta:
        verbose_name = _('comissão')
        verbose_name_plural = _('comissões')
        ordering = ('-id',)
        indexes = [
            models.Index(fields=('brokerage', 'id')),
            models.Index(fields=('brokerage', 'agent', 'id')),
            models.Index(fields=('brokerage', 'producer', 'id')),
            models.Index(fields=('brokerage', 'reference_date')),
        ]

    def __str__(self):
        return f'{self.amount} · {self.brokerage}'