"""Class Based Views for the ``catalog`` app.

Implements full CRUD for the three catalog entities (InsuranceCompany, Branch
and Coverage). Every view inherits from :class:`TenantViewMixin` so querysets
and form instances are automatically scoped to ``request.tenant`` — data of
another brokerage is never reachable.

Coverage is "by branch": the list accepts a ``branch`` quick filter and the
form's ``branch`` choices are restricted to the current tenant by
``TenantFormMixin.restrict_form_choices``.
"""
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from base.views import TenantViewMixin
from catalog.forms import BranchForm, CoverageForm, InsuranceCompanyForm
from catalog.models import Branch, Coverage, InsuranceCompany


# ---------------------------------------------------------------------------
# InsuranceCompany
# ---------------------------------------------------------------------------
class InsuranceCompanyListView(TenantViewMixin, ListView):
    """Paginated list of insurers with search."""

    model = InsuranceCompany
    template_name = 'catalog/insurancecompany_list.html'
    context_object_name = 'insurance_companies'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset()
        search = (self.request.GET.get('q') or '').strip()
        if search:
            qs = qs.filter(
                Q(name__icontains=search)
                | Q(code__icontains=search)
                | Q(document__icontains=search)
                | Q(contact__icontains=search)
            )
        return qs.order_by('-id')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search'] = self.request.GET.get('q', '')
        ctx['page_title'] = _('Seguradoras')
        ctx['create_url'] = reverse_lazy('catalog:insurancecompany_create')
        return ctx


class InsuranceCompanyDetailView(TenantViewMixin, DetailView):
    """Detail page for a single insurer."""

    model = InsuranceCompany
    template_name = 'catalog/insurancecompany_detail.html'
    context_object_name = 'insurance_company'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = self.object.name
        ctx['list_url'] = reverse_lazy('catalog:insurancecompany_list')
        ctx['update_url'] = reverse_lazy('catalog:insurancecompany_update', args=[self.object.pk])
        ctx['delete_url'] = reverse_lazy('catalog:insurancecompany_delete', args=[self.object.pk])
        return ctx


class InsuranceCompanyCreateView(TenantViewMixin, CreateView):
    model = InsuranceCompany
    form_class = InsuranceCompanyForm
    template_name = 'catalog/insurancecompany_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Nova seguradora')
        ctx['list_url'] = reverse_lazy('catalog:insurancecompany_list')
        ctx['submit_label'] = _('Criar seguradora')
        return ctx

    def get_success_url(self):
        return reverse_lazy('catalog:insurancecompany_detail', args=[self.object.pk])


class InsuranceCompanyUpdateView(TenantViewMixin, UpdateView):
    model = InsuranceCompany
    form_class = InsuranceCompanyForm
    template_name = 'catalog/insurancecompany_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Editar seguradora')
        ctx['list_url'] = reverse_lazy('catalog:insurancecompany_list')
        ctx['submit_label'] = _('Salvar alterações')
        return ctx

    def get_success_url(self):
        return reverse_lazy('catalog:insurancecompany_detail', args=[self.object.pk])


class InsuranceCompanyDeleteView(TenantViewMixin, DeleteView):
    model = InsuranceCompany
    template_name = 'catalog/insurancecompany_confirm_delete.html'
    success_url = reverse_lazy('catalog:insurancecompany_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Excluir seguradora')
        ctx['list_url'] = reverse_lazy('catalog:insurancecompany_list')
        ctx['detail_url'] = reverse_lazy('catalog:insurancecompany_detail', args=[self.object.pk])
        return ctx


# ---------------------------------------------------------------------------
# Branch
# ---------------------------------------------------------------------------
class BranchListView(TenantViewMixin, ListView):
    """Paginated list of branches with search."""

    model = Branch
    template_name = 'catalog/branch_list.html'
    context_object_name = 'branches'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset()
        search = (self.request.GET.get('q') or '').strip()
        if search:
            qs = qs.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        return qs.order_by('-id')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search'] = self.request.GET.get('q', '')
        ctx['page_title'] = _('Ramos')
        ctx['create_url'] = reverse_lazy('catalog:branch_create')
        return ctx


class BranchDetailView(TenantViewMixin, DetailView):
    """Detail page for a single branch, including its coverages."""

    model = Branch
    template_name = 'catalog/branch_detail.html'
    context_object_name = 'branch'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = self.object.name
        ctx['list_url'] = reverse_lazy('catalog:branch_list')
        ctx['update_url'] = reverse_lazy('catalog:branch_update', args=[self.object.pk])
        ctx['delete_url'] = reverse_lazy('catalog:branch_delete', args=[self.object.pk])
        # Tenant-scoped coverages for this branch (read-only listing here; full
        # CRUD lives on the dedicated Coverage views below).
        ctx['coverages'] = self.object.coverages.for_tenant(self.request.tenant)
        ctx['coverage_create_url'] = reverse_lazy('catalog:coverage_create') + f'?branch={self.object.pk}'
        return ctx


class BranchCreateView(TenantViewMixin, CreateView):
    model = Branch
    form_class = BranchForm
    template_name = 'catalog/branch_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Novo ramo')
        ctx['list_url'] = reverse_lazy('catalog:branch_list')
        ctx['submit_label'] = _('Criar ramo')
        ctx['branch_suggestions'] = BranchForm.BRANCH_SUGGESTIONS
        return ctx

    def get_success_url(self):
        return reverse_lazy('catalog:branch_detail', args=[self.object.pk])


class BranchUpdateView(TenantViewMixin, UpdateView):
    model = Branch
    form_class = BranchForm
    template_name = 'catalog/branch_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Editar ramo')
        ctx['list_url'] = reverse_lazy('catalog:branch_list')
        ctx['submit_label'] = _('Salvar alterações')
        ctx['branch_suggestions'] = BranchForm.BRANCH_SUGGESTIONS
        return ctx

    def get_success_url(self):
        return reverse_lazy('catalog:branch_detail', args=[self.object.pk])


class BranchDeleteView(TenantViewMixin, DeleteView):
    model = Branch
    template_name = 'catalog/branch_confirm_delete.html'
    success_url = reverse_lazy('catalog:branch_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Excluir ramo')
        ctx['list_url'] = reverse_lazy('catalog:branch_list')
        ctx['detail_url'] = reverse_lazy('catalog:branch_detail', args=[self.object.pk])
        return ctx


# ---------------------------------------------------------------------------
# Coverage
# ---------------------------------------------------------------------------
class CoverageListView(TenantViewMixin, ListView):
    """Paginated list of coverages with search and a branch quick filter."""

    model = Coverage
    template_name = 'catalog/coverage_list.html'
    context_object_name = 'coverages'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset()
        search = (self.request.GET.get('q') or '').strip()
        branch_id = (self.request.GET.get('branch') or '').strip()
        if search:
            qs = qs.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        if branch_id:
            qs = qs.filter(branch_id=branch_id)
        return qs.select_related('branch').order_by('-id')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search'] = self.request.GET.get('q', '')
        ctx['selected_branch'] = self.request.GET.get('branch', '')
        ctx['branches'] = Branch.objects.for_tenant(self.request.tenant).order_by('name')
        ctx['page_title'] = _('Coberturas')
        ctx['create_url'] = reverse_lazy('catalog:coverage_create')
        return ctx


class CoverageDetailView(TenantViewMixin, DetailView):
    model = Coverage
    template_name = 'catalog/coverage_detail.html'
    context_object_name = 'coverage'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = self.object.name
        ctx['list_url'] = reverse_lazy('catalog:coverage_list')
        ctx['update_url'] = reverse_lazy('catalog:coverage_update', args=[self.object.pk])
        ctx['delete_url'] = reverse_lazy('catalog:coverage_delete', args=[self.object.pk])
        return ctx


class CoverageCreateView(TenantViewMixin, CreateView):
    model = Coverage
    form_class = CoverageForm
    template_name = 'catalog/coverage_form.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        self.restrict_form_choices(form)
        # Pre-select branch from query string when navigating from a branch
        # detail page (?branch=<id>).
        branch_id = self.request.GET.get('branch')
        if branch_id and not form.is_bound:
            form.fields['branch'].initial = branch_id
        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Nova cobertura')
        ctx['list_url'] = reverse_lazy('catalog:coverage_list')
        ctx['submit_label'] = _('Criar cobertura')
        return ctx

    def get_success_url(self):
        return reverse_lazy('catalog:coverage_detail', args=[self.object.pk])


class CoverageUpdateView(TenantViewMixin, UpdateView):
    model = Coverage
    form_class = CoverageForm
    template_name = 'catalog/coverage_form.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        self.restrict_form_choices(form)
        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Editar cobertura')
        ctx['list_url'] = reverse_lazy('catalog:coverage_list')
        ctx['submit_label'] = _('Salvar alterações')
        return ctx

    def get_success_url(self):
        return reverse_lazy('catalog:coverage_detail', args=[self.object.pk])


class CoverageDeleteView(TenantViewMixin, DeleteView):
    model = Coverage
    template_name = 'catalog/coverage_confirm_delete.html'
    success_url = reverse_lazy('catalog:coverage_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = _('Excluir cobertura')
        ctx['list_url'] = reverse_lazy('catalog:coverage_list')
        ctx['detail_url'] = reverse_lazy('catalog:coverage_detail', args=[self.object.pk])
        return ctx