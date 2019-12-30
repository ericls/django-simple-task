# How It Works

Here's a simple overview of how it works:

1. On application start, a queue is created and a number of workers starts to listen to the queue
2. When `defer` is called, a task(function or coroutine function) is added to the queue
3. When a worker gets a task,  it runs it or delegates it to a threadpool
4. On application shutdown, it waits for tasks to finish before exiting ASGI server

On a more detailed note, `django_simple_task_middlware` hooks up to [ASGI lifespan](https://asgi.readthedocs.io/en/latest/specs/lifespan.html) calls, and on application start up it creates a `asyncio.Queue` and save it as well as the running event loop in [AppConfig](https://docs.djangoproject.com/en/3.0/ref/applications/#django.apps.AppConfig). A number of workers (defaults to 1) would then start  to listen to the queue.  When `django_simple_task.defer` is called, it gets the event loop and queue from `AppConfig` and put the task in the queue by calling `call_soon_threadsafe` on the loop. 

A queue is used here so that we can have more control over concurrency level, and it would be helpful if we want to add more complex things such as retry mechanism. More importantly, on application shutdown, it allows us to make sure the task queues are finished before exiting ASGI server.  
