"""Class Based View mixins for the multi-tenant architecture.

These mixins enforce tenant (brokerage) isolation on every read/write path
using ``request.tenant`` (set by ``core.middlewares.TenantMiddleware``):

- ``TenantRequiredMixin``: requires an authenticated user with a brokerage.
- ``TenantQuerySetMixin``: scopes ListView / SingleObject querysets to the
  tenant via ``TenantQuerySet.for_tenant``.
- ``TenantFormMixin``: stamps ``brokerage`` on create and helpers to restrict
  FK / M2M choices to the current tenant.
- ``TenantViewMixin``: convenience base combining the three above for CRUD.

Usage::

    class ProposalListView(TenantViewMixin, ListView):
        model = Proposal

    class ProposalUpdateView(TenantViewMixin, UpdateView):
        model = Proposal
        fields = [...]

Order matters: tenant mixins must precede the generic Django CBV in the MRO
so ``super().get_queryset()`` resolves to ``MultipleObjectMixin`` /
``SingleObjectMixin``.
"""
from django.core.exceptions import FieldDoesNotExist, PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404

from django.contrib.auth.mixins import LoginRequiredMixin


class TenantRequiredMixin(LoginRequiredMixin):
    """LoginRequiredMixin that also enforces ``request.tenant`` (brokerage).

    Anonymous users are handled by ``LoginRequiredMixin`` (redirect to
    ``LOGIN_URL``). Authenticated users without a brokerage (superusers /
    internal SCSI staff) get a ``PermissionDenied`` (403) — they can still use
    the Django admin, which has its own tenant-aware queryset filtering.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if getattr(request, 'tenant', None) is None:
            raise PermissionDenied('Usuário sem corretora vinculada.')
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class TenantQuerySetMixin:
    """Scope a model queryset to the current tenant (``request.tenant``).

    Relies on ``TenantManager.for_tenant`` exposed by ``BaseTenantModel``
    subclasses. Place before ``ListView`` / ``SingleObjectMixin`` in MRO so
    ``super().get_queryset()`` returns the unscoped manager queryset.
    """

    tenant_field = 'brokerage'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.for_tenant(self.request.tenant)


class TenantFormMixin:
    """Stamp ``brokerage`` on create and expose FK-choice restriction helpers.

    For ``CreateView`` it forces ``brokerage = request.tenant`` before saving.
    For ``UpdateView`` the object is already loaded through the tenant-scoped
    queryset, so this is a no-op.

    Call ``self.restrict_form_choices(form)`` from ``get_form()`` in concrete
    views to filter ``ModelChoiceField`` / ``ModelMultipleChoiceField``
    querysets to the current tenant (inspecting each related model).
    """

    tenant_field = 'brokerage'

    def form_valid(self, form):
        if not getattr(form.instance, self.tenant_field, None):
            setattr(form.instance, self.tenant_field, self.request.tenant)
        return super().form_valid(form)

    def restrict_form_choices(self, form):
        """Limit every FK / M2M field on ``form`` to the current tenant.

        Each related model that inherits ``BaseTenantModel`` is filtered via
        ``for_tenant``; unrelated fields are left untouched.
        """
        from base.models import BaseTenantModel

        for field_name, field in form.fields.items():
            queryset = getattr(field, 'queryset', None)
            if queryset is None:
                continue
            model = queryset.model
            if not issubclass(model, BaseTenantModel):
                continue
            try:
                model._meta.get_field(self.tenant_field)
            except FieldDoesNotExist:
                continue
            field.queryset = queryset.for_tenant(self.request.tenant)
        return form


class TenantObjectMixin:
    """SingleObject fetch that strictly filters by tenant.

    Used as an explicit guard on ``get_object``: even if a ``pk`` for another
    tenant is supplied, the lookup runs through ``for_tenant`` and returns
    404 instead of leaking data.
    """

    tenant_field = 'brokerage'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        pk = self.kwargs.get(self.pk_url_kwarg or 'pk')
        if pk is None:
            raise AttributeError(
                f'{self.__class__.__name__} requires a pk URL keyword argument.'
            )
        return get_object_or_404(queryset.for_tenant(self.request.tenant), pk=pk)


class TenantViewMixin(TenantRequiredMixin, TenantQuerySetMixin, TenantFormMixin, TenantObjectMixin):
    """Convenience base mixin for tenant-scoped CRUD CBVs.

    Combine with: ``ListView``, ``DetailView``, ``CreateView``, ``UpdateView``
    or ``DeleteView``. Always declare tenant mixins before the generic view::

        class DealUpdateView(TenantViewMixin, UpdateView):
            model = Deal
    """