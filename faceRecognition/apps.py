from django.apps import AppConfig

class FaceRecognitionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'faceRecognition'

    def ready(self):
        import faceRecognition.signal
