from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from base.models import TimeStampedModel
from core.managers import UserManager


class Plan(TimeStampedModel):
    """Subscription plan offered to brokerages (fictional; only `free` available initially).

    Per PRD RF-LP-03 / RF-BR-03: `free` is the only plan with `is_available=True`;
    paid plans (`pro`, `business`, ...) are displayed as "em breve" (coming soon)
    and remain blocked.
    """

    code = models.CharField(_('código'), max_length=32, unique=True)
    name = models.CharField(_('nome'), max_length=64)
    description = models.TextField(_('descrição'), blank=True)
    is_active = models.BooleanField(_('ativo'), default=True)
    is_available = models.BooleanField(_('disponível para cadastro'), default=False)

    class Meta:
        verbose_name = _('plano')
        verbose_name_plural = _('planos')
        ordering = ('id',)

    def __str__(self):
        return self.name


class Brokerage(TimeStampedModel):
    """Tenant of the system. Every domain entity is scoped by ``brokerage``.

    Per PRD RF-BR-02: ``legal_name`` (Razão Social) and ``cnpj`` are mandatory
    and unique. The chosen ``plan`` defaults to ``free`` during onboarding
    (Sprint 6).
    """

    name = models.CharField(_('nome fantasia'), max_length=120)
    legal_name = models.CharField(_('razão social'), max_length=180)
    cnpj = models.CharField('CNPJ', max_length=20, unique=True)
    email = models.EmailField(_('e-mail'), blank=True)
    phone = models.CharField(_('telefone'), max_length=32, blank=True)
    address = models.CharField(_('endereço'), max_length=255, blank=True)
    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name='brokerages',
        verbose_name=_('plano'),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _('corretora')
        verbose_name_plural = _('corretoras')
        ordering = ('-id',)

    def __str__(self):
        return f'{self.legal_name} ({self.cnpj})'


class User(AbstractUser):
    """Custom user authenticating by email (no username).

    Multi-tenant user of SCSI. Belongs to exactly one brokerage (FK added in
    the multi-tenant sprint). Username field is removed in favour of a unique
    email, keeping the native Django auth backend and password flows.

    ``brokerage`` is nullable so superusers / internal SCSI staff can exist
    before onboarding creates a brokerage; tenant-scoped views enforce it via
    ``TenantRequiredMixin`` in ``base.views``.
    """

    username = None
    email = models.EmailField(_('e-mail'), unique=True)

    brokerage = models.ForeignKey(
        Brokerage,
        on_delete=models.CASCADE,
        related_name='users',
        verbose_name=_('corretora'),
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(_('criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('atualizado em'), auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = _('usuário')
        verbose_name_plural = _('usuários')
        ordering = ('-id',)

    def __str__(self):
        return self.email