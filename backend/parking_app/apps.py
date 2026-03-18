"""Apps configuration for parking app."""
from django.apps import AppConfig


class ParkingAppConfig(AppConfig):
    """Configuration for parking app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'parking_app'
    verbose_name = 'Parking Management'
