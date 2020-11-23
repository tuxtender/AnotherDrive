from django.apps import AppConfig

class FilestorageConfig(AppConfig):
    name = 'filestorage'

    def ready(self):
        import filestorage.signals
