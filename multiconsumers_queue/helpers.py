from __future__ import annotations

import sys

import loguru


def reset_logger(logger: loguru.Logger, level: str) -> None:
    """Customize logging output"""
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
