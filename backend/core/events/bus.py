import asyncio
import logging
from typing import Any, Callable, Dict, List, Set

logger = logging.getLogger("vas.events")

class EventBus:
    """
    In-memory Event Bus for cross-system, loosely coupled communication.
    Supports both synchronous dispatching for worker threads (e.g., standard def routes)
    and asynchronous background task execution.
    """
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
        self._background_tasks: Set[asyncio.Task] = set()

    def on(self, event_name: str, callback: Callable) -> None:
        """Register a callback for an event."""
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(callback)
        logger.debug(f"Registered listener for event '{event_name}'")

    def dispatch(self, event_name: str, **kwargs: Any) -> None:
        """
        Synchronously dispatch an event.
        Calls each listener registered for the event.
        """
        if event_name not in self._listeners:
            return

        for callback in self._listeners[event_name]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    # If there's a running loop, create a task. Otherwise, run until complete.
                    try:
                        loop = asyncio.get_running_loop()
                        task = loop.create_task(callback(**kwargs))
                        self._background_tasks.add(task)
                        task.add_done_callback(self._background_tasks.discard)
                    except RuntimeError:
                        # No running event loop
                        asyncio.run(callback(**kwargs))
                else:
                    try:
                        loop = asyncio.get_running_loop()
                        loop.run_in_executor(None, lambda cb=callback, kw=kwargs: cb(**kw))
                    except RuntimeError:
                        callback(**kwargs)
            except Exception as e:
                logger.error(f"Error dispatching event '{event_name}' to {callback.__name__}: {e}", exc_info=True)

# Global event bus instance
bus = EventBus()
