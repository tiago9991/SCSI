from django.contrib import admin

from base.admin import TenantAwareAdmin
from attachments.models import Attachment


@admin.register(Attachment)
class AttachmentAdmin(TenantAwareAdmin):
    list_display = ('id', 'name', 'brokerage', 'content_type', 'object_id', 'size', 'created_at')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'mime')
    list_filter = ('content_type', 'created_at')
    sortable_by = ('size', 'created_at')
    date_hierarchy = 'created_at'
    readonly_fields = ('name', 'mime', 'size', 'content_type', 'object_id', 'brokerage')