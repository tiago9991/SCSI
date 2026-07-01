"""Class Based Views for the ``crm`` app.

All views inherit from :class:`TenantViewMixin` (see ``base.views``) so the
queryset, form FK choices and single-object fetches are automatically scoped
to ``request.tenant`` — data of another brokerage is never reachable.

Sprint 15 implements the CRM Grid (PRD §19.2 "grid"): a paginated, filterable
and sortable list of ``Deal`` objects, plus the CRUD for ``Pipeline``,
``PipelineStage`` and ``Deal``.

Sprint 16 adds the CRM Kanban (PRD §19.2 "kanban"): columns per stage,
drag-and-drop cards and a POST endpoint to persist the stage change.
"""
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from base.views import TenantRequiredMixin, TenantViewMixin
from crm.forms import DealForm, PipelineForm, PipelineStageForm
from crm.models import Deal, Pipeline, PipelineStage


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------
class PipelineListView(TenantViewMixin, ListView):
    """List of pipelines belonging to the current brokerage."""

    model = Pipeline
    template_name = 'crm/pipeline_list.html'
    context_object_name = 'pipelines'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset()
        search = (self.request.GET.get('q') or '').strip()
        if search:
            qs = qs.filter(name__icontains=search)
        return qs.order_by('-is_default', '-id')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search'] = self.request.GET.get('q', '')
        ctx['page_title'] = _('Pipelines')
        ctx['create_url'] = reverse_lazy('crm:pipeline_create')
        ctx['stage_create_url'] = reverse_lazy('crm:stage_create')
        return ctx


class PipelineDetailView(TenantViewMixin, DetailView):
    """Detail page for a single pipeline — lists its stages (1:N)."""

    model = Pipeline
    template_name = 'crm/pipeline_detail.html'
    context_object_name = 'pipeline'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = str(self.object)
        ctx['list_url'] = reverse_lazy('crm:pipeline_list')
        ctx['update_url'] = reverse_lazy('crm:pipeline_update', args=[self.object.pk])
        ctx['delete_url'] = reverse_lazy('crm:pipeline_delete', args=[self.object.pk])
        ctx['stages'] = (
            self.object.stages.for_tenant(self.request.tenant).order_by('order', 'id')
        )
        ctx['stage_create_url'] = reverse_lazy('crm:stage_create')
        return ctx


class PipelineCreateView(TenantViewMixin, CreateView):
    model = Pipeline
    form_class = PipelineForm
    template_name = 'crm/pipeline_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Novo pipeline')
        ctx['list_url'] = reverse_lazy('crm:pipeline_list')
        ctx['submit_label'] = _('Criar pipeline')
        return ctx

    def get_success_url(self):
        return reverse_lazy('crm:pipeline_detail', args=[self.object.pk])


class PipelineUpdateView(TenantViewMixin, UpdateView):
    model = Pipeline
    form_class = PipelineForm
    template_name = 'crm/pipeline_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Editar pipeline')
        ctx['list_url'] = reverse_lazy('crm:pipeline_list')
        ctx['submit_label'] = _('Salvar alterações')
        return ctx

    def get_success_url(self):
        return reverse_lazy('crm:pipeline_detail', args=[self.object.pk])


class PipelineDeleteView(TenantViewMixin, DeleteView):
    model = Pipeline
    template_name = 'crm/pipeline_confirm_delete.html'
    success_url = reverse_lazy('crm:pipeline_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Excluir pipeline')
        ctx['list_url'] = reverse_lazy('crm:pipeline_list')
        ctx['detail_url'] = reverse_lazy('crm:pipeline_detail', args=[self.object.pk])
        return ctx


# ---------------------------------------------------------------------------
# PipelineStage
# ---------------------------------------------------------------------------
class PipelineStageCreateView(TenantViewMixin, CreateView):
    """Add a stage. The pipeline is chosen via a tenant-scoped select."""

    model = PipelineStage
    form_class = PipelineStageForm
    template_name = 'crm/stage_form.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        self.restrict_form_choices(form)
        # Pre-select pipeline when passed via ?pipeline= in the URL.
        pipeline_pk = self.request.GET.get('pipeline') or self.request.POST.get('pipeline')
        if pipeline_pk:
            try:
                pipeline = Pipeline.objects.for_tenant(self.request.tenant).get(pk=pipeline_pk)
            except Pipeline.DoesNotExist:
                pipeline = None
            if pipeline is not None:
                form.fields['pipeline'].initial = pipeline.pk
        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Nova etapa')
        ctx['list_url'] = reverse_lazy('crm:pipeline_list')
        ctx['submit_label'] = _('Criar etapa')
        return ctx

    def get_success_url(self):
        pipeline = self.object.pipeline
        if pipeline is not None:
            return reverse_lazy('crm:pipeline_detail', args=[pipeline.pk])
        return reverse_lazy('crm:pipeline_list')


class PipelineStageUpdateView(TenantViewMixin, UpdateView):
    model = PipelineStage
    form_class = PipelineStageForm
    template_name = 'crm/stage_form.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        self.restrict_form_choices(form)
        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Editar etapa')
        ctx['list_url'] = reverse_lazy('crm:pipeline_detail', args=[self.object.pipeline_id])
        ctx['submit_label'] = _('Salvar alterações')
        return ctx

    def get_success_url(self):
        return reverse_lazy('crm:pipeline_detail', args=[self.object.pipeline_id])


class PipelineStageDeleteView(TenantViewMixin, DeleteView):
    model = PipelineStage
    template_name = 'crm/stage_confirm_delete.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Excluir etapa')
        ctx['list_url'] = reverse_lazy('crm:pipeline_detail', args=[self.object.pipeline_id])
        return ctx

    def get_success_url(self):
        return reverse_lazy('crm:pipeline_detail', args=[self.object.pipeline_id])


# ---------------------------------------------------------------------------
# Deal (CRM Grid)
# ---------------------------------------------------------------------------
class DealListView(TenantViewMixin, ListView):
    """CRM Grid — paginated, searchable, sortable list of deals.

    Sort is controlled by ``?sort=`` (defaults to ``-id``). Only whitelisted
    fields can be sorted to avoid SQL injection through raw ORDER BY.
    """

    model = Deal
    template_name = 'crm/deal_list.html'
    context_object_name = 'deals'
    paginate_by = 25

    SORT_FIELDS = {
        'id': 'id',
        'title': 'title',
        'amount': 'amount',
        'expected_close_date': 'expected_close_date',
        'status': 'status',
        'client': 'client__first_name',
        'stage': 'stage__order',
        'created_at': 'created_at',
    }

    def get_queryset(self):
        qs = super().get_queryset().select_related('client', 'stage', 'stage__pipeline')
        search = (self.request.GET.get('q') or '').strip()
        if search:
            qs = qs.filter(
                Q(title__icontains=search)
                | Q(client__first_name__icontains=search)
                | Q(client__last_name__icontains=search)
                | Q(client__document__icontains=search)
            )
        status = (self.request.GET.get('status') or '').strip()
        if status:
            qs = qs.filter(status=status)
        stage = (self.request.GET.get('stage') or '').strip()
        if stage:
            qs = qs.filter(stage_id=stage)
        # Sort
        sort = (self.request.GET.get('sort') or '-id').strip()
        reverse = sort.startswith('-')
        field = sort.lstrip('-')
        order_field = self.SORT_FIELDS.get(field, 'id')
        if reverse:
            order_field = f'-{order_field}'
        return qs.order_by(order_field)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search'] = self.request.GET.get('q', '')
        ctx['selected_status'] = self.request.GET.get('status', '')
        ctx['selected_stage'] = self.request.GET.get('stage', '')
        ctx['status_choices'] = Deal.STATUS_CHOICES
        ctx['stages'] = (
            PipelineStage.objects.for_tenant(self.request.tenant).order_by('pipeline', 'order', 'id')
        )
        ctx['page_title'] = _('CRM · Negociações')
        ctx['create_url'] = reverse_lazy('crm:deal_create')
        ctx['pipeline_list_url'] = reverse_lazy('crm:pipeline_list')
        ctx['sort'] = self.request.GET.get('sort', '-id')
        # Build querystring without the ``sort`` param so the template can
        # flip the sort direction while preserving filters.
        qd = self.request.GET.copy()
        qd.pop('sort', None)
        ctx['filter_querystring'] = qd.urlencode()
        return ctx


class DealDetailView(TenantViewMixin, DetailView):
    """Detail page for a single deal."""

    model = Deal
    template_name = 'crm/deal_detail.html'
    context_object_name = 'deal'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = str(self.object)
        ctx['list_url'] = reverse_lazy('crm:deal_list')
        ctx['update_url'] = reverse_lazy('crm:deal_update', args=[self.object.pk])
        ctx['delete_url'] = reverse_lazy('crm:deal_delete', args=[self.object.pk])
        # Attachments panel (Sprint 14).
        from attachments.utils import attachments_context
        att_ctx = attachments_context(self.object, self.request.tenant)
        ctx['attachments'] = att_ctx['attachments']
        ctx['upload_url'] = att_ctx['attachments_upload_url']
        return ctx


class DealCreateView(TenantViewMixin, CreateView):
    model = Deal
    form_class = DealForm
    template_name = 'crm/deal_form.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        self.restrict_form_choices(form)
        # Pre-select stage when passed via ?stage= in the URL.
        stage_pk = self.request.GET.get('stage') or self.request.POST.get('stage')
        if stage_pk:
            try:
                stage = PipelineStage.objects.for_tenant(self.request.tenant).get(pk=stage_pk)
            except PipelineStage.DoesNotExist:
                stage = None
            if stage is not None:
                form.fields['stage'].initial = stage.pk
        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Nova negociação')
        ctx['list_url'] = reverse_lazy('crm:deal_list')
        ctx['submit_label'] = _('Criar negociação')
        return ctx

    def get_success_url(self):
        return reverse_lazy('crm:deal_detail', args=[self.object.pk])


class DealUpdateView(TenantViewMixin, UpdateView):
    model = Deal
    form_class = DealForm
    template_name = 'crm/deal_form.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        self.restrict_form_choices(form)
        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Editar negociação')
        ctx['list_url'] = reverse_lazy('crm:deal_list')
        ctx['submit_label'] = _('Salvar alterações')
        return ctx

    def get_success_url(self):
        return reverse_lazy('crm:deal_detail', args=[self.object.pk])


class DealDeleteView(TenantViewMixin, DeleteView):
    model = Deal
    template_name = 'crm/deal_confirm_delete.html'
    success_url = reverse_lazy('crm:deal_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Excluir negociação')
        ctx['list_url'] = reverse_lazy('crm:deal_list')
        ctx['detail_url'] = reverse_lazy('crm:deal_detail', args=[self.object.pk])
        return ctx


# ---------------------------------------------------------------------------
# Deal (CRM Kanban) — Sprint 16
# ---------------------------------------------------------------------------
class DealKanbanView(TenantRequiredMixin, ListView):
    """CRM Kanban board (PRD §19.2 "kanban" / Sprint 16).

    Stage columns of the selected (or default) pipeline are rendered side by
    side with deal cards the user can drag-and-drop between stages. The board
    is read through ``PipelineStage.for_tenant`` so a brokerage never sees
    another brokerage's stages, and every card comes from a tenant-scoped
    ``Deal`` queryset.

    Optional query parameters:

    - ``pipeline``: pipeline pk. Defaults to the brokerage default pipeline,
      or the first pipeline of the brokerage when none is flagged as default.
    """

    model = Deal
    template_name = 'crm/deal_kanban.html'
    context_object_name = 'deals'

    def get_pipeline(self):
        tenant = self.request.tenant
        pipelines = Pipeline.objects.for_tenant(tenant).order_by('-is_default', 'id')
        pipeline_pk = self.request.GET.get('pipeline')
        if pipeline_pk:
            return get_object_or_404(pipelines, pk=pipeline_pk)
        return pipelines.first()

    def get_queryset(self):
        tenant = self.request.tenant
        qs = Deal.objects.for_tenant(tenant).select_related('client', 'stage', 'stage__pipeline')
        pipeline = self.get_pipeline()
        if pipeline is not None:
            qs = qs.filter(stage__pipeline=pipeline)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        pipeline = self.get_pipeline()

        stages = []
        if pipeline is not None:
            stages = list(
                PipelineStage.objects.for_tenant(tenant)
                .filter(pipeline=pipeline)
                .order_by('order', 'id')
                .annotate(total=Sum('deals__amount'))
            )

        # Group deals by stage so the template can render columns directly.
        deals_by_stage = {stage.pk: [] for stage in stages}
        for deal in ctx['deals']:
            stage_id = deal.stage_id
            if stage_id in deals_by_stage:
                deals_by_stage[stage_id].append(deal)

        stages_with_deals = [(stage, deals_by_stage[stage.pk]) for stage in stages]

        ctx['pipeline'] = pipeline
        ctx['pipelines'] = Pipeline.objects.for_tenant(tenant).order_by('-is_default', 'id')
        ctx['stages'] = stages
        ctx['stages_with_deals'] = stages_with_deals
        ctx['page_title'] = _('CRM · Kanban')
        ctx['list_url'] = reverse_lazy('crm:deal_list')
        ctx['kanban_url'] = reverse_lazy('crm:deal_kanban')
        ctx['create_url'] = reverse_lazy('crm:deal_create')
        ctx['pipeline_list_url'] = reverse_lazy('crm:pipeline_list')
        ctx['deal_move_url'] = reverse_lazy('crm:deal_move', args=[0])
        return ctx


@require_POST
def deal_move(request, pk):
    """Persist a drag-and-drop stage change for a deal (Sprint 16).

    Body: ``stage`` (PipelineStage pk) and optional ``order`` (int). The deal
    and the target stage are both fetched through the tenant-scoped queryset so
    a cross-brokerage move is impossible by construction.
    """
    if not request.user.is_authenticated or getattr(request, 'tenant', None) is None:
        return JsonResponse({'ok': False, 'error': 'Não autorizado.'}, status=403)

    tenant = request.tenant
    deal = get_object_or_404(Deal.objects.for_tenant(tenant), pk=pk)
    stage_pk = request.POST.get('stage')
    target_stage = get_object_or_404(PipelineStage.objects.for_tenant(tenant), pk=stage_pk)
    deal.stage = target_stage
    deal.save(update_fields=['stage', 'updated_at'])
    return JsonResponse({'ok': True, 'stage': target_stage.pk})