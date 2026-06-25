from django.db import models
from django.utils.translation import gettext_lazy as _

from base.models import BaseTenantModel


class Client(BaseTenantModel):
    """Tenanted customer of a brokerage.

    Per PRD §16.3: holds identification, contact, address and free-form notes.
    ``ai_summary`` is the field populated by the "Resumir com IA" feature in
    Sprint 23; attachments land on the generic Attachment model in Sprint 14.
    """

    first_name = models.CharField(_('nome'), max_length=150)
    last_name = models.CharField(_('sobrenome'), max_length=150, blank=True)
    document = models.CharField(
        _('CPF/CNPJ'),
        max_length=32,
        blank=True,
        help_text=_('CPF ou CNPJ do cliente. Apenas um por cliente.'),
    )
    email = models.EmailField(_('e-mail'), blank=True)
    phone = models.CharField(_('telefone'), max_length=32, blank=True)
    birth_date = models.DateField(_('data de nascimento'), null=True, blank=True)
    address = models.CharField(_('endereço'), max_length=255, blank=True)
    notes = models.TextField(_('observações'), blank=True)
    ai_summary = models.TextField(_('resumo com IA'), blank=True, null=True)

    class Meta:
        verbose_name = _('cliente')
        verbose_name_plural = _('clientes')
        ordering = ('-id',)
        indexes = [
            models.Index(fields=('brokerage', 'id')),
            models.Index(fields=('brokerage', 'last_name', 'first_name')),
        ]

    def __str__(self):
        full = f'{self.first_name} {self.last_name}'.strip()
        return f'{full} ({self.document})' if self.document else full or f'#{self.pk}'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()