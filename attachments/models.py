"""Attachment model for private, tenant-scoped media (PRD §14 / §16.8).

The PRD explicitly allows either a generic ``content_type`` + ``object_id``
relation **or** FKs per entity — we go with the GenericFK approach since it
keeps a single table for all attachments (clients, proposals, policies and
claims) and is the option described in §16.8.

Isolation rules:
- ``brokerage`` is always stamped on the row for fast filter.
- The parent object's brokerage must match the attachment's brokerage; enforced
  in :meth:`Attachment.clean` and in the upload view.
- Only a known set of parent models ("attachment content") may be the target,
  declared in :data:`ATTACHABLE_MODELS`.
"""
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from base.models import BaseTenantModel


# Whitelist of parent models that may receive attachments (app_label.Model).
# Each entry maps to a human-readable verbose name used by the upload view.
ATTACHABLE_MODELS = {
    'clients.Client': _('Cliente'),
    'proposals.Proposal': _('Proposta'),
    'policies.Policy': _('Apólice'),
    'claims.Claim': _('Sinistro'),
}


def attachment_path(instance, filename):
    """Private storage path: ``attachments/<brokerage_id>/<ct>/<obj_id>/<file>``.

    Bucketed by brokerage so filesystem-level inspection and backups stay
    tenant-organized; the actual access control still happens in
    :class:`PrivateMediaView` (filenames never served directly).
    """
    brokerage_id = getattr(instance, 'brokerage_id', 0) or 0
    ct = instance.content_type_id or 0
    obj = instance.object_id or 0
    return f'attachments/{brokerage_id}/{ct}/{obj}/{filename}'


class Attachment(BaseTenantModel):
    """Tenanted attachment bound to any of the whitelisted parent models."""

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_('tipo do objeto'),
    )
    object_id = models.PositiveIntegerField(_('id do objeto'))
    content_object = GenericForeignKey('content_type', 'object_id')

    file = models.FileField(_('arquivo'), upload_to=attachment_path, max_length=500)
    name = models.CharField(_('nome'), max_length=255, help_text=_('Nome original do arquivo.'))
    mime = models.CharField(_('MIME'), max_length=255, blank=True)
    size = models.PositiveIntegerField(_('tamanho (bytes)'), default=0)

    class Meta:
        verbose_name = _('anexo')
        verbose_name_plural = _('anexos')
        ordering = ('-id',)
        indexes = [
            models.Index(fields=('brokerage', 'id')),
            models.Index(fields=('brokerage', 'content_type', 'object_id')),
        ]

    def __str__(self):
        return self.name or f'#{self.pk}'

    def clean(self):
        super().clean()
        # Enforce the parent whitelist.
        if self.content_type_id is None:
            return
        label = f'{self.content_type.app_label}.{self.content_type.model_class().__name__}' \
            if self.content_type.model_class() else None
        # ContentType.model is the lowercased model name; ContentType.app_label
        # is the app label. Reconstruct the canonical "app.Model" key using the
        # actual model class to be case-correct.
        model_cls = self.content_type.model_class()
        if model_cls is not None:
            label = f'{model_cls._meta.app_label}.{model_cls.__name__}'
        if label not in ATTACHABLE_MODELS:
            raise ValidationError(_('Este tipo de objeto não suporta anexos.'))
        # Enforce tenant match between the attachment and its parent.
        parent = self.content_object
        if parent is None:
            return
        parent_brokerage_id = getattr(parent, 'brokerage_id', None)
        if parent_brokerage_id is not None and parent_brokerage_id != self.brokerage_id:
            raise ValidationError(
                _('O anexo deve pertencer à mesma corretora do objeto pai.')
            )