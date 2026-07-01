"""CRM models: Pipeline, PipelineStage and Deal (PRD §16.9 / §19).

Each brokerage owns a ``Pipeline`` that groups ordered ``PipelineStage``s
(nome + cor, customizáveis). ``Deal`` (negociação) is the lead/oportunidade:
points to a ``Client``, sits on a ``PipelineStage``, carries value, expected
close date, status and an ``ai_summary`` placeholder (Sprint 23).

The ``producer`` FK (commercial.Producer, PRD §16.9) is nullable and is added
in Sprint 19 once the ``commercial`` app exists — until then it is omitted so
the migration graph stays valid (mirrors how ``proposals.Proposal`` handled
the same dependency).
"""
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from base.models import BaseTenantModel


HEX_COLOR_VALIDATOR = RegexValidator(
    regex=r'^#[0-9a-fA-F]{6}$',
    message=_('Informe uma cor hexadecimal no formato #RRGGBB.'),
)


class Pipeline(BaseTenantModel):
    """Tenanted pipeline (one per brokerage). PRD §16.9 / §19.1."""

    name = models.CharField(_('nome'), max_length=120)
    is_default = models.BooleanField(
        _('padrão'),
        default=False,
        help_text=_('Marque para usar este pipeline como padrão da corretora.'),
    )

    class Meta:
        verbose_name = _('pipeline')
        verbose_name_plural = _('pipelines')
        ordering = ('-id',)
        indexes = [
            models.Index(fields=('brokerage', 'id')),
        ]

    def __str__(self):
        return self.name or f'#{self.pk}'

    def save(self, *args, **kwargs):
        """Enforce a single default pipeline per brokerage.

        When this pipeline is flagged as default, any other default of the
        same brokerage is cleared first so the invariant holds.
        """
        if self.is_default:
            qs = Pipeline.objects.filter(brokerage=self.brokerage, is_default=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            qs.update(is_default=False)
        super().save(*args, **kwargs)


class PipelineStage(BaseTenantModel):
    """Ordered, named, colored stage of a pipeline. PRD §16.9 / §19.1.

    Stages are ordered within their pipeline by ``order``. Suggested default
    flow (PRD §19.1): Lead → Contato → Proposta → Negociação →
    Fechado/Ganho, Fechado/Perdido.
    """

    pipeline = models.ForeignKey(
        Pipeline,
        on_delete=models.CASCADE,
        related_name='stages',
        verbose_name=_('pipeline'),
    )
    name = models.CharField(_('nome'), max_length=120)
    color = models.CharField(
        _('cor'),
        max_length=7,
        default='#2563eb',
        validators=[HEX_COLOR_VALIDATOR],
        help_text=_('Cor hexadecimal (ex.: #2563eb).'),
    )
    order = models.PositiveIntegerField(_('ordem'), default=0)

    class Meta:
        verbose_name = _('etapa do pipeline')
        verbose_name_plural = _('etapas do pipeline')
        ordering = ('order', 'id')
        indexes = [
            models.Index(fields=('brokerage', 'id')),
            models.Index(fields=('brokerage', 'pipeline', 'order')),
        ]

    def __str__(self):
        return f'{self.pipeline} · {self.name}'


class Deal(BaseTenantModel):
    """Tenanted commercial deal (negociação). PRD §16.9 / §19.3.

    The ``producer`` FK (commercial.Producer, nullable per PRD §16.9) links the
    deal to the corretor responsible. ``ai_summary`` is populated by the
    "Resumir com IA" feature in Sprint 23.
    """

    STATUS_OPEN = 'aberta'
    STATUS_WON = 'ganha'
    STATUS_LOST = 'perdida'
    STATUS_ABANDONED = 'abandonada'

    STATUS_CHOICES = [
        (STATUS_OPEN, _('Aberta')),
        (STATUS_WON, _('Ganha')),
        (STATUS_LOST, _('Perdida')),
        (STATUS_ABANDONED, _('Abandonada')),
    ]

    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.PROTECT,
        related_name='deals',
        verbose_name=_('cliente'),
    )
    stage = models.ForeignKey(
        PipelineStage,
        on_delete=models.PROTECT,
        related_name='deals',
        verbose_name=_('etapa'),
    )
    producer = models.ForeignKey(
        'commercial.Producer',
        on_delete=models.SET_NULL,
        related_name='deals',
        verbose_name=_('produtor'),
        null=True,
        blank=True,
    )
    title = models.CharField(_('título'), max_length=200)
    amount = models.DecimalField(
        _('valor'),
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
    )
    expected_close_date = models.DateField(_('fechamento previsto'), null=True, blank=True)
    status = models.CharField(
        _('status'),
        max_length=32,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
    )
    ai_summary = models.TextField(_('resumo com IA'), blank=True, null=True)

    class Meta:
        verbose_name = _('negociação')
        verbose_name_plural = _('negociações')
        ordering = ('-id',)
        indexes = [
            models.Index(fields=('brokerage', 'id')),
            models.Index(fields=('brokerage', 'status')),
            models.Index(fields=('brokerage', 'stage', 'id')),
        ]

    def __str__(self):
        return self.title or f'#{self.pk}'