"""Demo script with ThreadPoolExecutor and ^C handler."""

import random
import signal
import time
from typing import Any, Iterator, no_type_check

import attr
import click
from loguru import logger as log

from multiconsumers_queue import ThreadPool
from multiconsumers_queue.helpers import reset_logger


@attr.s(auto_attribs=True)
class ItemsProducer:
    """Example of Producer with initialization before start."""

    limit: int

    def get_item(self) -> Iterator[int]:
        """Producer.

        Yields:
            int

        Raises:
            ValueError: random error
        """
        for _ in range(self.limit):
            yield random.randint(1, 10)  # noqa: S311
            if random.randint(1, 10) == 7:  # noqa: S311
                raise ValueError("Producer error")


def process_item(item: int) -> None:
    """Consumer.

    Args:
        item: Item to process

    Raises:
        ValueError: random error
    """
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
def main(**kwargs) -> None:
    """Demo script with ThreadPoolExecutor.

    Args:
        **kwargs: arguments from click
    """

    def log_stats() -> None:
        """Stats logging for ScheduledLogger."""
        log.info(dict(pool.stats))

    def receive_signal(_sig_num: int, _frame: Any) -> None:
        """^C handler.

        Args:
            _sig_num: Signal as int
            _frame: Current stack frame

        References:
            https://docs.python.org/3/library/signal.html#signal.signal
        """
        log.debug(f"^C signal received")
        pool.producer.stop()

    reset_logger(kwargs["logging_level"])
    log.info(f"Started with {kwargs}")
    src = ItemsProducer(kwargs["limit"])
    pool = ThreadPool(src.get_item, process_item, log_stats, 30)
    signal.signal(signal.SIGINT, receive_signal)
    pool.run()


if __name__ == "__main__":
    main()
