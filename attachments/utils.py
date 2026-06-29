"""Helpers to integrate attachments into parent detail pages.

Each parent detail view (Client, Proposal, Policy, Claim) calls
:func:`attachments_context` from its ``get_context_data`` with the resolved
parent object to expose the tenant-scoped attachment queryset and the upload
URL expected by ``attachments/_attachments_panel.html``.
"""
from django.urls import reverse

from attachments.models import Attachment


def attachments_context(parent, tenant):
    """Return a context dict for the attachments panel of a parent object.

    Looks up attachments via the tenant-scoped queryset so a brokerage never
    sees another brokerage's files, and builds the upload URL from the parent's
    ContentType + pk. The parent must be one of the whitelisted attachable
    models (``ATTACHABLE_MODELS``).
    """
    from django.contrib.contenttypes.models import ContentType

    ct = ContentType.objects.get_for_model(parent)
    attachments = (
        Attachment.objects.for_tenant(tenant)
        .filter(content_type=ct, object_id=parent.pk)
        .order_by('-id')
    )
    upload_url = reverse(
        'attachments:attachment_create',
        args=[ct.pk, parent.pk],
    )
    return {
        'attachments': attachments,
        'attachments_upload_url': upload_url,
    }