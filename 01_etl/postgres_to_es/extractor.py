"""
Загрузчик данных из Postgres.

1. Получает на вход дату последнего обновления данных в ES.

2. Подключается к БД.

3. Первый запрос на получение всех id фильмов, для которых были изменены:
сами фильмы, персоны или жанры, относящиеся к фильмам.

4. Второй запрос: получение этих же фильмов, но с полным набором данных
(первый запрос не позволяет получить данные, напр., об актерах, которые
были изменены до целевой даты).
Сортировка фильмов происходит по наиболее поздней дате изменения:
самого фильма, персон или жанров.

5. Возвращает данные, которые нужно преобразовать перед загрузкой в ES.

"""

from datetime import datetime
from typing import Generator

import psycopg2
from pydantic import BaseSettings, Field

from backoff import backoff
from logger import extractor_logger as logger

BATCH_SIZE = 100


class Settings(BaseSettings):
    dbname: str = Field(..., env='DB_NAME')
    user: str = Field(..., env='DB_USER')
    password: str = Field(..., env='DB_PASSWORD')
    host: str = Field(..., env='DB_HOST')
    port: int = Field(..., env='DB_PORT')
    options: str = '-c search_path=content'

    class Config:
        env_file = '.env'


settings = Settings().dict()


class Extractor:

    def __init__(self, modified_from: str):
        self.modified_from = datetime.strptime(modified_from, '%Y-%m-%d %H:%M:%S.%f%z')
        self.conn = None
        self.curs = None
        self.connect()

    @backoff(logger=logger, log_msg='Не удалось установить соединение с БД.')
    def connect(self):
        self.conn = psycopg2.connect(**settings)
        self.curs = self.conn.cursor()

    def close_connection(self):
        if self.conn:
            self.conn.close()

    def executor(self, query: str, condition: tuple) -> None:
        # Выполнение запроса к БД на получение списка id фильмов
        # или на получение списка документов.
        try:
            self.curs.execute(query, condition)
        except psycopg2.OperationalError:
            logger.error('Соединение с БД оборвалось в процессе выполнения запроса.')
            self.connect()
            self.executor(query, condition)

    def find_modified_data(self) -> Generator:
        # Запрос на получение id измененных фильмов.
        query = """
            WITH vars(mod_time) as (values (%s))
            SELECT F.id
            FROM vars, film_work F
            LEFT JOIN person_film_work PFW on F.id = PFW.film_work_id
            LEFT JOIN person P on P.id = PFW.person_id
            LEFT JOIN genre_film_work GFW on F.id = GFW.film_work_id
            LEFT JOIN genre G on G.id = GFW.genre_id
            WHERE (F.modified > mod_time OR P.modified > mod_time OR G.modified > mod_time)
            GROUP BY F.id;
            """

        self.executor(query, (self.modified_from,))
        film_ids = tuple(self.curs.fetchall())

        # Запрос на получение измененных документов.
        query = """
            SELECT F.id, rating, title, F.description,
            ARRAY_AGG(DISTINCT(P.id || '|' || P.full_name || '|' || PFW.role)),
            ARRAY_AGG(DISTINCT(G.name)),
            GREATEST(MAX(P.modified), MAX(G.modified), F.modified) as latest_modified
            FROM film_work F
            LEFT JOIN person_film_work PFW on F.id = PFW.film_work_id
            LEFT JOIN person P on P.id = PFW.person_id
            LEFT JOIN genre_film_work GFW on F.id = GFW.film_work_id
            LEFT JOIN genre G on G.id = GFW.genre_id
            WHERE F.id IN %s
            GROUP BY F.id
            ORDER BY latest_modified;
            """

        if len(film_ids) > 0:
            self.executor(query, (film_ids,))
            while results := self.curs.fetchmany(BATCH_SIZE):
                yield results
