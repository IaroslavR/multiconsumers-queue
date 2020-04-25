from collections import Counter
import concurrent.futures
import queue
import time
from typing import Counter as TypingCounter

from loguru import logger as log

from multiconsumers_queue import __version__, Producer, Consumer
from multiconsumers_queue.helpers import reset_logger

reset_logger(log, "TRACE")


def test_version():
    assert __version__ == "0.1.0"


def test_producer_ok():
    def get_item():
        yield 1

    stats: TypingCounter[str] = Counter()
    q: queue.Queue = queue.Queue()
    p = Producer(consumers_cnt=2, q=q, stats=stats, fn=get_item)
    p.run()
    assert stats == {"items produced": 1}
    assert q.get() == 1
    assert q.get() is None
    assert q.get() is None
    assert q.empty()


def test_producer_exception():
    def get_item():
        raise ValueError

    stats: TypingCounter[str] = Counter()
    q: queue.Queue = queue.Queue()
    p = Producer(consumers_cnt=1, q=q, stats=stats, fn=get_item)
    p.run()
    assert stats == {"producer errors": 1}
    assert q.get() is None
    assert q.empty()


def test_consumer_ok():
    def process_item(item):
        pass

    stats: TypingCounter[str] = Counter()
    q: queue.Queue = queue.Queue()
    c = Consumer(q, process_item, stats)
    q.put(1)
    q.put(None)
    c.run()
    assert stats == {"items consumed": 1}
    assert q.empty()


def test_consumer_exception():
    def process_item(item):
        if item == 2:
            raise ValueError

    stats: TypingCounter[str] = Counter()
    q: queue.Queue = queue.Queue()
    c = Consumer(q, process_item, stats)
    q.put(2)
    q.put(1)
    q.put(None)
    c.run()
    assert stats == {"consumer errors": 1, "items consumed": 1}
    assert q.empty()


def test_producer_stop():
    def get_item():
        yield 1
        yield 2
        yield 3
        p.stop()
        yield 4

    def process_item(item):
        time.sleep(0.1)
        return

    stats: TypingCounter[str] = Counter()
    q: queue.Queue = queue.Queue(1)
    p = Producer(consumers_cnt=1, q=q, stats=stats, fn=get_item)
    c = Consumer(q, process_item, stats)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = {executor.submit(each.run) for each in [p, c]}
        concurrent.futures.wait(futures)
    assert stats == {"items produced": 3, "items consumed": 2, "items dropped": 1}
    assert q.empty()
