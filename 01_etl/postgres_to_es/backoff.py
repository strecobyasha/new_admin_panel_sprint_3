"""
Декоратор перезагрузки функции.

В случае неудачного подключения к БД или ES
предпринимаются повторные попытки с увеличивающимся
интервалом. По достижении предельного времени ожидания (border_sleep_time)
таймаут не увеличивается.

"""

import time
from functools import wraps

from logger import manager_logger


def backoff(
    logger: object = manager_logger,
    log_msg: str = '',
    start_sleep_time=0.1,
    factor=2,
    border_sleep_time=10,
):
    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            sleep_time = kwargs.get('sleep_time', start_sleep_time)
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as ex:
                    logger.error(f'{log_msg}, {ex}')
                    time.sleep(min(sleep_time, border_sleep_time))
                    sleep_time *= factor

        return inner

    return func_wrapper
