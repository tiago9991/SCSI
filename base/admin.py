"""Tenant-aware base ``ModelAdmin`` shared by domain apps.

Per PRD §26.3:
- ``get_queryset`` filters by ``request.user.brokerage`` so brokerage users
  only see their own data.
- Superusers (internal SCSI staff) keep the global queryset — the multi-tenant
  admin audit hook should live on top of the standard Django log.
- ``save_model`` stamps ``brokerage`` from the request user when the model
  inherits ``BaseTenantModel`` and ``brokerage`` isn't already set.
"""
from django.contrib import admin


class TenantAwareAdmin(admin.ModelAdmin):
    """Multi-tenant ModelAdmin base for ``BaseTenantModel`` subclasses."""

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        if user.is_superuser:
            return qs
        brokerage = getattr(user, 'brokerage', None)
        if brokerage is None:
            return qs.none()
        # TenantQuerySet already supports for_tenant; for managers attached to
        # BaseTenantModel subclasses use it directly when feasible.
        if hasattr(qs, 'for_tenant'):
            return qs.for_tenant(brokerage)
        # Fallback: filter by brokerage field when present.
        try:
            qs.model._meta.get_field('brokerage')
            return qs.filter(brokerage=brokerage)
        except Exception:
            return qs

    def save_model(self, request, obj, form, change):
        if not change and not getattr(obj, 'brokerage_id', None):
            brokerage = getattr(request.user, 'brokerage', None)
            if brokerage is not None:
                obj.brokerage = brokerage
        super().save_model(request, obj, form, change)

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        # Pre-fill brokerage when possible (rarely visible on the form).
        if 'brokerage' in [f.name for f in self.model._meta.get_fields()] \
                and not initial.get('brokerage'):
            brokerage = getattr(request.user, 'brokerage', None)
            if brokerage is not None:
                initial['brokerage'] = brokerage.id
        return initial