import threading
from typing import Callable, List, Dict, Any, Optional

import arrow
import attr
from loguru import logger as log


@attr.s(auto_attribs=True)
class ScheduledAction(object):
    function: Callable
    args: List = []
    kwargs: Dict[str, Any] = {}
    interval: int = 60  # every minute
    is_running: bool = False
    timer: threading.Timer = attr.ib()
    start_time: arrow.arrow.Arrow = attr.ib()
    stop_time: Optional[arrow.arrow.Arrow] = None

    @timer.default  # noqa
    def init_timer(self) -> threading.Timer:
        return threading.Timer(self.interval, self._run)

    @start_time.default
    def start(self) -> arrow.arrow.Arrow:
        self._start()
        return arrow.get()

    def _run(self) -> None:
        self.is_running = False
        self._start()
        self.function(*self.args, **self.kwargs)

    def _start(self) -> None:
        if not self.is_running:
            self.timer = self.init_timer()
            self.timer.start()
            self.is_running = True

    def stop(self) -> None:
        self.timer.cancel()
        self.is_running = False
        self.stop_time = arrow.get()
        self.function(*self.args, **self.kwargs)
        log.info(f"Execution time {self.stop_time - self.start_time}")
