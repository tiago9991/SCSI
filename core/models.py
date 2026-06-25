from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom user authenticating by email (no username).

    Multi-tenant user of SCSI. Belongs to exactly one brokerage (FK added in
    the multi-tenant sprint). Username field is removed in favour of a unique
    email, keeping the native Django auth backend and password flows.
    """

    username = None
    email = models.EmailField(_('e-mail'), unique=True)

    created_at = models.DateTimeField(_('criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('atualizado em'), auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('usuário')
        verbose_name_plural = _('usuários')
        ordering = ('-id',)

    def __str__(self):
        return self.email