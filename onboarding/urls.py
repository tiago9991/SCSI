"""URL configuration for the onboarding app."""
from django.urls import path

from onboarding.views import LandingView, SignupView


app_name = 'onboarding'

urlpatterns = [
    path('', LandingView.as_view(), name='landing'),
    path('cadastro/', SignupView.as_view(), name='signup'),
]