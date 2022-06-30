"""
Загрузчик данных в индекс movies ES.

При создании объекта Loader происходит проверка существования индекса.
Если индекс не сушествует, он создается.

В случае отсутствия соединения с ES рекурсивно вызывается функция connector
с увеличивающимся интервалом времени.

При загрузке данных в индекс функция connector отдает код ответа
(или None, если ES не доступен). Только если код ответа 200
в постоянное хранилище запишется время последнего обновления.

"""

import json
import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

from backoff import backoff
from es_index import index

path = Path(__file__).resolve().parent
load_dotenv(''.join([str(path), '/.env']))


class Loader:

    def __init__(self):
        self.host = os.environ.get('ES_HOST')
        self.port = os.environ.get('ES_PORT')
        # Проверка существования индекса при первом подключении.
        self.connector(req='get', tail='/_cat/indices/movies')

    @backoff()
    def connector(self, **kwargs) -> Any:
        req = kwargs.get('req', 'post')             # Тип запроса: get, put, post.
        tail = kwargs.get('tail', '/movies/_bulk')  # Хвост адреса для запроса.
        data = kwargs.get('data', None)

        request_method = getattr(requests, req)
        url = self.host + ':' + self.port + tail
        headers = {'Content-Type': 'application/json'}

        response = request_method(url, data=data, headers=headers)

        if req == 'get' and response.status_code != 200:
            # Создание индекса.
            self.connector(req='put', tail='/movies', data=json.dumps(index))
        return response
