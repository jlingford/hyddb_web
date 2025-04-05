from django.apps import AppConfig


class ClassifierConfig(AppConfig):
    name = 'classifier'
    verbose_name = 'Classifier'

    def ready(self):
        from . import handlers
