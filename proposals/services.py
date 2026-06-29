"""Service layer for the proposals app.

The "Gerar apólice" flow (PRD §20.2 / Sprint 12) lives here so it can be reused
by views, admin actions and (eventually) a management command. It creates the
``Policy`` from an accepted ``Proposal`` and copies every ``ProposalCoveredItem``
into a ``PolicyCoveredItem`` in a single transaction, keeping the ``proposal``
FK link on the new policy.
"""
from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from policies.models import Policy, PolicyCoveredItem
from proposals.models import Proposal


class ProposalNotAcceptedError(ValueError):
    """Raised when "Gerar apólice" is invoked on a non-accepted proposal."""


def default_policy_number(brokerage, policy_pk):
    """Build a human-readable policy number.

    Per PRD §20.2 the number format is "configurável por corretora" — there is
    no brokerage config model yet, so we emit a stable default based on the
    brokerage pk, the current year and the policy pk. This keeps the number
    unique within the brokerage while remaining easy to override later.
    """
    year = timezone.localdate().year
    return f'{brokerage.pk}-{year}-{policy_pk:06d}'


@transaction.atomic
def generate_policy_from_proposal(proposal):
    """Create a ``Policy`` from an accepted ``Proposal`` (PRD Sprint 12).

    - Requires ``proposal.status == Proposal.STATUS_ACCEPTED``.
    - Copies client, insurance_company, branch and premium from the proposal.
    - Keeps the ``proposal`` FK link on the new policy.
    - Defines ``start_date`` (today) and ``end_date`` (``valid_until`` when
      available, otherwise today + 365 days).
    - Generates a policy number via :func:`default_policy_number`.
    - Copies every ``ProposalCoveredItem`` → ``PolicyCoveredItem`` preserving
      ``kind``, ``description``, ``value``, ``attributes`` and ``brokerage``.

    Returns the created ``Policy``.
    """
    if proposal.status != Proposal.STATUS_ACCEPTED:
        raise ProposalNotAcceptedError(
            _('Apenas propostas aceitas podem gerar apólice.')
        )

    today = timezone.localdate()
    end_date = proposal.valid_until or (today + timedelta(days=365))

    policy = Policy.objects.create(
        brokerage=proposal.brokerage,
        proposal=proposal,
        client=proposal.client,
        insurance_company=proposal.insurance_company,
        branch=proposal.branch,
        number='',  # stamped below so it can embed the policy pk
        start_date=today,
        end_date=end_date,
        premium=proposal.premium,
        status=Policy.STATUS_ACTIVE,
    )
    policy.number = default_policy_number(proposal.brokerage, policy.pk)
    policy.save(update_fields=['number'])

    covered_items = list(proposal.covered_items.all())
    PolicyCoveredItem.objects.bulk_create(
        [
            PolicyCoveredItem(
                brokerage=proposal.brokerage,
                policy=policy,
                kind=item.kind,
                description=item.description,
                value=item.value,
                attributes=item.attributes or {},
            )
            for item in covered_items
        ]
    )
    return policy