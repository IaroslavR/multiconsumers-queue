import random
import signal
import time
from typing import Any, no_type_check, Iterator

import attr
import click
from loguru import logger as log

from multiconsumers_queue import Pool
from multiconsumers_queue.helpers import reset_logger


@attr.s(auto_attribs=True)
class ItemsProducer:
    limit: int

    def get_item(self) -> Iterator[int]:
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

    def log_stats() -> None:
        """Stats logging for ScheduledLogger"""
        log.info(dict(pool.stats))

    def receive_signal(_sig_num: int, _frame: Any) -> None:
        """^C handler"""
        log.debug(f"^C signal received")
        pool.producer.stop()

    reset_logger(log, kwargs["logging_level"])
    log.info(f"Started with {kwargs}")
    src = ItemsProducer(kwargs["limit"])
    pool = Pool(src.get_item, process_item, log_stats, 30)
    signal.signal(signal.SIGINT, receive_signal)
    pool.run()


if __name__ == "__main__":
    main()
