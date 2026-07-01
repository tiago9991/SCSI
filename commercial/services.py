"""Service layer for the commercial app (PRD §21.3 / Sprint 20).

Cálculo automatizado de repasses: given the total commission ``amount`` and
the configured percentuais of agente / produtor (and the implicit brokerage
share = remainder), returns the three share values. Agente and produtor are
optional — when absent their shares are zero and the brokerage keeps the full
amount.
"""
from decimal import Decimal

from commercial.models import Commission


def calculate_shares(amount, agent=None, producer=None):
    """Return ``(brokerage_share, agent_share, producer_share)`` decimals.

    ``amount`` is the total commission. ``agent`` / ``producer`` are
    ``commercial.Agent`` / ``commercial.Producer`` instances (or ``None``).
    Percentuais come from each instance's ``commission_percent`` (0–100).

    The brokerage share is whatever is left after subtracting the agent and
    producer shares from the total — guaranteed to never be negative even if
    misconfigured percentuais exceed 100% combined (clamped to zero).
    """
    amount = Decimal(amount or 0)
    agent_pct = Decimal(agent.commission_percent or 0) if agent else Decimal(0)
    producer_pct = Decimal(producer.commission_percent or 0) if producer else Decimal(0)

    agent_share = (amount * agent_pct / Decimal(100)).quantize(Decimal('0.01'))
    producer_share = (amount * producer_pct / Decimal(100)).quantize(Decimal('0.01'))
    brokerage_share = amount - agent_share - producer_share
    if brokerage_share < 0:
        brokerage_share = Decimal(0)
    return brokerage_share, agent_share, producer_share


def apply_shares(commission):
    """Compute and persist the share fields on a ``Commission`` instance.

    Uses the commission's ``agent`` / ``producer`` and ``amount``; returns the
    updated instance (caller still calls ``save()`` or the helper does it).
    """
    b, a, p = calculate_shares(commission.amount, commission.agent, commission.producer)
    commission.brokerage_share = b
    commission.agent_share = a
    commission.producer_share = p
    return commission