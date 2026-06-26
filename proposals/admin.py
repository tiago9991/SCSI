from django.contrib import admin

from base.admin import TenantAwareAdmin
from proposals.models import Proposal, ProposalCoveredItem


@admin.register(Proposal)
class ProposalAdmin(TenantAwareAdmin):
    list_display = ('id', 'client', 'insurance_company', 'branch', 'status', 'valid_until', 'premium')
    list_display_links = ('id',)
    search_fields = ('client__first_name', 'client__last_name', 'client__document',
                     'insurance_company__name', 'notes')
    list_filter = ('status', 'branch', 'created_at')
    sortable_by = ('status', 'valid_until', 'premium', 'created_at')
    date_hierarchy = 'created_at'
    raw_id_fields = ('client', 'insurance_company', 'branch')

    fieldsets = (
        ('Vínculos', {'fields': ('client', 'insurance_company', 'branch')}),
        ('Negociação', {'fields': ('status', 'valid_until', 'premium')}),
        ('Outros', {'fields': ('notes',)}),
        ('IA', {'fields': ('ai_summary',), 'classes': ('collapse',)}),
    )


@admin.register(ProposalCoveredItem)
class ProposalCoveredItemAdmin(TenantAwareAdmin):
    list_display = ('id', 'proposal', 'kind', 'description', 'value')
    list_display_links = ('id',)
    search_fields = ('kind', 'description')
    list_filter = ('kind', 'created_at')
    sortable_by = ('kind', 'value', 'created_at')
    date_hierarchy = 'created_at'
    raw_id_fields = ('proposal',)

    fieldsets = (
        ('Vínculo', {'fields': ('proposal',)}),
        ('Item coberto', {'fields': ('kind', 'description', 'value', 'attributes')}),
    )