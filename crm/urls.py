"""URL configuration for the crm app."""
from django.urls import path

from crm.views import (
    DealCreateView,
    DealDeleteView,
    DealDetailView,
    DealListView,
    DealUpdateView,
    PipelineCreateView,
    PipelineDeleteView,
    PipelineDetailView,
    PipelineListView,
    PipelineUpdateView,
    PipelineStageCreateView,
    PipelineStageDeleteView,
    PipelineStageUpdateView,
)


app_name = 'crm'

urlpatterns = [
    # --- Pipelines ---
    path('crm/pipelines/', PipelineListView.as_view(), name='pipeline_list'),
    path('crm/pipelines/novo/', PipelineCreateView.as_view(), name='pipeline_create'),
    path('crm/pipelines/<int:pk>/', PipelineDetailView.as_view(), name='pipeline_detail'),
    path('crm/pipelines/<int:pk>/editar/', PipelineUpdateView.as_view(), name='pipeline_update'),
    path('crm/pipelines/<int:pk>/excluir/', PipelineDeleteView.as_view(), name='pipeline_delete'),

    # --- Pipeline stages (nested under pipeline where possible) ---
    path('crm/etapas/novo/', PipelineStageCreateView.as_view(), name='stage_create'),
    path('crm/etapas/<int:pk>/editar/', PipelineStageUpdateView.as_view(), name='stage_update'),
    path('crm/etapas/<int:pk>/excluir/', PipelineStageDeleteView.as_view(), name='stage_delete'),

    # --- Deals (CRM Grid) ---
    path('crm/negociacoes/', DealListView.as_view(), name='deal_list'),
    path('crm/negociacoes/novo/', DealCreateView.as_view(), name='deal_create'),
    path('crm/negociacoes/<int:pk>/', DealDetailView.as_view(), name='deal_detail'),
    path('crm/negociacoes/<int:pk>/editar/', DealUpdateView.as_view(), name='deal_update'),
    path('crm/negociacoes/<int:pk>/excluir/', DealDeleteView.as_view(), name='deal_delete'),
]