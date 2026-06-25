"""Service layer for the onboarding app.

Keeping the signup logic outside views/migrations makes the flow reusable by
tests, templates-only onboarding and (later) an admin command.
"""
from django.contrib.auth import get_user_model
from django.db import transaction

from base.permissions import assign_role
from core.models import Brokerage, Plan

User = get_user_model()


@transaction.atomic
def register_brokerage(*, legal_name, cnpj, name='', email='', phone='',
                       address='', admin_email, admin_first_name='',
                       admin_last_name='', admin_password, plan_code='free'):
    """Create a brokerage and its first administrator in a single transaction.

    Returns ``(brokerage, admin_user)``. Respects RF-BR-01..05:
    - ``legal_name`` and ``cnpj`` are mandatory (validated at form level;
      uniqueness enforced by the model).
    - The chosen ``plan`` must be available (``Plan.is_available=True``);
      defaults to ``free``.
    - The admin user is created, linked to the brokerage and assigned the
      ``brokerage_admin`` role group.
    - There is no signup without a brokerage.
    """
    plan = Plan.objects.get(code=plan_code)
    if not plan.is_available:
        raise ValueError('Plano indisponível para cadastro.')

    brokerage = Brokerage.objects.create(
        name=name or legal_name,
        legal_name=legal_name,
        cnpj=cnpj,
        email=email,
        phone=phone,
        address=address,
        plan=plan,
    )

    admin = User.objects.create_user(
        email=admin_email,
        password=admin_password,
        first_name=admin_first_name,
        last_name=admin_last_name,
        is_active=True,
        brokerage=brokerage,
    )
    assign_role(admin, 'brokerage_admin')
    return brokerage, admin