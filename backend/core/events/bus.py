import asyncio
from typing import Callable, Any, Dict, List
import logging

logger = logging.getLogger("vas.events")

class EventBus:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
        self._background_tasks = set()

    def subscribe(self, event_type: str, listener: Callable):
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        if listener not in self._listeners[event_type]:
            self._listeners[event_type].append(listener)
            logger.debug(f"Subscribed {listener.__name__} to {event_type}")

    def unsubscribe(self, event_type: str, listener: Callable):
        if event_type in self._listeners and listener in self._listeners[event_type]:
            self._listeners[event_type].remove(listener)

    async def publish(self, event_type: str, **kwargs: Any):
        logger.info(f"EventBus publishing: {event_type}")
        if event_type in self._listeners:
            for listener in self._listeners[event_type]:
                try:
                    if asyncio.iscoroutinefunction(listener):
                        task = asyncio.create_task(listener(**kwargs))
                        self._background_tasks.add(task)

                        def handle_exception(t):
                            self._background_tasks.discard(t)
                            try:
                                t.result()
                            except Exception as e:
                                logger.error(f"Error inside async event listener for {event_type}: {e}")

                        task.add_done_callback(handle_exception)
                    else:
                        listener(**kwargs)
                except Exception as e:
                    logger.error(f"Error in event listener for {event_type}: {e}")

bus = EventBus()
