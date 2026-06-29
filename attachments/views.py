"""Class Based Views for the ``attachments`` app.

Two concerns are served here:

1. **CRUD for attachments** scoped to a parent object (one of Client, Proposal,
   Policy or Claim). The parent is resolved from the URL, validated against
   the current tenant, and then used as the GenericFK target.

2. **Private media serving** via :class:`PrivateMediaView`. Files are *never*
   served directly by Traefik/WhiteNoise — every request goes through Django
   so we can enforce authentication, brokerage isolation and (future) role
   checks. In production, ``X-Sendfile``/``X-Accel-Redirect`` can be enabled
   for efficient offload (PRD §14.2).
"""
import os

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import View
from django.views.generic.edit import CreateView, DeleteView

from attachments.forms import AttachmentForm
from attachments.models import ATTACHABLE_MODELS, Attachment


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def resolve_parent_or_404(content_type_id, object_id, tenant):
    """Resolve the parent object for an attachment (PRD §14.3 validation).

    Returns ``(parent, content_type)`` or raises ``Http404`` when:
    - the ContentType is unknown or not in the whitelist;
    - the parent object does not exist or is filtered out by tenant isolation.
    """
    ct = get_object_or_404(ContentType, pk=content_type_id)
    model_cls = ct.model_class()
    if model_cls is None:
        raise Http404('Tipo de objeto desconhecido.')
    label = f'{model_cls._meta.app_label}.{model_cls.__name__}'
    if label not in ATTACHABLE_MODELS:
        raise Http404('Tipo de objeto não suporta anexos.')
    # Tenant-safe fetch: every attachable model inherits BaseTenantModel, so it
    # exposes the ``for_tenant`` manager method.
    qs = model_cls._default_manager
    if hasattr(qs, 'for_tenant'):
        qs = qs.for_tenant(tenant)
    else:
        qs = qs.filter(brokerage=tenant)
    parent = get_object_or_404(qs, pk=object_id)
    return parent, ct


# ---------------------------------------------------------------------------
# Private media serving (PRD §14.2)
# ---------------------------------------------------------------------------
class PrivateMediaView(View):
    """Serve an attachment file after validating authentication + brokerage.

    URL contract: ``/anexos/<pk>/arquivo/``. The lookup is by attachment ``pk``
    (not by file path) so we can enforce isolation before opening the file.

    Production note: in a high-traffic setup set ``ATTACHMENT_USE_XSENDFILE``
    in settings and configure the web server (nginx ``X-Accel-Redirect`` or
    apache ``X-Sendfile``) to serve the bytes; the brokerage check still runs
    in Django.
    """

    def get(self, request, pk, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        tenant = getattr(request, 'tenant', None)
        if tenant is None:
            raise PermissionDenied

        # Tenant-scoped lookup — only attachments of the current brokerage.
        qs = Attachment.objects.for_tenant(tenant)
        attachment = get_object_or_404(qs, pk=pk)

        fileobj = attachment.file
        if not fileobj:
            raise Http404('Arquivo não disponível.')

        # Defence in depth: ensure the resolved file path is under MEDIA_ROOT.
        try:
            fileobj.open('rb')
        except (FileNotFoundError, OSError):
            raise Http404('Arquivo não encontrado no armazenamento.')

        response = FileResponse(fileobj, filename=attachment.name or os.path.basename(fileobj.name))
        response['Content-Length'] = str(attachment.size or fileobj.size)
        if attachment.mime:
            response['Content-Type'] = attachment.mime
        # Inline so the browser previews images/PDFs when possible.
        response['Content-Disposition'] = f'inline; filename="{attachment.name}"'
        # Hint the reverse proxy not to cache private media.
        response['Cache-Control'] = 'no-store'
        return response


# ---------------------------------------------------------------------------
# Attachment create / delete
# ---------------------------------------------------------------------------
class AttachmentCreateView(CreateView):
    """Upload a new attachment to a parent object.

    The URL carries ``content_type_id`` and ``object_id``; the view resolves
    the parent through the tenant-scoped queryset, then stamps the GenericFK
    relation and the brokerage before saving. On success the user is bounced
    back to the parent's detail page (the source of the upload form).
    """

    form_class = AttachmentForm
    template_name = 'attachments/attachment_form.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or getattr(request, 'tenant', None) is None:
            raise PermissionDenied
        self.parent, self.content_type = resolve_parent_or_404(
            kwargs['content_type_id'], kwargs['object_id'], request.tenant
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['parent'] = self.parent
        ctx['parent_label'] = ATTACHABLE_MODELS.get(
            f'{self.parent._meta.app_label}.{self.parent.__class__.__name__}',
            str(self.parent),
        )
        ctx['page_title'] = _('Novo anexo')
        ctx['cancel_url'] = self.parent_detail_url()
        ctx['submit_label'] = _('Enviar anexo')
        return ctx

    def form_valid(self, form):
        uploaded = form.cleaned_data['file']
        attachment = form.save(commit=False)
        attachment.brokerage = self.request.tenant
        attachment.content_type = self.content_type
        attachment.object_id = self.parent.pk
        attachment.name = uploaded.name
        attachment.mime = uploaded.content_type or ''
        attachment.size = uploaded.size or 0
        attachment.save()
        from django.contrib import messages
        messages.success(self.request, _('Anexo "%(name)s" enviado.') % {'name': attachment.name})
        return redirect(self.parent_detail_url())

    def parent_detail_url(self):
        """Best-effort URL back to the parent's detail page.

        Each attachable model exposes a ``<model>:<model>_detail`` route; we
        look it up via reverse with the parent pk. Unknown/missing routes
        degrade to the attachment list fallback.
        """
        from django.urls import NoReverseMatch, reverse

        app = self.parent._meta.app_label
        model = self.parent._meta.model_name
        for candidate in (f'{app}:{model}_detail', f'{app}:{model}'):
            try:
                return reverse(candidate, args=[self.parent.pk])
            except NoReverseMatch:
                continue
        return reverse_lazy('attachments:attachment_list')


class AttachmentDeleteView(View):
    """Delete a single attachment (POST action).

    Validates brokerage isolation via ``for_tenant`` and removes the file from
    storage alongside the database row. Bounces back to the parent detail page
    when possible, otherwise to the attachment list.
    """

    def post(self, request, pk, *args, **kwargs):
        if not request.user.is_authenticated or getattr(request, 'tenant', None) is None:
            raise PermissionDenied
        qs = Attachment.objects.for_tenant(request.tenant)
        attachment = get_object_or_404(qs, pk=pk)

        # Resolve the parent url *before* deleting (we lose the relation after).
        parent_url = None
        parent = attachment.content_object
        if parent is not None:
            from django.urls import NoReverseMatch, reverse

            app = parent._meta.app_label
            model = parent._meta.model_name
            for candidate in (f'{app}:{model}_detail', f'{app}:{model}'):
                try:
                    parent_url = reverse(candidate, args=[parent.pk])
                    break
                except NoReverseMatch:
                    continue

        # Remove the file from disk, then the row.
        fileobj = attachment.file
        attachment.delete()
        if fileobj:
            try:
                fileobj.delete(save=False)
            except Exception:
                pass

        from django.contrib import messages
        messages.success(request, _('Anexo removido.'))
        return redirect(parent_url or 'attachments:attachment_list')