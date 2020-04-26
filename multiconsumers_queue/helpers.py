"""Miscellaneous helpers."""
from __future__ import annotations

import sys
import threading
from typing import Any, Callable, Dict, List, Optional, Union

import arrow
import attr
from loguru import logger, logger as log


def reset_logger(level: str) -> None:
    """Customize logging output.

    Args:
        level: logging level

    """
    logger.remove()
    kwargs = dict(
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> <level>{message}</level>",
        level=level,
        backtrace=False,
        diagnose=False,
    )
    if level in ["DEBUG", "TRACE"]:
        kwargs.update({"backtrace": True, "diagnose": True})
    logger.add(sink=sys.stderr, **kwargs)  # type: ignore


@attr.s(auto_attribs=True)
class ScheduledAction(object):
    """Helper for action that should be run only after a certain amount of time has passed.

    Args:
        fn: Callable for execute
        args: Callable args
        kwargs: Callable kwargs
        notification_interval: time between fn calls in seconds
        is_running: Running state flag
        timer: Timer
        start_time: Starting time
        stop_time: Stopping time
    """

    fn: Callable
    args: List = []
    kwargs: Dict[str, Any] = {}
    notification_interval: Union[int, float] = 60  # every minute
    is_running: bool = False
    timer: threading.Timer = attr.ib()
    start_time: arrow.arrow.Arrow = attr.ib()
    stop_time: Optional[arrow.arrow.Arrow] = None

    @timer.default  # noqa
    def init_timer(self) -> threading.Timer:
        """Start new timer.

        Returns:
            threading.Timer
        """
        return threading.Timer(self.notification_interval, self._run)

    @start_time.default
    def start(self) -> arrow.arrow.Arrow:
        """Set action starting time.

        Returns:
            arrow.arrow.Arrow
        """
        self._start()
        return arrow.get()

    def _run(self) -> None:
        self.is_running = False
        self._start()
        self.fn(*self.args, **self.kwargs)

    def _start(self) -> None:
        if not self.is_running:
            self.timer = self.init_timer()
            self.timer.start()
            self.is_running = True

    def stop(self) -> None:
        """Stop timer."""
        self.timer.cancel()
        self.is_running = False
        self.stop_time = arrow.get()
        self.fn(*self.args, **self.kwargs)
        log.info(f"Execution time {self.stop_time - self.start_time}")
