from django.db import models
from django.utils.translation import gettext_lazy as _

from base.managers import TenantManager


class TimeStampedModel(models.Model):
    """Model abstrato com campos de auditoria created_at e updated_at."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='atualizado em')

    class Meta:
        abstract = True


class BaseTenantModel(TimeStampedModel):
    """Model abstrato base para entidades multi-tenant (compartilhadas).

    Toda entidade de dominio herda desta classe, garantindo o isolamento
    por corretora via campo brokerage.
    """

    brokerage = models.ForeignKey(
        'core.Brokerage',
        on_delete=models.CASCADE,
        related_name='%(class)ss',
        verbose_name='corretora',
    )

    objects = TenantManager()

    class Meta:
        abstract = True


class BaseCoveredItem(BaseTenantModel):
    """Abstract base for ``ProposalCoveredItem`` and ``PolicyCoveredItem``.

    Per PRD Sprint 9 ("ou model reutilizável conforme design") the two covered
    item models share ``kind``, ``description``, ``value`` and a flexible
    ``attributes`` JSON field (placa, endereço, lista de itens, destino...).
    Concrete subclasses add the parent FK (``proposal`` or ``policy``) and
    keep the tenant isolation inherited from ``BaseTenantModel``.

    See PRD §16.5 / §16.6 / §20.4.
    """

    KIND_AUTO = 'auto'
    KIND_HOME = 'casa'
    KIND_FLEET = 'frota'
    KIND_TRAVEL = 'viagem'
    KIND_LIFE = 'vida'
    KIND_BUSINESS = 'empresarial'
    KIND_OTHER = 'outros'

    KIND_CHOICES = [
        (KIND_AUTO, _('Auto')),
        (KIND_HOME, _('Casa')),
        (KIND_FLEET, _('Frota')),
        (KIND_TRAVEL, _('Viagem')),
        (KIND_LIFE, _('Vida')),
        (KIND_BUSINESS, _('Empresarial')),
        (KIND_OTHER, _('Outros')),
    ]

    kind = models.CharField(
        _('tipo'),
        max_length=32,
        choices=KIND_CHOICES,
        default=KIND_OTHER,
        help_text=_('Objeto segurado: auto, casa, frota, viagem, vida, empresarial, outros.'),
    )
    description = models.CharField(
        _('descrição'),
        max_length=255,
        blank=True,
        help_text=_('Descrição livre do objeto segurado.'),
    )
    value = models.DecimalField(
        _('valor'),
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Valor do objeto segurado.'),
    )
    attributes = models.JSONField(
        _('atributos'),
        blank=True,
        default=dict,
        help_text=_('Atributos flexíveis em JSON (placa, endereço, lista de itens, destino, etc.).'),
    )

    class Meta:
        abstract = True

    @property
    def kind_label(self):
        """Human-readable label for the current ``kind``."""
        return dict(self.KIND_CHOICES).get(self.kind, self.kind)
