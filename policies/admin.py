from django.contrib import admin

from base.admin import TenantAwareAdmin
from policies.models import Policy, PolicyCoveredItem


@admin.register(Policy)
class PolicyAdmin(TenantAwareAdmin):
    list_display = ('number', 'client', 'insurance_company', 'branch', 'status', 'start_date', 'end_date', 'premium')
    list_display_links = ('number',)
    search_fields = ('number', 'client__first_name', 'client__last_name',
                     'client__document', 'insurance_company__name')
    list_filter = ('status', 'branch', 'created_at')
    sortable_by = ('status', 'start_date', 'end_date', 'premium', 'created_at')
    date_hierarchy = 'created_at'
    raw_id_fields = ('proposal', 'client', 'insurance_company', 'branch')

    fieldsets = (
        ('Vínculos', {'fields': ('proposal', 'client', 'insurance_company', 'branch')}),
        ('Apólice', {'fields': ('number', 'status', 'start_date', 'end_date', 'premium')}),
        ('IA', {'fields': ('ai_summary',), 'classes': ('collapse',)}),
    )


@admin.register(PolicyCoveredItem)
class PolicyCoveredItemAdmin(TenantAwareAdmin):
    list_display = ('id', 'policy', 'kind', 'description', 'value')
    list_display_links = ('id',)
    search_fields = ('kind', 'description')
    list_filter = ('kind', 'created_at')
    sortable_by = ('kind', 'value', 'created_at')
    date_hierarchy = 'created_at'
    raw_id_fields = ('policy',)

    fieldsets = (
        ('Vínculo', {'fields': ('policy',)}),
        ('Item coberto', {'fields': ('kind', 'description', 'value', 'attributes')}),
    )