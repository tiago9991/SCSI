"""URL configuration for the claims app."""
from django.urls import path

from claims.views import (
    ClaimCreateView,
    ClaimDeleteView,
    ClaimDetailView,
    ClaimListView,
    ClaimUpdateView,
)


app_name = 'claims'

urlpatterns = [
    path('sinistros/', ClaimListView.as_view(), name='claim_list'),
    path('sinistros/novo/', ClaimCreateView.as_view(), name='claim_create'),
    path('sinistros/<int:pk>/', ClaimDetailView.as_view(), name='claim_detail'),
    path('sinistros/<int:pk>/editar/', ClaimUpdateView.as_view(), name='claim_update'),
    path('sinistros/<int:pk>/excluir/', ClaimDeleteView.as_view(), name='claim_delete'),
]