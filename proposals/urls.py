"""URL configuration for the proposals app."""
from django.urls import path

from proposals.views import (
    ProposalCoveredItemCreateView,
    ProposalCoveredItemDeleteView,
    ProposalCoveredItemUpdateView,
    ProposalCreateView,
    ProposalDeleteView,
    ProposalDetailView,
    ProposalListView,
    ProposalUpdateView,
)


app_name = 'proposals'

urlpatterns = [
    # --- Proposal (propostas) ---
    path('propostas/', ProposalListView.as_view(), name='proposal_list'),
    path('propostas/novo/', ProposalCreateView.as_view(), name='proposal_create'),
    path('propostas/<int:pk>/', ProposalDetailView.as_view(), name='proposal_detail'),
    path('propostas/<int:pk>/editar/', ProposalUpdateView.as_view(), name='proposal_update'),
    path('propostas/<int:pk>/excluir/', ProposalDeleteView.as_view(), name='proposal_delete'),

    # --- Covered items nested under a proposal (1:N) ---
    path('propostas/<int:proposal_pk>/itens/novo/',
         ProposalCoveredItemCreateView.as_view(), name='covereditem_create'),
    path('propostas/<int:proposal_pk>/itens/<int:pk>/editar/',
         ProposalCoveredItemUpdateView.as_view(), name='covereditem_update'),
    path('propostas/<int:proposal_pk>/itens/<int:pk>/excluir/',
         ProposalCoveredItemDeleteView.as_view(), name='covereditem_delete'),
]