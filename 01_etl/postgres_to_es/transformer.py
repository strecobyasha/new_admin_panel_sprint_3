"""
Преобразование данных для загрузки в ES.

На основе полученных от Postgres данных формируется массив,
пригодный для загрузки в ES. По последнему документу определяется
время изменения данных в ES.

"""

import json
import uuid
from datetime import datetime
from typing import Any

from pydantic.dataclasses import dataclass


@dataclass
class Film:
    film_id: uuid.UUID
    rating: Any
    title: str
    descr: Any
    persons: list
    genres: list
    latest_modified: datetime


class Transformer:

    def transform(self, batch: list) -> tuple:

        data_str = ''
        modified_at = None

        for film in batch:
            film_data = Film(*film)
            persons_dict = self.get_persons_dict(film_data.persons)

            modified_at = film_data.latest_modified.strftime('%Y-%m-%d %H:%M:%S.%f%z')

            data_str += json.dumps(
                {
                    'index': {
                        '_index': 'movies',
                        '_id': str(film_data.film_id),
                    },
                },
            ) + '\n'

            data_str += json.dumps(
                {
                    'id': str(film_data.film_id),
                    'imdb_rating': film_data.rating,
                    'genre': film_data.genres,
                    'title': film_data.title,
                    'description': film_data.descr,
                    'director': persons_dict['director'],
                    'actors_names': persons_dict['actors_names'],
                    'writers_names': persons_dict['writers_names'],
                    'actors': persons_dict['actors'],
                    'writers': persons_dict['writers'],
                },
            ) + '\n'

        return data_str, modified_at

    def get_persons_dict(self, persons: list) -> dict:
        # Распределение персон фильма по их функциям.
        persons_dict = {
            'director': [],
            'actors_names': [],
            'writers_names': [],
            'actors': [],
            'writers': [],
            }

        for person in filter(lambda x: x is not None, persons):
            id, name, role = person.split('|')
            match role:
                case 'actor':
                    persons_dict['actors_names'].append(name)
                    persons_dict['actors'].append({'id': id, 'name': name})
                case 'writer':
                    persons_dict['writers_names'].append(name)
                    persons_dict['writers'].append({'id': id, 'name': name})
                case 'director':
                    persons_dict['director'].append(name)

        return persons_dict
