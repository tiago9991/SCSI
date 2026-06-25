"""URL configuration for the clients app."""
from django.urls import path

from clients.views import (
    ClientCreateView,
    ClientDeleteView,
    ClientDetailView,
    ClientListView,
    ClientUpdateView,
)


app_name = 'clients'

urlpatterns = [
    path('clientes/', ClientListView.as_view(), name='client_list'),
    path('clientes/novo/', ClientCreateView.as_view(), name='client_create'),
    path('clientes/<int:pk>/', ClientDetailView.as_view(), name='client_detail'),
    path('clientes/<int:pk>/editar/', ClientUpdateView.as_view(), name='client_update'),
    path('clientes/<int:pk>/excluir/', ClientDeleteView.as_view(), name='client_delete'),
]