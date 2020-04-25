from collections import Counter
import concurrent.futures
from itertools import chain
import queue
import random
import signal
import time
from typing import Counter as TypingCounter, Any, Iterable, no_type_check

import attr
import click
from loguru import logger as log

from multiconsumers_queue import ScheduledAction, Producer, Consumer
from multiconsumers_queue.helpers import reset_logger

stats: TypingCounter[str] = Counter()


def log_stats() -> None:
    """Stats logging for ScheduledLogger"""
    log.info(dict(stats))


@attr.s(auto_attribs=True)
class ItemsProducer:
    limit: int

    def get_item(self) -> Iterable[int]:
        """Producer"""
        for _ in range(self.limit):
            yield random.randint(1, 10)
            if random.randint(1, 10) == 7:
                raise ValueError("Producer error")


def process_item(item: int) -> None:
    """Consumer"""
    if item == 3:
        raise ValueError("Value 3 not allowed")
    time.sleep(item)


@no_type_check
@click.command()
@click.option(
    "--workers", help="How many workers will be started", default=5, show_default=True, type=int
)
@click.option(
    "--limit", help="How many items can be produced", default=50, show_default=True, type=int
)
@click.option("--logging-level", help="Logging level", default="INFO", show_default=True, type=str)
def main(**kwargs):
    """Demo script with ThreadPoolExecutor"""

    def receive_signal(_sig_num: int, _frame: Any) -> None:
        log.debug(f"^C signal received")
        producer.stop()

    reset_logger(log, kwargs["logging_level"])
    log.info(f"Started with {kwargs}")
    notifier = ScheduledAction(log_stats, interval=30)
    q: queue.Queue = queue.Queue(kwargs["workers"])
    src = ItemsProducer(kwargs["limit"])
    consumers = [
        Consumer(q, process_item, stats, f"consumer-{idx}") for idx in range(kwargs["workers"])
    ]
    producer = Producer(q, src.get_item, stats, len(consumers))
    signal.signal(signal.SIGINT, receive_signal)
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1 + kwargs["workers"]) as executor:
            futures = {executor.submit(each.run) for each in chain([producer], consumers)}
            concurrent.futures.wait(futures)
        q.join()
    finally:
        notifier.stop()


if __name__ == "__main__":
    main()
