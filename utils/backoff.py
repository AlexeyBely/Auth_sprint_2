from functools import wraps
from logging import Logger
from time import sleep

from logger import logger as default_logger


def backoff(start_sleep_time: float = 0.1,
            factor: int = 2,
            border_sleep_time: float = 10,
            logger: Logger = default_logger) -> callable:
    """
    The decorator to re-execute a function after some time if an exception was raised.
    It uses a naive exponential increasing of the repeating time.

    Formula:
        t = start_sleep_time * factor^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time

    :param no_raise_exceptions: the list of exceptions that will not be raised
    :param start_sleep_time: the start time of the repeating
    :param factor: the multiplier to increase the delay time
    :param border_sleep_time: the max delay time
    :param logger: custom logger
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            sleep_time = start_sleep_time if start_sleep_time < border_sleep_time else border_sleep_time
            while True:
                try:
                    res = func(*args, **kwargs)
                    return res
                except Exception as e:
                    logger.warning(f'An exception occurred. Next attempt in {sleep_time} seconds.\n{e}')
                    sleep(sleep_time)
                    sleep_time *= factor
                    if sleep_time > border_sleep_time:
                        sleep_time = border_sleep_time
        return inner
    return func_wrapper
