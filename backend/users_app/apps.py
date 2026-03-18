"""Apps configuration for users app."""
from django.apps import AppConfig


class UsersAppConfig(AppConfig):
    """Configuration for users app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users_app'
    verbose_name = 'Users Management'
