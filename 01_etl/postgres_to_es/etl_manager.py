"""
Базовый файл сервиса.

Пошагово запускаются отдельные этапы трансфера данных:
1. Запрашивается время последнего обновленного документа в ES.
2. Загружаются новые данные из Postgres.
3. Данные адаптируются для загрузки в ES.
4. Данные загружаются в ES по частям.
5. После выполнения загрузки в ES каждой части данных происходит
обновление параметр es_modified (время последнего обновленного документа).

"""

import time
from http import HTTPStatus

from extractor import Extractor
from json_state import State
from loader import Loader
from logger import manager_logger as logger
from transformer import Transformer


def transfer():
    # Время последнего обновления данных в ES.
    state = State()
    es_modified = state.get_state('modified_at')

    # Обновленные данные в Postgres.
    extractor = Extractor(es_modified)
    data = extractor.find_modified_data()

    # Преобразование данных для загрузки в ES.
    transformer = Transformer()
    loader = Loader()

    for batch in data:
        data_to_load, modified_at = transformer.transform(batch)

        # Загрузка данных в ES.
        response = loader.connector(data=data_to_load)

        # Изменение значения времени последнего обновления данных в ES.
        if response and response.status_code == HTTPStatus.OK:
            state.set_state('modified_at', modified_at)

    extractor.close_connection()


if __name__ == '__main__':
    while True:
        logger.info('Запуск трансфера данных.')
        transfer()
        logger.info('Трансфер данных завершен.')
        time.sleep(60)
