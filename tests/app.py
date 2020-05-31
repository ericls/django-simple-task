from django.core.asgi import get_asgi_application
from django_simple_task import django_simple_task_middlware

from django_simple_task.middleware import asgi3_to_asgi2

application = django_simple_task_middlware(get_asgi_application())

application_wrapping_asgi2 = django_simple_task_middlware(
    asgi3_to_asgi2(get_asgi_application)
)
application_wrapt_as_asgi2 = django_simple_task_middlware(
    get_asgi_application(), asgi_version=2
)
