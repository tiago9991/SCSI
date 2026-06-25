from django.utils.deprecation import MiddlewareMixin


class TenantMiddleware(MiddlewareMixin):
    """Resolve and expose the request's tenant (brokerage).

    The brokerage of the authenticated user is attached to the request as
    ``request.tenant``. Anonymous users (or users not yet linked to a
    brokerage) get ``request.tenant = None``. Downstream views and querysets
    use this attribute to scope data access to the current tenant.

    The brokerage relationship is added to ``core.User`` in the multi-tenant
    sprint; until then this middleware degrades to ``None`` safely so the rest
    of the stack keeps working during onboarding and landing-page flows.
    """

    def process_request(self, request):
        user = getattr(request, 'user', None)
        if user is None or not user.is_authenticated:
            request.tenant = None
            return
        request.tenant = getattr(user, 'brokerage', None)