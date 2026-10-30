import asyncio
import logging
from collections import defaultdict
from typing import Callable, Coroutine, Dict, List, Any

logger = logging.getLogger("vas.events")

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[..., Coroutine[Any, Any, Any]]]] = defaultdict(list)

    def subscribe(self, event_type: str, callback: Callable[..., Coroutine[Any, Any, Any]]):
        self._subscribers[event_type].append(callback)
        logger.debug(f"Subscribed to {event_type}")

    async def publish(self, event_type: str, *args, **kwargs):
        if event_type not in self._subscribers:
            return

        logger.info(f"Publishing event: {event_type}")
        tasks = []
        for callback in self._subscribers[event_type]:
            tasks.append(callback(*args, **kwargs))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

event_bus = EventBus()
