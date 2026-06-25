"""Views for the onboarding app.

All views are CBV. Landing page is public. Signup collects brokerage + admin
data in a single form and authenticates the new administrator before
redirecting to the dashboard.
"""
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from onboarding.forms import BrokerageSignupForm
from onboarding.services import register_brokerage


class LandingView(TemplateView):
    """Public landing page (root ``/``).

    Renders the marketing copy, CTA buttons (Criar conta / Acessar) and the
    plans strip (only ``free`` is enabled; paid plans show "em breve" per
    RF-LP-04).
    """

    template_name = 'onboarding/landing.html'

    def get_context_data(self, **kwargs):
        from core.models import Plan
        ctx = super().get_context_data(**kwargs)
        ctx['plans'] = Plan.objects.filter(is_active=True).order_by('id')
        ctx['title'] = 'SCSI · Gestão para Corretora de Seguros'
        return ctx


class SignupView(FormView):
    """Brokerage signup form (CNPJ + Razão Social obrigatórios).

    On success creates ``Brokerage`` + ``User`` admin (via
    ``register_brokerage``), logs the new admin in and redirects to the
    dashboard (admin:index for now; replaced by app dashboard in Sprint 22).
    """

    template_name = 'onboarding/signup.html'
    form_class = BrokerageSignupForm
    success_url = reverse_lazy('admin:index')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('admin:index')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        data = form.cleaned_data
        brokerage, admin = register_brokerage(
            legal_name=data['legal_name'],
            cnpj=data['cnpj'],
            name=data.get('name') or '',
            email=data.get('email') or '',
            phone=data.get('phone') or '',
            address=data.get('address') or '',
            admin_email=data['admin_email'],
            admin_first_name=data.get('admin_first_name') or '',
            admin_last_name=data.get('admin_last_name') or '',
            admin_password=data['admin_password'],
            plan_code=data.get('plan') or 'free',
        )
        # SiteProtocol-less backend: authenticate by email + raw password.
        from django.contrib.auth import authenticate
        user = authenticate(
            self.request,
            username=admin.email,
            password=data['admin_password'],
        )
        if user is not None:
            login(self.request, user)
        return HttpResponseRedirect(self.get_success_url())