import asyncio
from typing import Callable, Dict, List, Any

class EventBus:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}

    def on(self, event_name: str, callback: Callable):
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(callback)

    async def emit(self, event_name: str, *args: Any, **kwargs: Any):
        if event_name in self._listeners:
            for cb in self._listeners[event_name]:
                try:
                    if asyncio.iscoroutinefunction(cb):
                        await cb(*args, **kwargs)
                    else:
                        cb(*args, **kwargs)
                except Exception as e:
                    import logging
                    logging.getLogger("vas.event_bus").error(f"Error in event listener for {event_name}: {e}")  # noqa

bus = EventBus()
