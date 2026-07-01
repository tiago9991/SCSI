"""URL configuration for the policies app."""
from django.urls import path

from policies.views import (
    EndorsementCreateView,
    EndorsementDeleteView,
    EndorsementUpdateView,
    PolicyCoveredItemCreateView,
    PolicyCoveredItemDeleteView,
    PolicyCoveredItemUpdateView,
    PolicyCreateView,
    PolicyDeleteView,
    PolicyDetailView,
    PolicyListView,
    PolicyUpdateView,
    RenewalCreateView,
    RenewalDeleteView,
    RenewalDetailView,
    RenewalListView,
    RenewalUpdateView,
)


app_name = 'policies'

urlpatterns = [
    # --- Policy (apólices) ---
    path('apolices/', PolicyListView.as_view(), name='policy_list'),
    path('apolices/novo/', PolicyCreateView.as_view(), name='policy_create'),
    path('apolices/<int:pk>/', PolicyDetailView.as_view(), name='policy_detail'),
    path('apolices/<int:pk>/editar/', PolicyUpdateView.as_view(), name='policy_update'),
    path('apolices/<int:pk>/excluir/', PolicyDeleteView.as_view(), name='policy_delete'),

    # --- Covered items nested under a policy (1:N) ---
    path('apolices/<int:policy_pk>/itens/novo/',
         PolicyCoveredItemCreateView.as_view(), name='covereditem_create'),
    path('apolices/<int:policy_pk>/itens/<int:pk>/editar/',
         PolicyCoveredItemUpdateView.as_view(), name='covereditem_update'),
    path('apolices/<int:policy_pk>/itens/<int:pk>/excluir/',
         PolicyCoveredItemDeleteView.as_view(), name='covereditem_delete'),

    # --- Endorsements nested under a policy (1:N) — Sprint 18 ---
    path('apolices/<int:policy_pk>/endossos/novo/',
         EndorsementCreateView.as_view(), name='endorsement_create'),
    path('apolices/<int:policy_pk>/endossos/<int:pk>/editar/',
         EndorsementUpdateView.as_view(), name='endorsement_update'),
    path('apolices/<int:policy_pk>/endossos/<int:pk>/excluir/',
         EndorsementDeleteView.as_view(), name='endorsement_delete'),

    # --- Renewals (top-level list + nested create) — Sprint 17 ---
    path('renovacoes/', RenewalListView.as_view(), name='renewal_list'),
    path('renovacoes/novo/', RenewalCreateView.as_view(), name='renewal_create_top'),
    path('renovacoes/<int:pk>/', RenewalDetailView.as_view(), name='renewal_detail'),
    path('renovacoes/<int:pk>/editar/', RenewalUpdateView.as_view(), name='renewal_update'),
    path('renovacoes/<int:pk>/excluir/', RenewalDeleteView.as_view(), name='renewal_delete'),
    path('apolices/<int:policy_pk>/renovacoes/novo/',
         RenewalCreateView.as_view(), name='renewal_create'),
]