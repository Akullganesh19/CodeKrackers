import asyncio
import logging
from typing import Callable, Dict, List, Any, Set

logger = logging.getLogger("vas.events.bus")


class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._background_tasks: Set[asyncio.Task] = set()

    def subscribe(self, event_type: str, callback: Callable) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.info(f"Subscribed to event: {event_type}")

    def publish(self, event_type: str, data: Any = None) -> None:
        if event_type not in self._subscribers:
            return

        for callback in self._subscribers[event_type]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    # Check if there is a running event loop
                    try:
                        loop = asyncio.get_running_loop()
                        task = loop.create_task(callback(data))
                        self._background_tasks.add(task)
                        task.add_done_callback(self._background_tasks.discard)
                    except RuntimeError:
                        # No running event loop (e.g. called from synchronous endpoint thread)
                        asyncio.run(callback(data))
                else:
                    callback(data)
            except Exception as e:
                logger.error(f"Error in event handler for {event_type}: {e}")


event_bus = EventBus()
