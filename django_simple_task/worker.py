import logging
from threading import get_ident
from asyncio import Queue, iscoroutinefunction
from typing import Any, Awaitable, Callable, Dict, Optional, Union

from asgiref.sync import sync_to_async

logger = logging.getLogger("DjangoSimpleTaskWorker")
logger.setLevel(logging.DEBUG)


async def run_task(
    func: Union[Callable[[Any], Awaitable], Callable],
    arguments: Optional[Dict],
    options: Optional[Dict],
    queue: Queue,
):
    if arguments is None:
        arguments = {}
    if options is None:
        options = {}
    async_func = func
    if not iscoroutinefunction(func):
        async_func = sync_to_async(
            func, thread_sensitive=options.get("thread_sensitive", False)
        )
    await async_func(*arguments.get("args", []), **arguments.get("kwargs", {}))


async def worker(name: str, queue: Queue):
    ident = get_ident()
    while True:
        func, arguments, options = await queue.get()
        try:
            await run_task(func, arguments, options, queue)
        except Exception:  # pragma: no cover
            logger.exception(f"[Thread: {ident}][Worker: {name}].")
        else:
            logger.info(f"[Thread: {ident}][Worker: {name}]: finished {func.__name__}.")
        finally:
            queue.task_done()
