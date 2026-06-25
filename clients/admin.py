from django.contrib import admin

from base.admin import TenantAwareAdmin
from clients.models import Client


@admin.register(Client)
class ClientAdmin(TenantAwareAdmin):
    list_display = ('full_name_display', 'document', 'email', 'phone', 'created_at')
    list_display_links = ('full_name_display',)
    search_fields = ('first_name', 'last_name', 'document', 'email', 'phone')
    list_filter = ('created_at',)
    sortable_by = ('created_at',)
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Identificação', {'fields': ('first_name', 'last_name', 'document')}),
        ('Contato', {'fields': ('email', 'phone', 'address')}),
        ('Outros', {'fields': ('birth_date', 'notes')}),
        ('IA', {'fields': ('ai_summary',), 'classes': ('collapse',)}),
    )

    @admin.display(description='Nome')
    def full_name_display(self, obj):
        return obj.full_name

    def get_fieldsets(self, request, obj=None):
        # SCM-internal staff (scsi_staff role, planned) can see brokerage picker;
        # brokerage users are auto-scoped by TenantAwareAdmin.save_model.
        return super().get_fieldsets(request, obj)