"""Class Based Views for the ``policies`` app.

All views inherit from :class:`TenantViewMixin` (see ``base.views``) so the
queryset, form FK choices and single-object fetches are automatically scoped to
``request.tenant`` — data of another brokerage is never reachable.

Sprint 11 implements the Policy CRUD plus the Covered Item CRUD nested under
each policy (1:N). The "Gerar apólice" flow (Sprint 12) is handled there.

Sprint 17 (Renovações) and Sprint 18 (Endossos) add their own CRUD nested
under a policy, mirroring the covered-item pattern; renovações also expose a
top-level list with 30/60/90-day alerts (PRD §8.8 / §9.10).
"""
from datetime import timedelta

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from base.views import TenantViewMixin
from policies.forms import (
    EndorsementForm,
    PolicyCoveredItemForm,
    PolicyForm,
    RenewalForm,
    RenewalNestedForm,
)
from policies.models import Endorsement, Policy, PolicyCoveredItem, Renewal


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
        # Endorsements (Sprint 18).
        ctx['endorsements'] = (
            self.object.endorsements.for_tenant(self.request.tenant).order_by('-effective_date', '-id')
        )
        ctx['endorsement_create_url'] = reverse_lazy('policies:endorsement_create', args=[self.object.pk])
        # Renewals (Sprint 17).
        ctx['renewals'] = (
            self.object.renewals.for_tenant(self.request.tenant).order_by('due_date', '-id')
        )
        ctx['renewal_create_url'] = reverse_lazy('policies:renewal_create', args=[self.object.pk])
        # Attachments panel (Sprint 14).
        from attachments.utils import attachments_context
        att_ctx = attachments_context(self.object, self.request.tenant)
        ctx['attachments'] = att_ctx['attachments']
        ctx['upload_url'] = att_ctx['attachments_upload_url']
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


# ---------------------------------------------------------------------------
# Endorsement (Sprint 18 — PRD §16.6 / §9.11) — nested under a policy (1:N)
# ---------------------------------------------------------------------------
class EndorsementCreateView(TenantViewMixin, CreateView):
    """Add an endorsement to a policy (1:N)."""

    model = Endorsement
    form_class = EndorsementForm
    template_name = 'policies/endorsement_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.policy = get_object_or_404(
            Policy.objects.for_tenant(request.tenant), pk=kwargs['policy_pk']
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Novo endosso')
        ctx['policy'] = self.policy
        ctx['list_url'] = reverse_lazy('policies:policy_detail', args=[self.policy.pk])
        ctx['submit_label'] = _('Criar endosso')
        return ctx

    def form_valid(self, form):
        form.instance.policy = self.policy
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('policies:policy_detail', args=[self.policy.pk])


class EndorsementUpdateView(TenantViewMixin, UpdateView):
    """Edit an endorsement — constrained to the policy in the URL."""

    model = Endorsement
    form_class = EndorsementForm
    template_name = 'policies/endorsement_form.html'

    def get_queryset(self):
        qs = super().get_queryset().filter(policy_id=self.kwargs['policy_pk'])
        return qs.select_related('policy')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Editar endosso')
        ctx['policy'] = self.object.policy
        ctx['list_url'] = reverse_lazy('policies:policy_detail', args=[self.object.policy_id])
        ctx['submit_label'] = _('Salvar alterações')
        return ctx

    def get_success_url(self):
        return reverse_lazy('policies:policy_detail', args=[self.object.policy_id])


class EndorsementDeleteView(TenantViewMixin, DeleteView):
    """Confirm delete of an endorsement — constrained to the policy in the URL."""

    model = Endorsement
    template_name = 'policies/endorsement_confirm_delete.html'

    def get_queryset(self):
        return super().get_queryset().filter(policy_id=self.kwargs['policy_pk'])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Excluir endosso')
        ctx['policy'] = self.object.policy
        ctx['list_url'] = reverse_lazy('policies:policy_detail', args=[self.object.policy_id])
        return ctx

    def get_success_url(self):
        return reverse_lazy('policies:policy_detail', args=[self.object.policy_id])


# ---------------------------------------------------------------------------
# Renewal (Sprint 17 — PRD §16.6 / §8.8 / §9.10) — top-level list + nested CRUD
# ---------------------------------------------------------------------------
class RenewalListView(TenantViewMixin, ListView):
    """Paginated list of renewals with status and 30/60/90-day alerts.

    ``?days=30|60|90`` filters renewals due within the next N days (alertas
    de renovações próximas, PRD §9.10 / §8.8). Empty / pending / in-progress
    statuses are surfaced by default so the corretora can act on them.
    """

    model = Renewal
    template_name = 'policies/renewal_list.html'
    context_object_name = 'renewals'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset().select_related('policy', 'policy__client', 'policy__insurance_company')
        search = (self.request.GET.get('q') or '').strip()
        if search:
            qs = qs.filter(
                Q(policy__number__icontains=search)
                | Q(policy__client__first_name__icontains=search)
                | Q(policy__client__last_name__icontains=search)
                | Q(policy__client__document__icontains=search)
                | Q(notes__icontains=search)
            )
        status = (self.request.GET.get('status') or '').strip()
        if status:
            qs = qs.filter(status=status)
        days = (self.request.GET.get('days') or '').strip()
        if days in ('30', '60', '90'):
            today = timezone.localdate()
            limit = today + timedelta(days=int(days))
            qs = qs.filter(due_date__lte=limit, due_date__gte=today)
        return qs.order_by('due_date', '-id')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        today = timezone.localdate()
        # Alert counts for 30/60/90 badges (active renewals due within the window).
        base = Renewal.objects.for_tenant(tenant).filter(
            due_date__gte=today
        ).exclude(status__in=[Renewal.STATUS_RENEWED, Renewal.STATUS_CANCELED])
        ctx['search'] = self.request.GET.get('q', '')
        ctx['selected_status'] = self.request.GET.get('status', '')
        ctx['selected_days'] = self.request.GET.get('days', '')
        ctx['status_choices'] = Renewal.STATUS_CHOICES
        ctx['alert_30'] = base.filter(due_date__lte=today + timedelta(days=30)).count()
        ctx['alert_60'] = base.filter(due_date__lte=today + timedelta(days=60)).count()
        ctx['alert_90'] = base.filter(due_date__lte=today + timedelta(days=90)).count()
        ctx['page_title'] = _('Renovações')
        ctx['create_url'] = reverse_lazy('policies:renewal_create_top')
        return ctx


class RenewalDetailView(TenantViewMixin, DetailView):
    """Detail page for a single renewal."""

    model = Renewal
    template_name = 'policies/renewal_detail.html'
    context_object_name = 'renewal'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = str(self.object)
        ctx['list_url'] = reverse_lazy('policies:renewal_list')
        ctx['update_url'] = reverse_lazy('policies:renewal_update', args=[self.object.pk])
        ctx['delete_url'] = reverse_lazy('policies:renewal_delete', args=[self.object.pk])
        return ctx


class RenewalCreateView(TenantViewMixin, CreateView):
    """Create a renewal. The ``policy`` may be pre-selected via ``?policy=``.

    When ``policy_pk`` is in the URL (nested flow under a policy), the
    ``RenewalNestedForm`` is used and ``policy`` is stamped from the URL. When
    reached from the top-level list, the full ``RenewalForm`` (with a
    tenant-scoped ``policy`` select) is rendered.
    """

    model = Renewal
    template_name = 'policies/renewal_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.policy = None
        policy_pk = kwargs.get('policy_pk') or request.GET.get('policy')
        if policy_pk:
            self.policy = get_object_or_404(
                Policy.objects.for_tenant(request.tenant), pk=policy_pk
            )
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        return RenewalNestedForm if self.policy is not None else RenewalForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.policy is None:
            self.restrict_form_choices(form)
            # Pre-select policy when arriving via ?policy=.
            policy_pk = self.request.GET.get('policy')
            if policy_pk and form.fields.get('policy'):
                form.fields['policy'].initial = policy_pk
        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Nova renovação')
        ctx['policy'] = self.policy
        ctx['list_url'] = reverse_lazy('policies:renewal_list')
        ctx['submit_label'] = _('Criar renovação')
        return ctx

    def form_valid(self, form):
        if self.policy is not None:
            form.instance.policy = self.policy
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('policies:renewal_detail', args=[self.object.pk])


class RenewalUpdateView(TenantViewMixin, UpdateView):
    model = Renewal
    form_class = RenewalForm
    template_name = 'policies/renewal_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Editar renovação')
        ctx['list_url'] = reverse_lazy('policies:renewal_list')
        ctx['submit_label'] = _('Salvar alterações')
        return ctx

    def get_success_url(self):
        return reverse_lazy('policies:renewal_detail', args=[self.object.pk])


class RenewalDeleteView(TenantViewMixin, DeleteView):
    model = Renewal
    template_name = 'policies/renewal_confirm_delete.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Excluir renovação')
        ctx['list_url'] = reverse_lazy('policies:renewal_list')
        ctx['detail_url'] = reverse_lazy('policies:renewal_detail', args=[self.object.pk])
        return ctx

    def get_success_url(self):
        return reverse_lazy('policies:renewal_list')