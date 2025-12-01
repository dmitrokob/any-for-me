from datetime import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class Deadline:
    name: str
    deadline: datetime
    days_needed: Optional[int] = None
    created: Optional[datetime] = None

    def __post_init__(self):
        if self.created is None:
            self.created = datetime.now()

    def to_dict(self):
        """Конвертирует в словарь для сохранения"""
        return {
            "name": self.name,
            "deadline": self.deadline.isoformat(),
            "days_needed": self.days_needed,
            "created": self.created.isoformat()
        }

    @classmethod
    def from_dict(cls, data):
        """Создает из словаря"""
        return cls(
            name=data["name"],
            deadline=datetime.fromisoformat(data["deadline"]),
            days_needed=data["days_needed"],
            created=datetime.fromisoformat(data["created"])
        )

    def is_urgent(self, current_time=None) -> bool:
        """Проверяет, является ли дедлайн срочным"""
        if current_time is None:
            current_time = datetime.now()

        if self.days_needed is None:
            return False

        days_remaining = (self.deadline - current_time).days
        return days_remaining < self.days_needed

    def is_overdue(self, current_time=None) -> bool:
        """Проверяет, просрочен ли дедлайн"""
        if current_time is None:
            current_time = datetime.now()
        return self.deadline <= current_time