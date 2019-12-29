from asyncio import Queue
from typing import Any, Awaitable, Callable, Dict, Optional, Union

from django.apps import apps


def defer(
    func: Union[Callable[[Any], Awaitable], Callable],
    arguments: Optional[Dict] = None,
    *,
    options: Optional[Dict] = None
):
    app_config = apps.get_app_config("django_simple_task")
    queue: Queue = app_config.queue
    loop = app_config.loop
    if loop:
        loop.call_soon_threadsafe(queue.put_nowait, (func, arguments, options))
