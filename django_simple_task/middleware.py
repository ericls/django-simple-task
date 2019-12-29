from asyncio import create_task, get_running_loop, Queue

from django.conf import settings


def django_simple_task_middlware(app):
    from django.apps import apps
    from django_simple_task.worker import worker

    async def lifespan_handler(scope, receive, send):
        if scope["type"] == "lifespan":
            app_config = apps.get_app_config("django_simple_task")
            app_config.loop = get_running_loop()
            queue = app_config.queue = Queue(loop=app_config.loop)
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
            return await app(scope, receive, send)

    return lifespan_handler
