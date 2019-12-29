from .task import defer
from .middleware import django_simple_task_middlware

__all__ = ["defer", "django_simple_task_middlware"]
__version__ = "0.1.0"

default_app_config = "django_simple_task.apps.DjangoSimpleTaskConfig"
