import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import json
import os


class DeadlineTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Трекер дедлайнов")
        self.root.geometry("750x450")

        self.deadlines = []
        self.load_data()

        self.create_widgets()
        self.update_display()

    def create_widgets(self):
        # Frame для добавления новых дедлайнов
        input_frame = ttk.Frame(self.root, padding="10")
        input_frame.grid(row=0, column=0, sticky="ew")

        # Поля ввода
        ttk.Label(input_frame, text="Название:").grid(row=0, column=0, sticky="w")
        self.name_entry = ttk.Entry(input_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Дата дедлайна (ММ-ДД):").grid(row=1, column=0, sticky="w")

        # Frame для даты и года
        date_frame = ttk.Frame(input_frame)
        date_frame.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        self.date_entry = ttk.Entry(date_frame, width=8)
        self.date_entry.grid(row=0, column=0, padx=(0, 5))

        # Поле года с текущим годом по умолчанию
        current_year = datetime.now().year
        self.year_entry = ttk.Entry(date_frame, width=6)
        self.year_entry.insert(0, str(current_year))
        self.year_entry.grid(row=0, column=1)

        ttk.Label(input_frame, text="Время (ЧЧ:ММ):").grid(row=2, column=0, sticky="w")
        self.time_entry = ttk.Entry(input_frame, width=10)
        self.time_entry.insert(0, "23:59")
        self.time_entry.grid(row=2, column=1, padx=5, pady=2, sticky="w")

        # Новое поле: Время на выполнение
        ttk.Label(input_frame, text="Дней на выполнение:").grid(row=3, column=0, sticky="w")
        self.days_needed_entry = ttk.Entry(input_frame, width=10)
        self.days_needed_entry.grid(row=3, column=1, padx=5, pady=2, sticky="w")

        # Подсказки
        ttk.Label(input_frame, text="* Дата в формате: 01-20",
                  font=("Arial", 8), foreground="gray").grid(row=4, column=1, sticky="w")
        ttk.Label(input_frame, text="* Оставьте пустым если не важно",
                  font=("Arial", 8), foreground="gray").grid(row=5, column=1, sticky="w")

        # Кнопка добавления
        ttk.Button(input_frame, text="Добавить дедлайн",
                   command=self.add_deadline).grid(row=6, column=0, columnspan=2, pady=10)

        # Treeview для отображения дедлайнов
        columns = ("name", "deadline", "days_needed", "remaining")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=15)

        self.tree.heading("name", text="Название")
        self.tree.heading("deadline", text="Дедлайн")
        self.tree.heading("days_needed", text="Дней на выполнение")
        self.tree.heading("remaining", text="Осталось времени")

        self.tree.column("name", width=200)
        self.tree.column("deadline", width=150)
        self.tree.column("days_needed", width=120)
        self.tree.column("remaining", width=180)

        self.tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Frame для кнопок управления (внизу)
        button_frame_bottom = ttk.Frame(self.root)
        button_frame_bottom.grid(row=2, column=0, pady=5)

        ttk.Button(button_frame_bottom, text="Удалить выбранный",
                   command=self.delete_deadline).grid(row=0, column=0, padx=5)

        ttk.Button(button_frame_bottom, text="Изменить выбранный",
                   command=self.edit_deadline).grid(row=0, column=1, padx=5)

        # Настройка растягивания
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def get_selected_deadline_index(self):
        """Получить индекс выбранного дедлайна"""
        selected = self.tree.selection()
        if not selected:
            return -1
        return self.tree.index(selected[0])

    def add_deadline(self):
        name = self.name_entry.get().strip()
        date_str = self.date_entry.get().strip()
        year_str = self.year_entry.get().strip()
        time_str = self.time_entry.get().strip()
        days_needed_str = self.days_needed_entry.get().strip()

        if not name or not date_str:
            messagebox.showerror("Ошибка", "Заполните название и дату!")
            return

        try:
            # Собираем полную дату из месяца-дня и года
            full_date_str = f"{year_str}-{date_str} {time_str}"
            deadline_date = datetime.strptime(full_date_str, "%Y-%m-%d %H:%M")

            # Проверяем что дедлайн в будущем
            if deadline_date <= datetime.now():
                messagebox.showerror("Ошибка", "Дедлайн должен быть в будущем!")
                return

            # Обрабатываем время на выполнение
            days_needed = None
            if days_needed_str:
                try:
                    days_needed = int(days_needed_str)
                    if days_needed <= 0:
                        messagebox.showerror("Ошибка", "Количество дней должно быть положительным!")
                        return
                except ValueError:
                    messagebox.showerror("Ошибка", "Количество дней должно быть числом!")
                    return

            # Добавляем в список
            self.deadlines.append({
                "name": name,
                "deadline": deadline_date,
                "days_needed": days_needed,
                "created": datetime.now()
            })

            # Очищаем поля ввода
            self.name_entry.delete(0, tk.END)
            self.date_entry.delete(0, tk.END)
            self.days_needed_entry.delete(0, tk.END)

            self.save_data()
            self.update_display()
            messagebox.showinfo("Успех", "Дедлайн добавлен!")

        except ValueError as e:
            messagebox.showerror("Ошибка",
                                 f"Неправильный формат даты/времени!\nИспользуйте: ММ-ДД и ЧЧ-ММ\nОшибка: {e}")

    def edit_deadline(self):
        """Редактирование выбранного дедлайна"""
        index = self.get_selected_deadline_index()
        if index == -1:
            messagebox.showwarning("Внимание", "Выберите дедлайн для редактирования!")
            return

        # Создаем окно редактирования
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Редактирование дедлайна")
        edit_window.geometry("400x250")
        edit_window.transient(self.root)
        edit_window.grab_set()

        # Получаем данные выбранного дедлайна
        deadline = self.deadlines[index]

        # Поля для редактирования
        ttk.Label(edit_window, text="Название:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        name_entry = ttk.Entry(edit_window, width=30)
        name_entry.insert(0, deadline["name"])
        name_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(edit_window, text="Дата и время:").grid(row=1, column=0, padx=10, pady=10, sticky="w")

        # Frame для даты и времени
        datetime_frame = ttk.Frame(edit_window)
        datetime_frame.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # Дата (ММ-ДД)
        date_entry = ttk.Entry(datetime_frame, width=8)
        date_entry.insert(0, deadline["deadline"].strftime("%m-%d"))
        date_entry.grid(row=0, column=0, padx=(0, 5))

        # Год
        year_entry = ttk.Entry(datetime_frame, width=6)
        year_entry.insert(0, str(deadline["deadline"].year))
        year_entry.grid(row=0, column=1, padx=(0, 5))

        # Время
        time_entry = ttk.Entry(datetime_frame, width=8)
        time_entry.insert(0, deadline["deadline"].strftime("%H:%M"))
        time_entry.grid(row=0, column=2)

        ttk.Label(datetime_frame, text="(ММ-ДД ГГГГ ЧЧ:ММ)").grid(row=1, column=0, columnspan=3, sticky="w")

        # Новое поле: Время на выполнение
        ttk.Label(edit_window, text="Дней на выполнение:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        days_needed_entry = ttk.Entry(edit_window, width=10)
        if deadline["days_needed"] is not None:
            days_needed_entry.insert(0, str(deadline["days_needed"]))
        days_needed_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        ttk.Label(edit_window, text="* Оставьте пустым если не важно",
                  font=("Arial", 8), foreground="gray").grid(row=3, column=1, sticky="w")

        def save_changes():
            """Сохранение изменений"""
            new_name = name_entry.get().strip()
            new_date_str = date_entry.get().strip()
            new_year_str = year_entry.get().strip()
            new_time_str = time_entry.get().strip()
            new_days_needed_str = days_needed_entry.get().strip()

            if not new_name or not new_date_str:
                messagebox.showerror("Ошибка", "Заполните название и дату!")
                return

            try:
                # Собираем новую дату
                full_date_str = f"{new_year_str}-{new_date_str} {new_time_str}"
                new_deadline_date = datetime.strptime(full_date_str, "%Y-%m-%d %H:%M")

                # Проверяем что дедлайн в будущем
                if new_deadline_date <= datetime.now():
                    messagebox.showerror("Ошибка", "Дедлайн должен быть в будущем!")
                    return

                # Обрабатываем время на выполнение
                new_days_needed = None
                if new_days_needed_str:
                    try:
                        new_days_needed = int(new_days_needed_str)
                        if new_days_needed <= 0:
                            messagebox.showerror("Ошибка", "Количество дней должно быть положительным!")
                            return
                    except ValueError:
                        messagebox.showerror("Ошибка", "Количество дней должно быть числом!")
                        return

                # Обновляем данные
                self.deadlines[index]["name"] = new_name
                self.deadlines[index]["deadline"] = new_deadline_date
                self.deadlines[index]["days_needed"] = new_days_needed

                self.save_data()
                self.update_display()
                edit_window.destroy()
                messagebox.showinfo("Успех", "Дедлайн обновлен!")

            except ValueError as e:
                messagebox.showerror("Ошибка", f"Неправильный формат даты/времени!\nОшибка: {e}")

        # Кнопки в окне редактирования
        button_frame = ttk.Frame(edit_window)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Сохранить",
                   command=save_changes).grid(row=0, column=0, padx=10)

        ttk.Button(button_frame, text="Отмена",
                   command=edit_window.destroy).grid(row=0, column=1, padx=10)

    def delete_deadline(self):
        index = self.get_selected_deadline_index()
        if index == -1:
            messagebox.showwarning("Внимание", "Выберите дедлайн для удаления!")
            return

        # Подтверждение удаления
        deadline_name = self.deadlines[index]["name"]
        result = messagebox.askyesno(
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить дедлайн:\n\"{deadline_name}\"?"
        )

        if result:
            del self.deadlines[index]
            self.save_data()
            self.update_display()

    def calculate_time_remaining(self, deadline, days_needed):
        now = datetime.now()
        difference = deadline - now

        if difference.total_seconds() <= 0:
            return "ПРОСРОЧЕНО!", True  # Второй параметр - красный цвет

        days = difference.days
        hours = difference.seconds // 3600
        minutes = (difference.seconds % 3600) // 60

        time_str = f"{days} дн. {hours} ч. {minutes} мин."

        # Проверяем нужно ли подсвечивать красным
        # СТРОГО МЕНЬШЕ дней чем нужно на выполнение
        is_urgent = False
        if days_needed is not None:
            if days < days_needed:  # ИЗМЕНЕНИЕ: строго меньше
                is_urgent = True

        return time_str, is_urgent

    def update_display(self):
        # Очищаем treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Сортируем по дате дедлайна
        self.deadlines.sort(key=lambda x: x["deadline"])

        # Добавляем дедлайны в treeview
        for deadline in self.deadlines:
            remaining, is_urgent = self.calculate_time_remaining(
                deadline["deadline"],
                deadline["days_needed"]
            )

            # Форматируем дни на выполнение
            days_needed_str = str(deadline["days_needed"]) if deadline["days_needed"] is not None else ""

            item = self.tree.insert("", "end", values=(
                deadline["name"],
                deadline["deadline"].strftime("%d.%m.%Y %H:%M"),
                days_needed_str,
                remaining
            ))

            # Подсвечиваем красным если срочно или просрочено
            if is_urgent or "ПРОСРОЧЕНО" in remaining:
                self.tree.item(item, tags=("urgent",))
            else:
                # Убираем подсветку если не срочно
                self.tree.item(item, tags=())

        # Настраиваем тег для красного цвета
        self.tree.tag_configure("urgent", background="#ffcccc")

        # Обновляем каждую минуту
        self.root.after(60000, self.update_display)

    def save_data(self):
        # Сохраняем в JSON файл
        data = []
        for deadline in self.deadlines:
            data.append({
                "name": deadline["name"],
                "deadline": deadline["deadline"].isoformat(),
                "days_needed": deadline["days_needed"],
                "created": deadline["created"].isoformat()
            })

        with open("deadlines.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_data(self):
        # Загружаем из JSON файла
        if os.path.exists("deadlines.json"):
            try:
                with open("deadlines.json", "r", encoding="utf-8") as f:
                    data = json.load(f)

                for item in data:
                    self.deadlines.append({
                        "name": item["name"],
                        "deadline": datetime.fromisoformat(item["deadline"]),
                        "days_needed": item["days_needed"],
                        "created": datetime.fromisoformat(item["created"])
                    })
            except Exception as e:
                print(f"Ошибка загрузки данных: {e}")


def main():
    root = tk.Tk()
    app = DeadlineTracker(root)
    root.mainloop()


if __name__ == "__main__":
    main()