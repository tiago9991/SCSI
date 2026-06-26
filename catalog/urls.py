"""URL configuration for the catalog app."""
from django.urls import path

from catalog.views import (
    BranchCreateView,
    BranchDeleteView,
    BranchDetailView,
    BranchListView,
    BranchUpdateView,
    CoverageCreateView,
    CoverageDeleteView,
    CoverageDetailView,
    CoverageListView,
    CoverageUpdateView,
    InsuranceCompanyCreateView,
    InsuranceCompanyDeleteView,
    InsuranceCompanyDetailView,
    InsuranceCompanyListView,
    InsuranceCompanyUpdateView,
)


app_name = 'catalog'

urlpatterns = [
    # --- InsuranceCompany (seguradoras) ---
    path('seguradoras/', InsuranceCompanyListView.as_view(), name='insurancecompany_list'),
    path('seguradoras/novo/', InsuranceCompanyCreateView.as_view(), name='insurancecompany_create'),
    path('seguradoras/<int:pk>/', InsuranceCompanyDetailView.as_view(), name='insurancecompany_detail'),
    path('seguradoras/<int:pk>/editar/', InsuranceCompanyUpdateView.as_view(), name='insurancecompany_update'),
    path('seguradoras/<int:pk>/excluir/', InsuranceCompanyDeleteView.as_view(), name='insurancecompany_delete'),

    # --- Branch (ramos) ---
    path('ramos/', BranchListView.as_view(), name='branch_list'),
    path('ramos/novo/', BranchCreateView.as_view(), name='branch_create'),
    path('ramos/<int:pk>/', BranchDetailView.as_view(), name='branch_detail'),
    path('ramos/<int:pk>/editar/', BranchUpdateView.as_view(), name='branch_update'),
    path('ramos/<int:pk>/excluir/', BranchDeleteView.as_view(), name='branch_delete'),

    # --- Coverage (coberturas) ---
    path('coberturas/', CoverageListView.as_view(), name='coverage_list'),
    path('coberturas/novo/', CoverageCreateView.as_view(), name='coverage_create'),
    path('coberturas/<int:pk>/', CoverageDetailView.as_view(), name='coverage_detail'),
    path('coberturas/<int:pk>/editar/', CoverageUpdateView.as_view(), name='coverage_update'),
    path('coberturas/<int:pk>/excluir/', CoverageDeleteView.as_view(), name='coverage_delete'),
]