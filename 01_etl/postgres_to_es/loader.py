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
from http import HTTPStatus
from typing import Any

import requests
from pydantic import BaseSettings, Field

from backoff import backoff
from es_index import index
from logger import loader_logger as logger


class Settings(BaseSettings):
    host: str = Field(..., env='ES_HOST')
    port: int = Field(..., env='ES_PORT')

    class Config:
        env_file = '.env'


class Loader:

    def __init__(self):
        self.params = Settings().dict()
        self.host = self.params.get('host')
        self.port = self.params.get('port')
        # Проверка существования индекса при первом подключении.
        self.connector(req='get', tail='/_cat/indices/movies')

    @backoff(logger=logger, log_msg='Ошибка выполнения запроса к ES.')
    def connector(
        self,
        req: str = 'post',
        tail: str = '/movies/_bulk',
        data: Any = None,
    ) -> Any:
        # req: тип запроса (get, put, post).
        # tail: хвост адреса для запроса.
        request_method = getattr(requests, req)
        url = ''.join([self.host, ':', str(self.port), tail])
        print(url)
        headers = {'Content-Type': 'application/json'}

        response = request_method(url, data=data, headers=headers)

        if req == 'get' and response.status_code == HTTPStatus.NOT_FOUND:
            # Создание индекса.
            self.connector(req='put', tail='/movies', data=json.dumps(index))
            logger.info('Индекс ES создан.')
        return response
