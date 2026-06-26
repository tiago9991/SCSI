"""Class Based Views for the ``policies`` app.

All views inherit from :class:`TenantViewMixin` (see ``base.views``) so the
queryset, form FK choices and single-object fetches are automatically scoped to
``request.tenant`` — data of another brokerage is never reachable.

Sprint 11 implements the Policy CRUD plus the Covered Item CRUD nested under
each policy (1:N). The "Gerar apólice" flow (Sprint 12) and endossos / renovações
(Sprints 18 / 17) are handled in their own sprints.
"""
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from base.views import TenantViewMixin
from policies.forms import PolicyCoveredItemForm, PolicyForm
from policies.models import Policy, PolicyCoveredItem


# ---------------------------------------------------------------------------
# Policy
# ---------------------------------------------------------------------------
class PolicyListView(TenantViewMixin, ListView):
    """Paginated list of policies with search and status filter."""

    model = Policy
    template_name = 'policies/policy_list.html'
    context_object_name = 'policies'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset().select_related('client', 'insurance_company', 'branch', 'proposal')
        search = (self.request.GET.get('q') or '').strip()
        if search:
            qs = qs.filter(
                Q(number__icontains=search)
                | Q(client__first_name__icontains=search)
                | Q(client__last_name__icontains=search)
                | Q(client__document__icontains=search)
                | Q(insurance_company__name__icontains=search)
            )
        status = (self.request.GET.get('status') or '').strip()
        if status:
            qs = qs.filter(status=status)
        return qs.order_by('-id')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search'] = self.request.GET.get('q', '')
        ctx['selected_status'] = self.request.GET.get('status', '')
        ctx['status_choices'] = Policy.STATUS_CHOICES
        ctx['page_title'] = _('Apólices')
        ctx['create_url'] = reverse_lazy('policies:policy_create')
        return ctx


class PolicyDetailView(TenantViewMixin, DetailView):
    """Detail page for a single policy — lists its covered items (1:N)."""

    model = Policy
    template_name = 'policies/policy_detail.html'
    context_object_name = 'policy'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = str(self.object)
        ctx['list_url'] = reverse_lazy('policies:policy_list')
        ctx['update_url'] = reverse_lazy('policies:policy_update', args=[self.object.pk])
        ctx['delete_url'] = reverse_lazy('policies:policy_delete', args=[self.object.pk])
        ctx['covered_items'] = (
            self.object.covered_items.for_tenant(self.request.tenant).order_by('-id')
        )
        ctx['item_create_url'] = reverse_lazy('policies:covereditem_create', args=[self.object.pk])
        return ctx


class PolicyCreateView(TenantViewMixin, CreateView):
    model = Policy
    form_class = PolicyForm
    template_name = 'policies/policy_form.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        self.restrict_form_choices(form)
        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Nova apólice')
        ctx['list_url'] = reverse_lazy('policies:policy_list')
        ctx['submit_label'] = _('Criar apólice')
        return ctx

    def get_success_url(self):
        return reverse_lazy('policies:policy_detail', args=[self.object.pk])


class PolicyUpdateView(TenantViewMixin, UpdateView):
    model = Policy
    form_class = PolicyForm
    template_name = 'policies/policy_form.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        self.restrict_form_choices(form)
        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Editar apólice')
        ctx['list_url'] = reverse_lazy('policies:policy_list')
        ctx['submit_label'] = _('Salvar alterações')
        return ctx

    def get_success_url(self):
        return reverse_lazy('policies:policy_detail', args=[self.object.pk])


class PolicyDeleteView(TenantViewMixin, DeleteView):
    model = Policy
    template_name = 'policies/policy_confirm_delete.html'
    success_url = reverse_lazy('policies:policy_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Excluir apólice')
        ctx['list_url'] = reverse_lazy('policies:policy_list')
        ctx['detail_url'] = reverse_lazy('policies:policy_detail', args=[self.object.pk])
        return ctx


# ---------------------------------------------------------------------------
# PolicyCoveredItem (nested under a policy — 1:N)
# ---------------------------------------------------------------------------
class PolicyCoveredItemCreateView(TenantViewMixin, CreateView):
    """Add a covered item to a policy (1:N).

    The parent ``policy`` is resolved from the URL and validated against the
    current tenant before stamping the new item in ``form_valid``.
    """

    model = PolicyCoveredItem
    form_class = PolicyCoveredItemForm
    template_name = 'policies/covereditem_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.policy = get_object_or_404(
            Policy.objects.for_tenant(request.tenant), pk=kwargs['policy_pk']
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Novo item coberto')
        ctx['policy'] = self.policy
        ctx['list_url'] = reverse_lazy('policies:policy_detail', args=[self.policy.pk])
        ctx['submit_label'] = _('Criar item coberto')
        return ctx

    def form_valid(self, form):
        form.instance.policy = self.policy
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('policies:policy_detail', args=[self.policy.pk])


class PolicyCoveredItemUpdateView(TenantViewMixin, UpdateView):
    """Edit a covered item — also constrained to the policy in the URL."""

    model = PolicyCoveredItem
    form_class = PolicyCoveredItemForm
    template_name = 'policies/covereditem_form.html'

    def get_queryset(self):
        qs = super().get_queryset().filter(policy_id=self.kwargs['policy_pk'])
        return qs.select_related('policy')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Editar item coberto')
        ctx['policy'] = self.object.policy
        ctx['list_url'] = reverse_lazy('policies:policy_detail', args=[self.object.policy_id])
        ctx['submit_label'] = _('Salvar alterações')
        return ctx

    def get_success_url(self):
        return reverse_lazy('policies:policy_detail', args=[self.object.policy_id])


class PolicyCoveredItemDeleteView(TenantViewMixin, DeleteView):
    """Confirm delete of a covered item — constrained to the policy in the URL."""

    model = PolicyCoveredItem
    template_name = 'policies/covereditem_confirm_delete.html'

    def get_queryset(self):
        return super().get_queryset().filter(policy_id=self.kwargs['policy_pk'])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Excluir item coberto')
        ctx['policy'] = self.object.policy
        ctx['list_url'] = reverse_lazy('policies:policy_detail', args=[self.object.policy_id])
        return ctx

    def get_success_url(self):
        return reverse_lazy('policies:policy_detail', args=[self.object.policy_id])