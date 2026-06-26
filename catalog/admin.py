from django.contrib import admin

from base.admin import TenantAwareAdmin
from catalog.models import Branch, Coverage, InsuranceCompany


@admin.register(InsuranceCompany)
class InsuranceCompanyAdmin(TenantAwareAdmin):
    list_display = ('name', 'code', 'document', 'contact', 'created_at')
    list_display_links = ('name',)
    search_fields = ('name', 'code', 'document', 'contact')
    list_filter = ('created_at',)
    sortable_by = ('name', 'created_at')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Identificação', {'fields': ('name', 'code', 'document')}),
        ('Contato', {'fields': ('contact',)}),
    )


@admin.register(Branch)
class BranchAdmin(TenantAwareAdmin):
    list_display = ('name', 'coverage_count', 'created_at')
    list_display_links = ('name',)
    search_fields = ('name', 'description')
    list_filter = ('created_at',)
    sortable_by = ('name', 'created_at')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Identificação', {'fields': ('name',)}),
        ('Detalhes', {'fields': ('description',)}),
    )

    @admin.display(description='Coberturas')
    def coverage_count(self, obj):
        return obj.coverages.count()


@admin.register(Coverage)
class CoverageAdmin(TenantAwareAdmin):
    list_display = ('name', 'branch', 'created_at')
    list_display_links = ('name',)
    search_fields = ('name', 'description')
    list_filter = ('branch', 'created_at')
    sortable_by = ('name', 'created_at')
    date_hierarchy = 'created_at'
    raw_id_fields = ('branch',)

    fieldsets = (
        ('Vínculo', {'fields': ('branch',)}),
        ('Identificação', {'fields': ('name', 'description')}),
    )