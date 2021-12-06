from django.apps import AppConfig
from google.cloud import firestore


class HfResaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hf_alerts'
    db = None

    def ready(self):
        self.db = firestore.Client(project="alert-everywhere")
