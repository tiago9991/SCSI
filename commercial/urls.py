"""URL configuration for the commercial app."""
from django.urls import path

from commercial.views import (
    AgentCreateView,
    AgentDeleteView,
    AgentDetailView,
    AgentListView,
    AgentUpdateView,
    CommissionCreateView,
    CommissionDeleteView,
    CommissionDetailView,
    CommissionListView,
    CommissionUpdateView,
    ProducerCreateView,
    ProducerDeleteView,
    ProducerDetailView,
    ProducerListView,
    ProducerUpdateView,
)


app_name = 'commercial'

urlpatterns = [
    # --- Agents ---
    path('comercial/agentes/', AgentListView.as_view(), name='agent_list'),
    path('comercial/agentes/novo/', AgentCreateView.as_view(), name='agent_create'),
    path('comercial/agentes/<int:pk>/', AgentDetailView.as_view(), name='agent_detail'),
    path('comercial/agentes/<int:pk>/editar/', AgentUpdateView.as_view(), name='agent_update'),
    path('comercial/agentes/<int:pk>/excluir/', AgentDeleteView.as_view(), name='agent_delete'),

    # --- Producers ---
    path('comercial/produtores/', ProducerListView.as_view(), name='producer_list'),
    path('comercial/produtores/novo/', ProducerCreateView.as_view(), name='producer_create'),
    path('comercial/produtores/<int:pk>/', ProducerDetailView.as_view(), name='producer_detail'),
    path('comercial/produtores/<int:pk>/editar/', ProducerUpdateView.as_view(), name='producer_update'),
    path('comercial/produtores/<int:pk>/excluir/', ProducerDeleteView.as_view(), name='producer_delete'),

    # --- Commissions (Sprint 20) ---
    path('comercial/comissoes/', CommissionListView.as_view(), name='commission_list'),
    path('comercial/comissoes/novo/', CommissionCreateView.as_view(), name='commission_create'),
    path('comercial/comissoes/<int:pk>/', CommissionDetailView.as_view(), name='commission_detail'),
    path('comercial/comissoes/<int:pk>/editar/', CommissionUpdateView.as_view(), name='commission_update'),
    path('comercial/comissoes/<int:pk>/excluir/', CommissionDeleteView.as_view(), name='commission_delete'),
]