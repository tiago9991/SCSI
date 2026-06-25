"""Role helpers and permission definitions for SCSI.

Per PRD §7.2: roles are managed via Django ``Group`` instances. Five roles
exist:

- ``brokerage_admin``     — Owner/admin of the brokerage (full access in tenant)
- ``brokerage_agent``     — External agent of the brokerage
- ``brokerage_producer``  — Producer/broker (final seller)
- ``brokerage_backoffice``— Back-office (catalog/attachments, no financials)
- ``scsi_staff``          — Internal SCSI staff (Django Admin, tenant-scoped)

Group membership is the single source of truth for a user's role. The
``ROLE_CODES`` mapping below is referenced by the seeding migration and by
``role_required`` helpers; the migration runs ``sync_roles`` (idempotent),
keeping the groups in sync with this module.
"""
from collections import OrderedDict

ROLE_CODES = OrderedDict([
    ('brokerage_admin', 'Administrador da corretora'),
    ('brokerage_agent', 'Agente'),
    ('brokerage_producer', 'Produtor'),
    ('brokerage_backoffice', 'Back-office'),
    ('scsi_staff', 'Equipe SCSI'),
])


# Per-role custom-permission codenames (Django app-level permissions). These
# map to ``Meta.permissions`` of each app's models and grant additional
# capability-based grants layered above standard ``add_*`` / ``change_*``.
# Currently empty: standard model-level permissions suffice for the initial
# role-based system. Custom codenames will be registered here as domains are
# added (Sprints 7+), keeping a single source of truth for role → permission.
ROLE_PERMISSIONS = {
    role_code: [] for role_code in ROLE_CODES
}


def sync_roles(sender=None, **kwargs):
    """Create/refresh the role ``Group``s.

    Idempotent — safe to call from migrations, the ready() hook, and tests.
    Returns a dict ``{role_code: Group}`` for the caller's convenience.

    The group ``name`` is the role code (e.g. ``brokerage_admin``) so
    membership checks are stable across codebases; the human-readable label
    is reachable via ``ROLE_CODES[code]``.
    """
    from django.contrib.auth.models import Group

    groups = {}
    for code, label in ROLE_CODES.items():
        group, _ = Group.objects.get_or_create(name=code)
        groups[code] = group
    return groups


def assign_role(user, role_code):
    """Assign a role ``Group`` to ``user`` (replaces any brokerage role)."""
    if role_code not in ROLE_CODES:
        raise ValueError(f'Unknown role: {role_code}')
    # Remove all known roles first; multi-tenant users have exactly one role.
    existing = list(
        user.groups.filter(name__in=list(ROLE_CODES)).exclude(name=role_code)
    )
    if existing:
        user.groups.remove(*existing)
    from django.contrib.auth.models import Group
    group, _ = Group.objects.get_or_create(name=role_code)
    user.groups.add(group)
    return group


def get_role(user):
    """Return the role code for ``user`` (or ``None`` if no known group)."""
    group = user.groups.filter(name__in=list(ROLE_CODES)).first()
    return group.name if group else None


# Baseline ``(app_label, codename)`` permission grants per role. Kept as a
# single source of truth so the post_migrate receiver can refresh grants every
# time migrate runs (idempotent via ``permissions.set``). Future domain sprints
# will append their custom codenames here.
ROLE_PERMISSION_CODES = {
    'brokerage_admin': [
        ('core', 'add_user'), ('core', 'change_user'),
        ('core', 'delete_user'), ('core', 'view_user'),
        ('auth', 'add_group'), ('auth', 'change_group'),
        ('auth', 'delete_group'), ('auth', 'view_group'),
    ],
    'scsi_staff': [
        ('core', 'view_user'), ('auth', 'view_group'),
    ],
}


def sync_role_permissions():
    """Refresh the baseline Django permissions attached to each role ``Group``.

    Runs via the ``post_migrate`` receiver (see ``base.apps.ready``), i.e.
    after Django has created all ``ContentType`` and ``Permission`` rows driven
    by the installed models. Idempotent — uses ``Group.permissions.set`` so
    subsequent calls rewrite the baseline exactly.
    """
    from django.contrib.auth.models import Permission

    permission_cache = {}

    def find_perm(app_label, codename):
        key = (app_label, codename)
        if key in permission_cache:
            return permission_cache[key]
        try:
            perm = Permission.objects.get(
                content_type__app_label=app_label, codename=codename)
        except Permission.DoesNotExist:
            permission_cache[key] = None
            return None
        permission_cache[key] = perm
        return perm

    groups = sync_roles()
    for role_code, codes in ROLE_PERMISSION_CODES.items():
        resolved = [find_perm(app_label, codename)
                    for app_label, codename in codes]
        resolved = [perm for perm in resolved if perm is not None]
        groups[role_code].permissions.set(resolved)