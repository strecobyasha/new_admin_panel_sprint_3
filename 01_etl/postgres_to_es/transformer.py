"""
Преобразование данных для загрузки в ES.

На основе полученных от Postgres данных формируется массив,
пригодный для загрузки в ES. По последнему документу определяется
время изменения данных в ES.

"""

import json


class Transformer:

    def transform(self, batch: list) -> tuple:
        fields = (
            'film_id',
            'rating',
            'title',
            'descr',
            'persons',
            'genres',
            'latest_modified',
            )

        data_str = ''
        modified_at = None

        for film in batch:
            data = dict(zip(fields, film))
            persons_dict = self.get_persons_dict(data.get('persons'))

            modified_at = data.get('latest_modified').strftime('%Y-%m-%d %H:%M:%S.%f%z')

            data_str += json.dumps(
                {
                    'index': {
                        '_index': 'movies',
                        '_id': data.get('film_id'),
                    },
                },
            ) + '\n'

            data_str += json.dumps(
                {
                    'id': data.get('film_id'),
                    'imdb_rating': data.get('rating'),
                    'genre': data.get('genres'),
                    'title': data.get('title'),
                    'description': data.get('descr'),
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
