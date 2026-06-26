"""URL configuration for the policies app."""
from django.urls import path

from policies.views import (
    PolicyCoveredItemCreateView,
    PolicyCoveredItemDeleteView,
    PolicyCoveredItemUpdateView,
    PolicyCreateView,
    PolicyDeleteView,
    PolicyDetailView,
    PolicyListView,
    PolicyUpdateView,
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
]