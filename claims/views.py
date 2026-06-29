"""Class Based Views for the ``claims`` app.

All views inherit from :class:`TenantViewMixin` (see ``base.views``) so the
queryset, form FK choices and single-object fetches are automatically scoped to
``request.tenant`` — data of another brokerage is never reachable.

Sprint 13 implements the Claim CRUD. Anexos (PRD §9.8 / Sprint 14) and resumo
com IA (PRD §9.8 / Sprint 23) are handled in their own sprints.
"""
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from base.views import TenantViewMixin
from claims.forms import ClaimForm
from claims.models import Claim
from policies.models import Policy, PolicyCoveredItem


class ClaimListView(TenantViewMixin, ListView):
    """Paginated list of claims with search and status filter."""

    model = Claim
    template_name = 'claims/claim_list.html'
    context_object_name = 'claims'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset().select_related(
            'policy', 'covered_item', 'client', 'policy__insurance_company',
        )
        search = (self.request.GET.get('q') or '').strip()
        if search:
            qs = qs.filter(
                Q(number__icontains=search)
                | Q(client__first_name__icontains=search)
                | Q(client__last_name__icontains=search)
                | Q(client__document__icontains=search)
                | Q(description__icontains=search)
                | Q(policy__number__icontains=search)
            )
        status = (self.request.GET.get('status') or '').strip()
        if status:
            qs = qs.filter(status=status)
        policy = (self.request.GET.get('policy') or '').strip()
        if policy:
            qs = qs.filter(policy_id=policy)
        return qs.order_by('-id')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search'] = self.request.GET.get('q', '')
        ctx['selected_status'] = self.request.GET.get('status', '')
        ctx['selected_policy'] = self.request.GET.get('policy', '')
        ctx['status_choices'] = Claim.STATUS_CHOICES
        ctx['page_title'] = _('Sinistros')
        ctx['create_url'] = reverse_lazy('claims:claim_create')
        return ctx


class ClaimDetailView(TenantViewMixin, DetailView):
    """Detail page for a single claim."""

    model = Claim
    template_name = 'claims/claim_detail.html'
    context_object_name = 'claim'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = str(self.object)
        ctx['list_url'] = reverse_lazy('claims:claim_list')
        ctx['update_url'] = reverse_lazy('claims:claim_update', args=[self.object.pk])
        ctx['delete_url'] = reverse_lazy('claims:claim_delete', args=[self.object.pk])
        # Attachments panel (Sprint 14).
        from attachments.utils import attachments_context
        att_ctx = attachments_context(self.object, self.request.tenant)
        ctx['attachments'] = att_ctx['attachments']
        ctx['upload_url'] = att_ctx['attachments_upload_url']
        return ctx


class ClaimCreateView(TenantViewMixin, CreateView):
    model = Claim
    form_class = ClaimForm
    template_name = 'claims/claim_form.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        self.restrict_form_choices(form)
        # When arriving from a policy (``?policy=``), pre-select that policy and
        # narrow the covered item choices to it for a smoother create flow.
        policy_pk = self.request.GET.get('policy') or self.request.POST.get('policy')
        if policy_pk:
            try:
                policy = Policy.objects.for_tenant(self.request.tenant).get(pk=policy_pk)
            except Policy.DoesNotExist:
                policy = None
            if policy is not None:
                form.fields['policy'].initial = policy.pk
                form.fields['covered_item'].queryset = (
                    PolicyCoveredItem.objects.for_tenant(self.request.tenant).filter(policy=policy)
                )
                form.fields['client'].initial = policy.client_id
        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Novo sinistro')
        ctx['list_url'] = reverse_lazy('claims:claim_list')
        ctx['submit_label'] = _('Criar sinistro')
        return ctx

    def get_success_url(self):
        return reverse_lazy('claims:claim_detail', args=[self.object.pk])


class ClaimUpdateView(TenantViewMixin, UpdateView):
    model = Claim
    form_class = ClaimForm
    template_name = 'claims/claim_form.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        self.restrict_form_choices(form)
        # Narrow covered item choices to the selected policy (or the current
        # claim's policy) so the field never presents items from another policy.
        policy = self.object.policy
        form.fields['covered_item'].queryset = (
            PolicyCoveredItem.objects.for_tenant(self.request.tenant).filter(policy=policy)
        )
        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Editar sinistro')
        ctx['list_url'] = reverse_lazy('claims:claim_list')
        ctx['submit_label'] = _('Salvar alterações')
        return ctx

    def get_success_url(self):
        return reverse_lazy('claims:claim_detail', args=[self.object.pk])


class ClaimDeleteView(TenantViewMixin, DeleteView):
    model = Claim
    template_name = 'claims/claim_confirm_delete.html'
    success_url = reverse_lazy('claims:claim_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Excluir sinistro')
        ctx['list_url'] = reverse_lazy('claims:claim_list')
        ctx['detail_url'] = reverse_lazy('claims:claim_detail', args=[self.object.pk])
        return ctx