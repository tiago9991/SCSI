from django.contrib import admin

from base.admin import TenantAwareAdmin
from claims.models import Claim


@admin.register(Claim)
class ClaimAdmin(TenantAwareAdmin):
    list_display = ('number', 'policy', 'covered_item', 'client', 'status', 'occurrence_date', 'amount')
    list_display_links = ('number',)
    search_fields = ('number', 'client__first_name', 'client__last_name',
                     'client__document', 'description', 'policy__number')
    list_filter = ('status', 'created_at')
    sortable_by = ('status', 'occurrence_date', 'amount', 'created_at')
    date_hierarchy = 'created_at'
    raw_id_fields = ('policy', 'covered_item', 'client')

    fieldsets = (
        ('Vínculos', {'fields': ('policy', 'covered_item', 'client')}),
        ('Sinistro', {'fields': ('number', 'occurrence_date', 'description', 'status', 'amount')}),
        ('IA', {'fields': ('ai_summary',), 'classes': ('collapse',)}),
    )