"""Forms for the ``attachments`` app.

The :class:`AttachmentForm`` validates uploaded files by extension/MIME
(whitelist of common document and image formats, PRD §9.9 / RF-AN-02) and by
size (configurable via ``settings.ATTACHMENT_MAX_UPLOAD_BYTES``, default 10 MB,
PRD §14.2). The parent relation (``content_type`` + ``object_id``) and the
tenant ``brokerage`` are stamped by the view from the resolved parent object,
so they are excluded from the rendered form.
"""
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from attachments.models import Attachment


# Whitelist of accepted file types (extension -> human label). Keep this list
# aligned with PRD §9.9 ("PDF, imagens, documentos comuns"). Adding new types
# is a one-line change here and is reflected in the upload accept attribute.
ALLOWED_FILE_TYPES = {
    'pdf': 'PDF',
    'jpg': 'Imagem JPEG',
    'jpeg': 'Imagem JPEG',
    'png': 'Imagem PNG',
    'gif': 'Imagem GIF',
    'webp': 'Imagem WebP',
    'svg': 'Imagem SVG',
    'doc': 'Documento Word',
    'docx': 'Documento Word',
    'xls': 'Planilha Excel',
    'xlsx': 'Planilha Excel',
    'ppt': 'Apresentação PowerPoint',
    'pptx': 'Apresentação PowerPoint',
    'txt': 'Texto',
    'csv': 'CSV',
    'zip': 'Arquivo ZIP',
}


def get_max_upload_bytes():
    """Return the configured max upload size in bytes (default 10 MB)."""
    return getattr(settings, 'ATTACHMENT_MAX_UPLOAD_BYTES', 10 * 1024 * 1024)


class AttachmentForm(forms.ModelForm):
    """ModelForm for uploading a single private attachment."""

    class Meta:
        model = Attachment
        fields = ['file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={
                'accept': ','.join(f'.{ext}' for ext in ALLOWED_FILE_TYPES),
            }),
        }
        labels = {
            'file': _('Arquivo'),
        }
        help_texts = {
            'file': _('PDF, imagens, documentos comuns e planilhas.'),
        }

    def clean_file(self):
        uploaded = self.cleaned_data.get('file')
        if not uploaded:
            return uploaded

        # --- Size validation (PRD §14.2) ---
        max_bytes = get_max_upload_bytes()
        if uploaded.size > max_bytes:
            max_mb = max_bytes / (1024 * 1024)
            raise ValidationError(
                _('O arquivo excede o tamanho máximo permitido de %(max).1f MB.') % {'max': max_mb}
            )

        # --- Type validation by extension (PRD §14.2) ---
        name = (uploaded.name or '').lower()
        ext = name.rsplit('.', 1)[-1] if '.' in name else ''
        if ext not in ALLOWED_FILE_TYPES:
            allowed = ', '.join(sorted(ALLOWED_FILE_TYPES))
            raise ValidationError(
                _('Tipo de arquivo não permitido: "%(ext)s". Aceitos: %(allowed)s.') % {
                    'ext': ext, 'allowed': allowed,
                }
            )

        # --- MIME sanity check (defence in depth) ---
        # We accept the extension as the primary signal (some clients send a
        # generic ``application/octet-stream`` MIME), but reject obvious
        # mismatches such as an .exe inside a .pdf extension.
        content_type = (uploaded.content_type or '').lower()
        if content_type and content_type in {
            'application/x-msdownload', 'application/x-executable',
            'application/x-dosexec', 'application/x-sh', 'application/x-bat',
        }:
            raise ValidationError(_('Tipo de arquivo não permitido.'))

        return uploaded