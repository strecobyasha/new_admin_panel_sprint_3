"""
Хранения состояния при работе с данными.

Чтобы постоянно не перечитывать данные с начала в json-файл
записывается время изменения последнего обновленного документа.

"""

import json
import os
from typing import Any, Optional


class JsonFileStorage:
    def __init__(self, file_path: Optional[str] = 'state.json'):
        self.file_path = file_path
        self.mode = 'w+'
        if os.path.exists(self.file_path):
            self.mode = 'r+'

    def save_state(self, state: dict) -> None:
        # Сохранить состояние в постоянное хранилище.
        with open(self.file_path, self.mode) as storage:
            try:
                data = json.load(storage)
            except json.decoder.JSONDecodeError:
                data = {}
            new_data = {**data, **state}
            storage.seek(0)
            json.dump(new_data, storage, indent=4, ensure_ascii=False)

    def retrieve_state(self) -> dict:
        # Загрузить состояние локально из постоянного хранилища.
        with open(self.file_path, self.mode) as storage:
            try:
                return json.load(storage)
            except json.decoder.JSONDecodeError:
                data = {'modified_at': '1895-03-22 00:00:00.000000+0300'}
                self.save_state(data)
                return data


class State:
    def __init__(self, storage: JsonFileStorage = JsonFileStorage()):
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        # Установить состояние для определённого ключа.
        self.storage.save_state({key: value})

    def get_state(self, key: str) -> Any:
        # Получить состояние по определённому ключу.
        state = self.storage.retrieve_state()
        return state.get(key)
