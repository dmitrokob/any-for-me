import tkinter as tk
from tkinter import ttk
from datetime import datetime


class DeadlineInputFrame(ttk.Frame):
    """Фрейм для ввода данных о дедлайне"""

    def __init__(self, parent, on_add_callback=None):
        super().__init__(parent, padding="10")
        self.on_add_callback = on_add_callback
        self.create_widgets()

    def create_widgets(self):
        # Поля ввода
        ttk.Label(self, text="Название:").grid(row=0, column=0, sticky="w")
        self.name_entry = ttk.Entry(self, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(self, text="Дата дедлайна (ММ-ДД):").grid(row=1, column=0, sticky="w")

        # Frame для даты и года
        date_frame = ttk.Frame(self)
        date_frame.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        self.date_entry = ttk.Entry(date_frame, width=8)
        self.date_entry.grid(row=0, column=0, padx=(0, 5))

        # Поле года с текущим годом по умолчанию
        current_year = datetime.now().year
        self.year_entry = ttk.Entry(date_frame, width=6)
        self.year_entry.insert(0, str(current_year))
        self.year_entry.grid(row=0, column=1)

        ttk.Label(self, text="Время (ЧЧ:ММ):").grid(row=2, column=0, sticky="w")
        self.time_entry = ttk.Entry(self, width=10)
        self.time_entry.insert(0, "23:59")
        self.time_entry.grid(row=2, column=1, padx=5, pady=2, sticky="w")

        # Поле: Время на выполнение
        ttk.Label(self, text="Дней на выполнение:").grid(row=3, column=0, sticky="w")
        self.days_needed_entry = ttk.Entry(self, width=10)
        self.days_needed_entry.grid(row=3, column=1, padx=5, pady=2, sticky="w")

        # Подсказки
        ttk.Label(self, text="* Дата в формате: 01-20",
                  font=("Arial", 8), foreground="gray").grid(row=4, column=1, sticky="w")
        ttk.Label(self, text="* Оставьте пустым если не важно",
                  font=("Arial", 8), foreground="gray").grid(row=5, column=1, sticky="w")

        # Кнопка добавления
        if self.on_add_callback:
            ttk.Button(self, text="Добавить дедлайн",
                       command=self.on_add_callback).grid(row=6, column=0, columnspan=2, pady=10)

    def get_input_data(self):
        """Возвращает данные из полей ввода"""
        return {
            "name": self.name_entry.get().strip(),
            "date": self.date_entry.get().strip(),
            "year": self.year_entry.get().strip(),
            "time": self.time_entry.get().strip(),
            "days_needed": self.days_needed_entry.get().strip()
        }

    def clear_inputs(self):
        """Очищает поля ввода"""
        self.name_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.days_needed_entry.delete(0, tk.END)