from django.apps import AppConfig


class BaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base'
    verbose_name = 'Recursos compartilhados'

    def ready(self):
        # Connect a post_migrate receiver that keeps the role ``Group``s and
        # their baseline permissions in sync with the code. Runs after Django
        # has created all ``ContentType`` / ``Permission`` rows so the
        # permission lookups resolve.
        from django.db.models.signals import post_migrate
        from base.permissions import sync_roles, sync_role_permissions

        def _post_migrate_receiver(sender, **kwargs):
            # Only react when the running app is to migrate (kept simple:
            # always sync — both helpers are idempotent).
            sync_roles()
            sync_role_permissions()

        post_migrate.connect(_post_migrate_receiver, dispatch_uid='base.sync_roles')