import asyncio
import logging
from typing import Callable, Any, Dict, List, Set

logger = logging.getLogger("vas.events")


class EventBus:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
        self._background_tasks: Set[asyncio.Task] = set()

    def subscribe(self, event_name: str, callback: Callable):
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(callback)

    def publish(self, event_name: str, **kwargs: Any):
        if event_name not in self._listeners:
            return

        for callback in self._listeners[event_name]:
            if asyncio.iscoroutinefunction(callback):
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    # If we are not in an async context, we have to run it synchronously
                    # Though ideally, event bus publish should be async if it calls async callbacks
                    # Or we just run it synchronously
                    # We will log error and skip for now if no loop
                    logger.error(
                        f"Cannot run async callback {callback} for event {event_name} outside of an event loop."
                    )
                    continue
                task = loop.create_task(callback(**kwargs))
                self._background_tasks.add(task)
                task.add_done_callback(self._background_tasks.discard)
            else:
                try:
                    callback(**kwargs)
                except Exception as e:
                    logger.error(
                        f"Error executing synchronous listener for event {event_name}: {e}",
                        exc_info=True,
                    )


event_bus = EventBus()
