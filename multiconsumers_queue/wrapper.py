import queue
import threading
import time
from typing import Any, Optional, Counter as TypingCounter, List, Dict, Callable

import arrow
import attr
from loguru import logger as log


@attr.s(auto_attribs=True)
class Producer:
    """Currently only one producer can be started"""

    q: queue.Queue
    fn: Callable
    stats: TypingCounter[str]  # shared stats counter
    consumers_cnt: int  # we need it for properly shutdown consumers
    name: str = "producer"
    lock: threading.Lock = attr.ib(factory=threading.Lock, repr=False)
    stop_now: bool = False  # External signal can stop producer
    wait_for_queue: float = 0.01  # Minimize CPU load for waiting loop

    def stop_consumers(self) -> None:
        for _ in range(self.consumers_cnt):
            self.q.put(None)

    def run(self) -> None:
        log.debug(f"{self.name} started")
        try:
            for item in self.fn():
                if self.stop_now:
                    log.info(f"{self.name} Stop signal received. Gracefully shutdown")
                    while not self.q.empty():
                        item = self.q.get()
                        self.q.task_done()
                        log.trace(f"{item} dropped")
                        self.stats["items dropped"] += 1
                    break
                while self.q.full():
                    time.sleep(self.wait_for_queue)  # minimize CPU load
                self.q.put(item)
                log.trace(f"{self.name} put {item}")
                with self.lock:
                    self.stats["items produced"] += 1
        except Exception:  # noqa
            log.exception("Unexpected producer error")
            with self.lock:
                self.stats["producer errors"] += 1
        finally:
            self.stop_consumers()
            log.debug(f"{self.name} finished")

    def stop(self) -> None:
        self.stop_now = True


@attr.s(auto_attribs=True)
class Consumer:
    q: queue.Queue
    fn: Callable
    stats: TypingCounter[str]  # shared stats counter
    name: str = "consumer"
    lock: threading.Lock = attr.ib(factory=threading.Lock, repr=False)

    def run(self) -> None:
        log.debug(f"{self.name} started")
        wait_for_items = True
        while wait_for_items:
            item = self.q.get()
            if item is None:
                wait_for_items = False
                self.q.task_done()
            else:
                try:
                    log.trace(f"{self.name} start processing {item}")
                    self.fn(item)
                    log.trace(f"{self.name} done")
                except Exception:  # noqa
                    log.exception("Unexpected consumer error")
                    with self.lock:
                        self.stats["consumer errors"] += 1
                else:
                    with self.lock:
                        self.stats["items consumed"] += 1
                finally:
                    self.q.task_done()
        log.debug(f"{self.name} finished")
