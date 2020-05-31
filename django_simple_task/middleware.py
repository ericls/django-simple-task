from asyncio import create_task, get_running_loop, Queue
from asgiref.compatibility import guarantee_single_callable

from django.conf import settings


def asgi3_to_asgi2(app):
    def _wrapped_as_asgi2(scope):
        async def _inner(receive, send):
            return await app(scope, receive, send)

        return _inner

    _wrapped_as_asgi2._asgi_double_callable = True
    return _wrapped_as_asgi2


def django_simple_task_middlware(app, *, asgi_version=3):
    from django.apps import apps
    from django_simple_task.worker import worker

    assert asgi_version in (2, 3), "Invalid asgi version"

    async def lifespan_handler(scope, receive, send):
        if scope["type"] == "lifespan":
            app_config = apps.get_app_config("django_simple_task")
            app_config.loop = get_running_loop()
            queue = app_config.queue = Queue()
            while True:
                message = await receive()
                if message["type"] == "lifespan.startup":
                    workers = [
                        create_task(worker(str(i), queue))
                        for i in range(
                            int(getattr(settings, "DJANGO_SIMPLE_TASK_WORKERS", 1))
                        )
                    ]
                    await send({"type": "lifespan.startup.complete"})
                elif message["type"] == "lifespan.shutdown":
                    await queue.join()
                    for w in workers:
                        w.cancel()
                    await send({"type": "lifespan.shutdown.complete"})
                    break
        else:
            return await guarantee_single_callable(app)(scope, receive, send)

    if asgi_version == 2:
        return asgi3_to_asgi2(lifespan_handler)
    return lifespan_handler
