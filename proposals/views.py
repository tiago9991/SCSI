"""Class Based Views for the ``proposals`` app.

All views inherit from :class:`TenantViewMixin` (see ``base.views``) so the
queryset, form FK choices and single-object fetches are automatically scoped to
``request.tenant`` — data of another brokerage is never reachable.

Sprint 10 implements the Proposal CRUD plus the Covered Item CRUD nested under
each proposal (1:N). The ``producer`` FK (commercial.Producer, PRD §16.5) is not
rendered yet — it lands in Sprint 19 once the ``commercial`` app is created.
"""
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from base.views import TenantViewMixin
from proposals.forms import ProposalCoveredItemForm, ProposalForm
from proposals.models import Proposal, ProposalCoveredItem


# ---------------------------------------------------------------------------
# Proposal
# ---------------------------------------------------------------------------
class ProposalListView(TenantViewMixin, ListView):
    """Paginated list of proposals with search and status filter."""

    model = Proposal
    template_name = 'proposals/proposal_list.html'
    context_object_name = 'proposals'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset().select_related('client', 'insurance_company', 'branch')
        search = (self.request.GET.get('q') or '').strip()
        if search:
            qs = qs.filter(
                Q(client__first_name__icontains=search)
                | Q(client__last_name__icontains=search)
                | Q(client__document__icontains=search)
                | Q(insurance_company__name__icontains=search)
                | Q(notes__icontains=search)
            )
        status = (self.request.GET.get('status') or '').strip()
        if status:
            qs = qs.filter(status=status)
        return qs.order_by('-id')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search'] = self.request.GET.get('q', '')
        ctx['selected_status'] = self.request.GET.get('status', '')
        ctx['status_choices'] = Proposal.STATUS_CHOICES
        ctx['page_title'] = _('Propostas')
        ctx['create_url'] = reverse_lazy('proposals:proposal_create')
        return ctx


class ProposalDetailView(TenantViewMixin, DetailView):
    """Detail page for a single proposal — lists its covered items (1:N)."""

    model = Proposal
    template_name = 'proposals/proposal_detail.html'
    context_object_name = 'proposal'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = str(self.object)
        ctx['list_url'] = reverse_lazy('proposals:proposal_list')
        ctx['update_url'] = reverse_lazy('proposals:proposal_update', args=[self.object.pk])
        ctx['delete_url'] = reverse_lazy('proposals:proposal_delete', args=[self.object.pk])
        ctx['covered_items'] = (
            self.object.covered_items.for_tenant(self.request.tenant).order_by('-id')
        )
        ctx['item_create_url'] = reverse_lazy('proposals:covereditem_create', args=[self.object.pk])
        return ctx


class ProposalCreateView(TenantViewMixin, CreateView):
    model = Proposal
    form_class = ProposalForm
    template_name = 'proposals/proposal_form.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        self.restrict_form_choices(form)
        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Nova proposta')
        ctx['list_url'] = reverse_lazy('proposals:proposal_list')
        ctx['submit_label'] = _('Criar proposta')
        return ctx

    def get_success_url(self):
        return reverse_lazy('proposals:proposal_detail', args=[self.object.pk])


class ProposalUpdateView(TenantViewMixin, UpdateView):
    model = Proposal
    form_class = ProposalForm
    template_name = 'proposals/proposal_form.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        self.restrict_form_choices(form)
        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Editar proposta')
        ctx['list_url'] = reverse_lazy('proposals:proposal_list')
        ctx['submit_label'] = _('Salvar alterações')
        return ctx

    def get_success_url(self):
        return reverse_lazy('proposals:proposal_detail', args=[self.object.pk])


class ProposalDeleteView(TenantViewMixin, DeleteView):
    model = Proposal
    template_name = 'proposals/proposal_confirm_delete.html'
    success_url = reverse_lazy('proposals:proposal_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Excluir proposta')
        ctx['list_url'] = reverse_lazy('proposals:proposal_list')
        ctx['detail_url'] = reverse_lazy('proposals:proposal_detail', args=[self.object.pk])
        return ctx


# ---------------------------------------------------------------------------
# ProposalCoveredItem (nested under a proposal — 1:N)
# ---------------------------------------------------------------------------
class ProposalCoveredItemCreateView(TenantViewMixin, CreateView):
    """Add a covered item to a proposal (1:N).

    The parent ``proposal`` is resolved from the URL and validated against the
    current tenant before stamping the new item in ``form_valid``.
    """

    model = ProposalCoveredItem
    form_class = ProposalCoveredItemForm
    template_name = 'proposals/covereditem_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.proposal = get_object_or_404(
            Proposal.objects.for_tenant(request.tenant), pk=kwargs['proposal_pk']
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Novo item coberto')
        ctx['proposal'] = self.proposal
        ctx['list_url'] = reverse_lazy('proposals:proposal_detail', args=[self.proposal.pk])
        ctx['submit_label'] = _('Criar item coberto')
        return ctx

    def form_valid(self, form):
        form.instance.proposal = self.proposal
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('proposals:proposal_detail', args=[self.proposal.pk])


class ProposalCoveredItemUpdateView(TenantViewMixin, UpdateView):
    """Edit a covered item — also constrained to the proposal in the URL."""

    model = ProposalCoveredItem
    form_class = ProposalCoveredItemForm
    template_name = 'proposals/covereditem_form.html'

    def get_queryset(self):
        qs = super().get_queryset().filter(proposal_id=self.kwargs['proposal_pk'])
        return qs.select_related('proposal')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Editar item coberto')
        ctx['proposal'] = self.object.proposal
        ctx['list_url'] = reverse_lazy('proposals:proposal_detail', args=[self.object.proposal_id])
        ctx['submit_label'] = _('Salvar alterações')
        return ctx

    def get_success_url(self):
        return reverse_lazy('proposals:proposal_detail', args=[self.object.proposal_id])


class ProposalCoveredItemDeleteView(TenantViewMixin, DeleteView):
    """Confirm delete of a covered item — constrained to the proposal in the URL."""

    model = ProposalCoveredItem
    template_name = 'proposals/covereditem_confirm_delete.html'

    def get_queryset(self):
        return super().get_queryset().filter(proposal_id=self.kwargs['proposal_pk'])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Excluir item coberto')
        ctx['proposal'] = self.object.proposal
        ctx['list_url'] = reverse_lazy('proposals:proposal_detail', args=[self.object.proposal_id])
        return ctx

    def get_success_url(self):
        return reverse_lazy('proposals:proposal_detail', args=[self.object.proposal_id])