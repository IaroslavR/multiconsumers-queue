"""Wrapper for queue based producer/consumers."""
from __future__ import annotations

from collections import Counter
import concurrent.futures
from itertools import chain
import queue
import threading
import time
import typing

import attr
from loguru import logger as log

from multiconsumers_queue.helpers import ScheduledAction


@attr.s(auto_attribs=True)
class Producer:
    """Wrapper for data source function.

    Args:
        q: Queue fot interconnection
        fn: Real producer
        stats: Shared counter with statistics
        consumers_cnt: How many consumers to start
        name: Process name
        lock: Lock for shared counter
        stop_now: Stop flag.If set it to True then consumers will be stopped
        wait_for_queue: sleep time for preventing CPU throttling
    """

    q: queue.Queue
    fn: typing.Callable[[], typing.Iterator[typing.Any]]
    stats: typing.Counter[str]
    consumers_cnt: int  # we need it for properly shutdown consumers
    name: str = "producer"
    lock: threading.Lock = attr.ib(factory=threading.Lock, repr=False)
    stop_now: bool = False  # External signal can stop producer
    wait_for_queue: float = 0.01  # Minimize CPU load for waiting loop

    def stop_consumers(self) -> None:
        """Send None to the consumers."""
        for _ in range(self.consumers_cnt):
            self.q.put(None)

    def run(self) -> None:
        """Start Producer."""
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
                    time.sleep(self.wait_for_queue)
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
        """Interrupt Producer."""
        self.stop_now = True


@attr.s(auto_attribs=True)
class Consumer:
    """Wrapper for data processing function.

    Args:
        q: Queue fot interconnection
        fn: Real producer
        stats: Shared counter with statistics
        name: Process name
        lock: Lock for shared counter
    """

    q: queue.Queue
    fn: typing.Callable
    stats: typing.Counter[str]
    name: str = "consumer"
    lock: threading.Lock = attr.ib(factory=threading.Lock, repr=False)

    def run(self) -> None:
        """Start Consumer."""
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


@attr.s(auto_attribs=True)
class ThreadPool:
    """Producer/Consumers thread pool.

    Args:
        src: Producer fn
        dst: Consumer fn
        notifier: ScheduledAction fn
        notification_interval: time between notifications in seconds
        consumers_cnt: How many consumers to start
        q: Queue fot interconnection
        stats: Shared counter with statistics
        producer: Producer
        consumers: list of Consumer objects
    """

    src: typing.Callable[[], typing.Iterator[typing.Any]]  # real producer
    dst: typing.Callable  # real consumer
    notifier: typing.Callable
    notification_interval: typing.Union[int, float] = 60
    consumers_cnt: int = 5
    q: queue.Queue = attr.ib()
    stats: typing.Counter[str] = attr.ib(factory=Counter)
    producer: Producer = attr.ib()
    consumers: typing.List[Consumer] = attr.ib()

    @consumers.default  # noqa
    def init_consumers(self) -> typing.List[Consumer]:
        """Init Consumer.

        Returns:
            List[Consumer]
        """
        return [
            Consumer(self.q, self.dst, self.stats, f"consumer-{idx}")
            for idx in range(self.consumers_cnt)
        ]

    @producer.default  # noqa
    def init_producer(self) -> Producer:
        """Init Producer.

        Returns:
            Producer
        """
        return Producer(self.q, self.src, self.stats, self.consumers_cnt)

    @q.default  # noqa
    def init_queue(self) -> queue.Queue:
        """Init queue.

        Returns:
            queue.Queue
        """
        return queue.Queue(self.consumers_cnt)

    def run(self) -> None:
        """Start processing."""
        workers: chain[typing.Union[Producer, Consumer]] = chain([self.producer], self.consumers)
        notifier = ScheduledAction(self.notifier, notification_interval=self.notification_interval)
        try:
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=1 + self.consumers_cnt
            ) as executor:
                futures = {executor.submit(each.run) for each in workers}
                concurrent.futures.wait(futures)
            self.q.join()
        finally:
            notifier.stop()
