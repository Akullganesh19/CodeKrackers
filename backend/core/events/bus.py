import asyncio
import inspect
import logging
from typing import Any, Callable, Dict, List

logger = logging.getLogger("vas.event_bus")

class _EventBus:
    """
    In-memory Event Bus for loosely coupled cross-system intelligence.
    Supports both sync and async listeners.
    """
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
        # Hard reference to prevent premature garbage collection of background tasks
        self._background_tasks = set()

    def on(self, event_name: str):
        """Decorator to register an event listener."""
        def decorator(func: Callable):
            if event_name not in self._listeners:
                self._listeners[event_name] = []
            self._listeners[event_name].append(func)
            logger.info("Event listener registered for '%s': %s", event_name, func.__name__)
            return func
        return decorator

    def emit(self, event_name: str, **kwargs: Any):
        """Emits an event to all registered listeners."""
        logger.info("Event emitted: '%s' with args: %s", event_name, kwargs)

        if event_name not in self._listeners:
            return

        for listener in self._listeners[event_name]:
            try:
                if inspect.iscoroutinefunction(listener):
                    # It's an async listener, schedule it in the background
                    try:
                        loop = asyncio.get_running_loop()
                        task = loop.create_task(listener(**kwargs))
                        self._background_tasks.add(task)
                        task.add_done_callback(self._background_tasks.discard)
                    except RuntimeError:
                        # No running event loop (e.g., sync context in thread)
                        # We should run it synchronously if possible, but usually async listeners
                        # expect an event loop.
                        logger.error(
                            "Cannot schedule async listener '%s' for event '%s': No running event loop.",
                            listener.__name__, event_name
                        )
                else:
                    # Sync listener, execute immediately
                    listener(**kwargs)
            except Exception as e:
                logger.error("Error executing listener '%s' for event '%s': %s", listener.__name__, event_name, e, exc_info=True)


# Singleton instance
EventBus = _EventBus()
