"""Class Based Views for the ``clients`` app.

All views inherit from :class:`TenantViewMixin` (see ``base.views``) so the
queryset and form instance are automatically scoped to ``request.tenant`` --
data of another brokerage is never reachable.
"""
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from base.views import TenantViewMixin
from clients.forms import ClientForm
from clients.models import Client


class ClientListView(TenantViewMixin, ListView):
    """Paginated list of clients with search and quick filters."""

    model = Client
    template_name = 'clients/client_list.html'
    context_object_name = 'clients'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset()
        # Search term: matches name, document, email and phone (case-insensitive).
        search = (self.request.GET.get('q') or '').strip()
        if search:
            qs = qs.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(document__icontains=search)
                | Q(email__icontains=search)
                | Q(phone__icontains=search)
            )

        # Optional quick filter by initial letter of last_name (A-Z bar).
        letter = (self.request.GET.get('letter') or '').strip().upper()
        if len(letter) == 1 and letter.isalpha():
            qs = qs.filter(last_name__istartswith=letter)

        return qs.order_by('-id')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search'] = self.request.GET.get('q', '')
        ctx['letter'] = (self.request.GET.get('letter') or '').strip().upper()
        ctx['page_title'] = _('Clientes')
        ctx['create_url'] = reverse_lazy('clients:client_create')
        return ctx


class ClientDetailView(TenantViewMixin, DetailView):
    """Detail page for a single client.

    Includes the placeholder section for "Resumir com IA" (active in Sprint 23)
    and an attachments placeholder (live in Sprint 14).
    """

    model = Client
    template_name = 'clients/client_detail.html'
    context_object_name = 'client'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = self.object.full_name
        ctx['list_url'] = reverse_lazy('clients:client_list')
        ctx['update_url'] = reverse_lazy('clients:client_update', args=[self.object.pk])
        ctx['delete_url'] = reverse_lazy('clients:client_delete', args=[self.object.pk])
        # Attachments panel (Sprint 14).
        from attachments.utils import attachments_context
        att_ctx = attachments_context(self.object, self.request.tenant)
        ctx['attachments'] = att_ctx['attachments']
        ctx['upload_url'] = att_ctx['attachments_upload_url']
        return ctx


class ClientCreateView(TenantViewMixin, CreateView):
    """Create a new client (brokerage stamped by TenantFormMixin)."""

    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Novo cliente')
        ctx['list_url'] = reverse_lazy('clients:client_list')
        ctx['submit_label'] = _('Criar cliente')
        return ctx

    def get_success_url(self):
        return reverse_lazy('clients:client_detail', args=[self.object.pk])


class ClientUpdateView(TenantViewMixin, UpdateView):
    """Edit an existing client (tenant-scoped via TenantObjectMixin)."""

    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Editar cliente')
        ctx['list_url'] = reverse_lazy('clients:client_list')
        ctx['submit_label'] = _('Salvar alterações')
        return ctx

    def get_success_url(self):
        return reverse_lazy('clients:client_detail', args=[self.object.pk])


class ClientDeleteView(TenantViewMixin, DeleteView):
    """Confirm delete of a client (tenant-scoped)."""

    model = Client
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('clients:client_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Excluir cliente')
        ctx['list_url'] = reverse_lazy('clients:client_list')
        ctx['detail_url'] = reverse_lazy('clients:client_detail', args=[self.object.pk])
        return ctx