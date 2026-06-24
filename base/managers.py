from django.db import models


class TenantQuerySet(models.QuerySet):
    """QuerySet que filtra registros por corretora (tenant)."""

    def for_tenant(self, brokerage):
        return self.filter(brokerage=brokerage)


class TenantManager(models.Manager):
    """Manager que expoe o TenantQuerySet e o filtro por tenant."""

    def get_queryset(self):
        return TenantQuerySet(self.model, using=self._db)

    def for_tenant(self, brokerage):
        return self.get_queryset().for_tenant(brokerage)
