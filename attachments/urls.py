"""URL configuration for the attachments app.

Routes:
- ``anexos/upload/<ct>/<oid>/`` — upload form for a parent object.
- ``anexos/<pk>/excluir/`` — delete a single attachment.
- ``anexos/<pk>/arquivo/`` — private media serving (PRD §14.2).
"""
from django.urls import path

from attachments.views import AttachmentCreateView, AttachmentDeleteView, PrivateMediaView


app_name = 'attachments'

urlpatterns = [
    path('anexos/upload/<int:content_type_id>/<int:object_id>/',
         AttachmentCreateView.as_view(), name='attachment_create'),
    path('anexos/<int:pk>/excluir/',
         AttachmentDeleteView.as_view(), name='attachment_delete'),
    path('anexos/<int:pk>/arquivo/',
         PrivateMediaView.as_view(), name='attachment_file'),
]