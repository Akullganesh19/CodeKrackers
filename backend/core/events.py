import asyncio
import logging
from typing import Callable, Dict, List, Any

logger = logging.getLogger("vas.events")

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    async def publish(self, event_type: str, *args, **kwargs):
        if event_type not in self._subscribers:
            return

        for callback in self._subscribers[event_type]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(*args, **kwargs))
                else:
                    loop = asyncio.get_running_loop()
                    loop.run_in_executor(None, lambda cb=callback: cb(*args, **kwargs))
            except Exception as e:
                logger.error(f"Error publishing {event_type} to subscriber {callback}: {e}")

event_bus = EventBus()
