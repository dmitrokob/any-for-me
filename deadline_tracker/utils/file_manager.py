import json
import os
from typing import List
from models.deadline import Deadline


class FileManager:
    def __init__(self, filename="deadlines.json"):
        self.filename = filename

    def save_deadlines(self, deadlines: List[Deadline]):
        """Сохраняет дедлайны в JSON файл"""
        data = [deadline.to_dict() for deadline in deadlines]

        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise Exception(f"Ошибка сохранения данных: {e}")

    def load_deadlines(self) -> List[Deadline]:
        """Загружает дедлайны из JSON файла"""
        if not os.path.exists(self.filename):
            return []

        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)

            return [Deadline.from_dict(item) for item in data]
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
            return []