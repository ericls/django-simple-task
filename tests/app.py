from django.core.asgi import get_asgi_application
from django_simple_task import django_simple_task_middlware

application = django_simple_task_middlware(get_asgi_application())
