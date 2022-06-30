"""
Декоратор перезагрузки функции.

В случае неудачного подключения к БД или ES
предпринимаются повторные попытки с увеличивающимся
интервалом. По достижении предельного времени ожидания (border_sleep_time)
таймаут не увеличивается.

"""

import time
from functools import wraps

from logger import extractor_logger, loader_logger


def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10):
    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            sleep_time = kwargs.get('sleep_time', start_sleep_time)
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as ex:
                    if type(ex).__name__ == 'OperationalError':
                        extractor_logger.error('Не удалось установить соединение с БД.')
                    else:
                        print('error', sleep_time)
                        loader_logger.error('Ошибка выполнения запроса к ES.')
                    time.sleep(min(sleep_time, border_sleep_time))
                    sleep_time *= factor

        return inner

    return func_wrapper
