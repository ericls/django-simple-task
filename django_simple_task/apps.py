from django.apps import AppConfig


class DjangoSimpleTaskConfig(AppConfig):
    name = "django_simple_task"
    verbose_name = "Django Simple Task"

    def ready(self):
        self.loop = None
        self.queue = None
