# Django Simple Task
[![Github Actions](https://github.com/ericls/django-simple-task/workflows/Build/badge.svg)](https://github.com/ericls/django-simple-task/actions)
[![Code Coverage](https://codecov.io/gh/ericls/django-simple-task/branch/master/graph/badge.svg)](https://codecov.io/gh/ericls/django-simple-task)
[![Python Version](https://img.shields.io/pypi/pyversions/django-simple-task.svg)](https://pypi.org/project/django-simple-task/)
[![PyPI Package](https://img.shields.io/pypi/v/django-simple-task.svg)](https://pypi.org/project/django-simple-task/)
[![License](https://img.shields.io/pypi/l/django-simple-task.svg)](https://github.com/ericls/django-simple-task/blob/master/LICENSE.md)

`django-simple-task` runs background tasks in Django 3 without requiring other services and workers. It runs them in the same event loop as your ASGI application. It is not resilient as a proper task runner such as Celery, but works for some simple tasks and has less overall overheads.

## Guide

Install the package:
```bash
pip install django-simple-task
```

Added it to installed apps:
```python
# settings.py
INSTALLED_APPS = [
	...
	'django_simple_task'
]
```
Apply ASGI middleware :
```python
# asgi.py
from django_simple_task import django_simple_task_middlware
application = django_simple_task_middlware(application)
```

Call a background task in Django view:
```python
from django_simple_task import defer

def task1():
	time.sleep(1)
	print("task1 done")

async def task2():
	await asyncio.sleep(1)
	print("task2 done")

def view(requests):
	defer(task1)
	defer(task2)
	return HttpResponse(b"My View")
```

It is required to run Django with ASGI server. [Official Doc](https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/)

## Configurations

Concurrency level can be controlled by adding `DJANGO_SIMPLE_TASK_WORKERS` to settings. Defaults to `1`.