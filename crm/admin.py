from django.contrib import admin

from base.admin import TenantAwareAdmin
from crm.models import Deal, Pipeline, PipelineStage


@admin.register(Pipeline)
class PipelineAdmin(TenantAwareAdmin):
    list_display = ('id', 'name', 'is_default', 'brokerage', 'created_at')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    list_filter = ('is_default', 'created_at')
    sortable_by = ('name', 'created_at')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Dados', {'fields': ('name', 'is_default')}),
    )


@admin.register(PipelineStage)
class PipelineStageAdmin(TenantAwareAdmin):
    list_display = ('id', 'pipeline', 'name', 'color', 'order', 'created_at')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'pipeline__name')
    list_filter = ('created_at',)
    sortable_by = ('order', 'created_at')
    date_hierarchy = 'created_at'
    raw_id_fields = ('pipeline',)

    fieldsets = (
        ('Vínculo', {'fields': ('pipeline',)}),
        ('Etapa', {'fields': ('name', 'color', 'order')}),
    )


@admin.register(Deal)
class DealAdmin(TenantAwareAdmin):
    list_display = ('id', 'title', 'client', 'stage', 'amount', 'expected_close_date', 'status')
    list_display_links = ('id', 'title')
    search_fields = ('title', 'client__first_name', 'client__last_name',
                     'client__document')
    list_filter = ('status', 'created_at')
    sortable_by = ('amount', 'expected_close_date', 'status', 'created_at')
    date_hierarchy = 'created_at'
    raw_id_fields = ('client', 'stage')

    fieldsets = (
        ('Vínculos', {'fields': ('client', 'stage')}),
        ('Negociação', {'fields': ('title', 'amount', 'expected_close_date', 'status')}),
        ('IA', {'fields': ('ai_summary',), 'classes': ('collapse',)}),
    )