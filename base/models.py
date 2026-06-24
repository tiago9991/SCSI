from django.db import models

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
