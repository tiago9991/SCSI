from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """User manager for the email-based ``core.User``.

    The default Django ``UserManager`` reserves a positional ``username``
    argument and instantiates the model with ``username=...``, which breaks
    for a user without a username field. This manager drives creation via
    ``USERNAME_FIELD`` (e-mail) while keeping the auth app's migration logic
    intact (``use_in_migrations = True``).
    """

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('O e-mail deve ser informado.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    create_user.alters_data = True

    async def _acreate_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('O e-mail deve ser informado.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        await user.asave(using=self._db)
        return user

    async def acreate_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return await self._acreate_user(email, password, **extra_fields)

    acreate_user.alters_data = True

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser deve ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser deve ter is_superuser=True.')
        return self._create_user(email, password, **extra_fields)

    create_superuser.alters_data = True