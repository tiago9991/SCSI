from django.contrib import admin

from base.admin import TenantAwareAdmin
from commercial.models import Agent, Commission, Producer


@admin.register(Agent)
class AgentAdmin(TenantAwareAdmin):
    list_display = ('id', 'name', 'document', 'type', 'commission_percent', 'created_at')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'document', 'contact')
    list_filter = ('type', 'created_at')
    sortable_by = ('name', 'commission_percent', 'created_at')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Agente', {'fields': ('name', 'document', 'type', 'commission_percent', 'contact')}),
    )


@admin.register(Producer)
class ProducerAdmin(TenantAwareAdmin):
    list_display = ('id', 'name', 'agent', 'document', 'commission_percent', 'created_at')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'document', 'contact', 'agent__name')
    list_filter = ('created_at',)
    sortable_by = ('name', 'commission_percent', 'created_at')
    date_hierarchy = 'created_at'
    raw_id_fields = ('agent',)

    fieldsets = (
        ('Produtor', {'fields': ('name', 'agent', 'document', 'commission_percent', 'contact')}),
    )


@admin.register(Commission)
class CommissionAdmin(TenantAwareAdmin):
    list_display = ('id', 'amount', 'agent', 'producer', 'brokerage_share', 'agent_share', 'producer_share', 'reference_date')
    list_display_links = ('id',)
    search_fields = ('agent__name', 'producer__name', 'policy__number')
    list_filter = ('reference_date', 'created_at')
    sortable_by = ('amount', 'reference_date', 'created_at')
    date_hierarchy = 'reference_date'
    raw_id_fields = ('policy', 'proposal', 'agent', 'producer')

    fieldsets = (
        ('Vínculos', {'fields': ('policy', 'proposal', 'agent', 'producer')}),
        ('Comissão', {'fields': ('amount', 'reference_date')}),
        ('Repasses', {'fields': ('brokerage_share', 'agent_share', 'producer_share')}),
    )