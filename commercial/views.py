"""Class Based Views for the ``commercial`` app (Sprint 19 / Sprint 20).

All views inherit from :class:`TenantViewMixin` so the queryset, form FK
choices and single-object fetches are automatically scoped to
``request.tenant`` — data of another brokerage is never reachable.

Sprint 19 implements the Agent and Producer CRUDs; Sprint 20 adds the
Commission list (by período / agente / produtor) and CRUD with automated
share calculation.
"""
from django.db.models import Q, Sum
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from base.views import TenantViewMixin
from commercial.forms import AgentForm, CommissionForm, ProducerForm
from commercial.models import Agent, Commission, Producer


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------
class AgentListView(TenantViewMixin, ListView):
    model = Agent
    template_name = 'commercial/agent_list.html'
    context_object_name = 'agents'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset()
        search = (self.request.GET.get('q') or '').strip()
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(document__icontains=search) | Q(contact__icontains=search))
        atype = (self.request.GET.get('type') or '').strip()
        if atype:
            qs = qs.filter(type=atype)
        return qs.order_by('-id')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search'] = self.request.GET.get('q', '')
        ctx['selected_type'] = self.request.GET.get('type', '')
        ctx['type_choices'] = Agent.TYPE_CHOICES
        ctx['page_title'] = _('Agentes')
        ctx['create_url'] = reverse_lazy('commercial:agent_create')
        return ctx


class AgentDetailView(TenantViewMixin, DetailView):
    model = Agent
    template_name = 'commercial/agent_detail.html'
    context_object_name = 'agent'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = str(self.object)
        ctx['list_url'] = reverse_lazy('commercial:agent_list')
        ctx['update_url'] = reverse_lazy('commercial:agent_update', args=[self.object.pk])
        ctx['delete_url'] = reverse_lazy('commercial:agent_delete', args=[self.object.pk])
        ctx['producers'] = (
            self.object.producers.for_tenant(self.request.tenant).order_by('-id')
        )
        ctx['producer_create_url'] = reverse_lazy('commercial:producer_create') + f'?agent={self.object.pk}'
        return ctx


class AgentCreateView(TenantViewMixin, CreateView):
    model = Agent
    form_class = AgentForm
    template_name = 'commercial/agent_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Novo agente')
        ctx['list_url'] = reverse_lazy('commercial:agent_list')
        ctx['submit_label'] = _('Criar agente')
        return ctx

    def get_success_url(self):
        return reverse_lazy('commercial:agent_detail', args=[self.object.pk])


class AgentUpdateView(TenantViewMixin, UpdateView):
    model = Agent
    form_class = AgentForm
    template_name = 'commercial/agent_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Editar agente')
        ctx['list_url'] = reverse_lazy('commercial:agent_list')
        ctx['submit_label'] = _('Salvar alterações')
        return ctx

    def get_success_url(self):
        return reverse_lazy('commercial:agent_detail', args=[self.object.pk])


class AgentDeleteView(TenantViewMixin, DeleteView):
    model = Agent
    template_name = 'commercial/agent_confirm_delete.html'
    success_url = reverse_lazy('commercial:agent_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Excluir agente')
        ctx['list_url'] = reverse_lazy('commercial:agent_list')
        ctx['detail_url'] = reverse_lazy('commercial:agent_detail', args=[self.object.pk])
        return ctx


# ---------------------------------------------------------------------------
# Producer
# ---------------------------------------------------------------------------
class ProducerListView(TenantViewMixin, ListView):
    model = Producer
    template_name = 'commercial/producer_list.html'
    context_object_name = 'producers'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset().select_related('agent')
        search = (self.request.GET.get('q') or '').strip()
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(document__icontains=search) | Q(contact__icontains=search))
        agent = (self.request.GET.get('agent') or '').strip()
        if agent:
            qs = qs.filter(agent_id=agent)
        return qs.order_by('-id')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search'] = self.request.GET.get('q', '')
        ctx['selected_agent'] = self.request.GET.get('agent', '')
        ctx['agents'] = Agent.objects.for_tenant(self.request.tenant).order_by('-id')
        ctx['page_title'] = _('Produtores')
        ctx['create_url'] = reverse_lazy('commercial:producer_create')
        return ctx


class ProducerDetailView(TenantViewMixin, DetailView):
    model = Producer
    template_name = 'commercial/producer_detail.html'
    context_object_name = 'producer'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = str(self.object)
        ctx['list_url'] = reverse_lazy('commercial:producer_list')
        ctx['update_url'] = reverse_lazy('commercial:producer_update', args=[self.object.pk])
        ctx['delete_url'] = reverse_lazy('commercial:producer_delete', args=[self.object.pk])
        return ctx


class ProducerCreateView(TenantViewMixin, CreateView):
    model = Producer
    form_class = ProducerForm
    template_name = 'commercial/producer_form.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        self.restrict_form_choices(form)
        # Pre-select agent when passed via ?agent= in the URL.
        agent_pk = self.request.GET.get('agent') or self.request.POST.get('agent')
        if agent_pk and form.fields.get('agent'):
            form.fields['agent'].initial = agent_pk
        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Novo produtor')
        ctx['list_url'] = reverse_lazy('commercial:producer_list')
        ctx['submit_label'] = _('Criar produtor')
        return ctx

    def get_success_url(self):
        return reverse_lazy('commercial:producer_detail', args=[self.object.pk])


class ProducerUpdateView(TenantViewMixin, UpdateView):
    model = Producer
    form_class = ProducerForm
    template_name = 'commercial/producer_form.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        self.restrict_form_choices(form)
        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Editar produtor')
        ctx['list_url'] = reverse_lazy('commercial:producer_list')
        ctx['submit_label'] = _('Salvar alterações')
        return ctx

    def get_success_url(self):
        return reverse_lazy('commercial:producer_detail', args=[self.object.pk])


class ProducerDeleteView(TenantViewMixin, DeleteView):
    model = Producer
    template_name = 'commercial/producer_confirm_delete.html'
    success_url = reverse_lazy('commercial:producer_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Excluir produtor')
        ctx['list_url'] = reverse_lazy('commercial:producer_list')
        ctx['detail_url'] = reverse_lazy('commercial:producer_detail', args=[self.object.pk])
        return ctx


# ---------------------------------------------------------------------------
# Commission (Sprint 20)
# ---------------------------------------------------------------------------
class CommissionListView(TenantViewMixin, ListView):
    """Commissions list with_filters by período / agente / produtor.

    ``?start=`` and ``?end=`` filter by ``reference_date``; ``?agent=`` and
    ``?producer=`` filter by the related FKs. Totals are aggregated for the
    quick KPIs at the top of the screen (PRD §9.13 / §21.3).
    """

    model = Commission
    template_name = 'commercial/commission_list.html'
    context_object_name = 'commissions'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset().select_related('agent', 'producer', 'policy', 'proposal')
        start = (self.request.GET.get('start') or '').strip()
        end = (self.request.GET.get('end') or '').strip()
        if start:
            qs = qs.filter(reference_date__gte=start)
        if end:
            qs = qs.filter(reference_date__lte=end)
        agent = (self.request.GET.get('agent') or '').strip()
        if agent:
            qs = qs.filter(agent_id=agent)
        producer = (self.request.GET.get('producer') or '').strip()
        if producer:
            qs = qs.filter(producer_id=producer)
        return qs.order_by('-id')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        qs = self.get_queryset()
        agg = qs.aggregate(
            total=Sum('amount'),
            brokerage=Sum('brokerage_share'),
            agent=Sum('agent_share'),
            producer=Sum('producer_share'),
        )
        ctx['search_start'] = self.request.GET.get('start', '')
        ctx['search_end'] = self.request.GET.get('end', '')
        ctx['selected_agent'] = self.request.GET.get('agent', '')
        ctx['selected_producer'] = self.request.GET.get('producer', '')
        ctx['agents'] = Agent.objects.for_tenant(tenant).order_by('-id')
        ctx['producers'] = Producer.objects.for_tenant(tenant).order_by('-id')
        ctx['total_amount'] = agg['total'] or 0
        ctx['total_brokerage'] = agg['brokerage'] or 0
        ctx['total_agent'] = agg['agent'] or 0
        ctx['total_producer'] = agg['producer'] or 0
        ctx['page_title'] = _('Comissões')
        ctx['create_url'] = reverse_lazy('commercial:commission_create')
        return ctx


class CommissionDetailView(TenantViewMixin, DetailView):
    model = Commission
    template_name = 'commercial/commission_detail.html'
    context_object_name = 'commission'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = str(self.object)
        ctx['list_url'] = reverse_lazy('commercial:commission_list')
        ctx['update_url'] = reverse_lazy('commercial:commission_update', args=[self.object.pk])
        ctx['delete_url'] = reverse_lazy('commercial:commission_delete', args=[self.object.pk])
        return ctx


class CommissionCreateView(TenantViewMixin, CreateView):
    model = Commission
    form_class = CommissionForm
    template_name = 'commercial/commission_form.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        self.restrict_form_choices(form)
        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Nova comissão')
        ctx['list_url'] = reverse_lazy('commercial:commission_list')
        ctx['submit_label'] = _('Criar comissão')
        return ctx

    def get_success_url(self):
        return reverse_lazy('commercial:commission_detail', args=[self.object.pk])


class CommissionUpdateView(TenantViewMixin, UpdateView):
    model = Commission
    form_class = CommissionForm
    template_name = 'commercial/commission_form.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        self.restrict_form_choices(form)
        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Editar comissão')
        ctx['list_url'] = reverse_lazy('commercial:commission_list')
        ctx['submit_label'] = _('Salvar alterações')
        return ctx

    def get_success_url(self):
        return reverse_lazy('commercial:commission_detail', args=[self.object.pk])


class CommissionDeleteView(TenantViewMixin, DeleteView):
    model = Commission
    template_name = 'commercial/commission_confirm_delete.html'
    success_url = reverse_lazy('commercial:commission_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Excluir comissão')
        ctx['list_url'] = reverse_lazy('commercial:commission_list')
        ctx['detail_url'] = reverse_lazy('commercial:commission_detail', args=[self.object.pk])
        return ctx