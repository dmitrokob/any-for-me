import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import os


class ListEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Редактор списков")
        self.root.geometry("800x600")

        # Данные
        self.lists = {"1": []}  # Словарь списков
        self.deleted_items = []  # Корзина
        self.current_file = None

        # Переменные для drag&drop
        self.drag_data = {"item": None, "index": None, "list_name": None, "y_offset": 0}

        self.setup_ui()

    def setup_ui(self):
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Настройка весов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Верхняя панель с кнопками
        top_frame = ttk.Frame(main_frame)
        top_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Button(top_frame, text="Открыть JSON", command=self.open_json_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(top_frame, text="Импорт TXT", command=self.import_txt_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(top_frame, text="Сохранить как", command=self.save_as_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(top_frame, text="Корзина", command=self.show_trash).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(top_frame, text="Добавить список", command=self.add_list).pack(side=tk.LEFT)

        # Фрейм для списков
        self.lists_frame = ttk.Frame(main_frame)
        self.lists_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.lists_frame.columnconfigure(0, weight=1)
        self.lists_frame.rowconfigure(0, weight=1)

        # Создаем Notebook для вкладок со списками
        self.notebook = ttk.Notebook(self.lists_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Изначально создаем список "1"
        self.create_list_widget("1")

        # Нижняя панель для добавления элементов
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

        ttk.Label(bottom_frame, text="Новый элемент:").pack(side=tk.LEFT)
        self.new_item_entry = ttk.Entry(bottom_frame, width=30)
        self.new_item_entry.pack(side=tk.LEFT, padx=(5, 5))
        self.new_item_entry.bind("<Return>", lambda e: self.add_item_to_current_list())

        ttk.Button(bottom_frame, text="Добавить", command=self.add_item_to_current_list).pack(side=tk.LEFT)

    def create_list_widget(self, list_name):
        """Создает виджет для списка"""
        frame = ttk.Frame(self.notebook, padding="5")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        # Listbox с прокруткой
        listbox_frame = ttk.Frame(frame)
        listbox_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, selectmode=tk.SINGLE)
        listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.config(command=listbox.yview)

        # Настройка drag&drop
        self.setup_drag_drop(listbox, list_name)

        # Привязываем двойной клик для редактирования
        listbox.bind("<Double-Button-1>", lambda e: self.edit_item(list_name))

        # Кнопки управления
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))

        ttk.Button(button_frame, text="Вверх",
                   command=lambda: self.move_item(list_name, -1)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Вниз",
                   command=lambda: self.move_item(list_name, 1)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Удалить",
                   command=lambda: self.delete_item(list_name)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="В другой список",
                   command=lambda: self.move_to_other_list(list_name)).pack(side=tk.LEFT, padx=(0, 5))

        # Кнопка удаления списка (только если это не последний список)
        if len(self.lists) > 1:
            ttk.Button(button_frame, text="Удалить список",
                       command=lambda: self.delete_list(list_name)).pack(side=tk.LEFT, padx=(0, 5))

        # Добавляем вкладку
        self.notebook.add(frame, text=list_name)

        # Сохраняем ссылки
        if not hasattr(self, 'list_widgets'):
            self.list_widgets = {}
        if not hasattr(self, 'list_frames'):
            self.list_frames = {}

        self.list_widgets[list_name] = listbox
        self.list_frames[list_name] = frame

        # Обновляем отображение
        self.refresh_list(list_name)

        # Добавляем контекстное меню для переименования вкладки
        self.setup_tab_context_menu()

    def setup_drag_drop(self, listbox, list_name):
        """Настраивает drag&drop для Listbox"""
        # Начало перетаскивания
        listbox.bind("<ButtonPress-1>", lambda e: self.on_drag_start(e, listbox, list_name))
        # Движение при перетаскивании
        listbox.bind("<B1-Motion>", lambda e: self.on_drag_motion(e, listbox, list_name))
        # Конец перетаскивания
        listbox.bind("<ButtonRelease-1>", lambda e: self.on_drag_release(e, listbox, list_name))

    def on_drag_start(self, event, listbox, list_name):
        """Начало перетаскивания"""
        # Получаем индекс элемента под курсором
        index = listbox.nearest(event.y)
        if index >= 0 and index < len(self.lists[list_name]):
            # Сохраняем данные о перетаскиваемом элементе
            self.drag_data["item"] = self.lists[list_name][index]
            self.drag_data["index"] = index
            self.drag_data["list_name"] = list_name
            self.drag_data["y_offset"] = event.y - listbox.bbox(index)[1]

            # Визуально выделяем перетаскиваемый элемент
            listbox.selection_clear(0, tk.END)
            listbox.selection_set(index)

    def on_drag_motion(self, event, listbox, list_name):
        """Движение при перетаскивании"""
        if self.drag_data["item"] is not None:
            # Получаем текущую позицию курсора
            current_index = listbox.nearest(event.y)

            # Если курсор на другом элементе, показываем визуальную подсказку
            if (current_index >= 0 and current_index != self.drag_data["index"] and
                    current_index < len(self.lists[list_name])):
                listbox.selection_clear(0, tk.END)
                listbox.selection_set(current_index)

    def on_drag_release(self, event, listbox, list_name):
        """Завершение перетаскивания"""
        if (self.drag_data["item"] is not None and
                self.drag_data["list_name"] == list_name):

            # Получаем конечную позицию
            end_index = listbox.nearest(event.y)

            # Если позиция изменилась и валидна
            if (end_index >= 0 and end_index != self.drag_data["index"] and
                    end_index < len(self.lists[list_name])):
                # Удаляем элемент из старой позиции
                item = self.lists[list_name].pop(self.drag_data["index"])

                # Вставляем в новую позицию
                self.lists[list_name].insert(end_index, item)

                # Обновляем отображение
                self.refresh_list(list_name)

                # Выделяем перемещенный элемент
                listbox.selection_set(end_index)

                # Автосохранение
                self.auto_save()

            # Сбрасываем данные о перетаскивании
            self.drag_data = {"item": None, "index": None, "list_name": None, "y_offset": 0}

    def setup_tab_context_menu(self):
        """Добавляет контекстное меню для переименования вкладок"""
        self.tab_menu = tk.Menu(self.root, tearoff=0)
        self.tab_menu.add_command(label="Переименовать список", command=self.rename_current_list)

        def show_tab_menu(event):
            # Определяем на какую вкладку кликнули
            tab_index = self.notebook.index(f"@{event.x},{event.y}")
            if tab_index != -1:
                self.current_tab_index = tab_index
                self.tab_menu.post(event.x_root, event.y_root)

        self.notebook.bind("<Button-3>", show_tab_menu)  # Правая кнопка мыши

    def rename_current_list(self):
        """Переименовывает текущую вкладку через контекстное меню"""
        if hasattr(self, 'current_tab_index'):
            old_name = self.notebook.tab(self.current_tab_index, "text")

            new_name = simpledialog.askstring(
                "Переименование списка",
                "Введите новое название списка:",
                initialvalue=old_name
            )

            if new_name and new_name.strip() and new_name != old_name:
                if new_name in self.lists:
                    messagebox.showerror("Ошибка", f"Список с названием '{new_name}' уже существует!")
                else:
                    self.rename_list_completely(old_name, new_name)

    def rename_list_completely(self, old_name, new_name):
        """Полностью переименовывает список, пересоздавая виджеты"""
        # Сохраняем данные
        list_data = self.lists[old_name]

        # Удаляем старый список
        del self.lists[old_name]
        del self.list_widgets[old_name]
        del self.list_frames[old_name]

        # Удаляем вкладку
        for tab in self.notebook.tabs():
            if self.notebook.tab(tab, "text") == old_name:
                self.notebook.forget(tab)
                break

        # Создаем новый список с новым именем
        self.lists[new_name] = list_data
        self.create_list_widget(new_name)

        # Обновляем ссылки в корзине
        for item in self.deleted_items:
            if item['original_list'] == old_name:
                item['original_list'] = new_name

        self.auto_save()

    def refresh_list(self, list_name):
        """Обновляет отображение списка"""
        if list_name in self.list_widgets:
            listbox = self.list_widgets[list_name]
            listbox.delete(0, tk.END)
            for item in self.lists[list_name]:
                listbox.insert(tk.END, item)

    def get_current_list_name(self):
        """Возвращает имя текущего активного списка"""
        current_tab = self.notebook.index(self.notebook.select())
        return self.notebook.tab(current_tab, "text")

    def get_current_listbox(self):
        """Возвращает текущий активный listbox"""
        current_list = self.get_current_list_name()
        return self.list_widgets.get(current_list)

    def add_item_to_current_list(self):
        """Добавляет новый элемент в текущий список"""
        item = self.new_item_entry.get().strip()
        if item:
            current_list = self.get_current_list_name()
            self.lists[current_list].append(item)
            self.refresh_list(current_list)
            self.new_item_entry.delete(0, tk.END)
            self.auto_save()

    def add_list(self):
        """Добавляет новый список"""
        list_name = simpledialog.askstring("Новый список", "Введите название списка:")
        if list_name:
            if list_name in self.lists:
                messagebox.showerror("Ошибка", f"Список с названием '{list_name}' уже существует!")
            else:
                self.lists[list_name] = []
                self.create_list_widget(list_name)
                self.auto_save()

    def delete_list(self, list_name):
        """Удаляет список"""
        if len(self.lists) <= 1:
            messagebox.showerror("Ошибка", "Нельзя удалить последний список!")
            return

        if messagebox.askyesno("Удаление списка",
                               f"Вы уверены, что хотите удалить список '{list_name}'?\nВсе элементы будут перемещены в корзину."):

            # Перемещаем все элементы в корзину
            for item in self.lists[list_name]:
                self.deleted_items.append({
                    'item': item,
                    'original_list': list_name,
                    'original_index': -1
                })

            # Удаляем список
            del self.lists[list_name]
            del self.list_widgets[list_name]
            del self.list_frames[list_name]

            # Удаляем вкладку
            for tab in self.notebook.tabs():
                if self.notebook.tab(tab, "text") == list_name:
                    self.notebook.forget(tab)
                    break

            self.auto_save()

    def move_item(self, list_name, direction):
        """Перемещает элемент вверх или вниз"""
        listbox = self.list_widgets.get(list_name)
        if not listbox:
            return

        selection = listbox.curselection()

        if selection:
            index = selection[0]
            new_index = index + direction

            if 0 <= new_index < len(self.lists[list_name]):
                # Меняем местами элементы в данных
                self.lists[list_name][index], self.lists[list_name][new_index] = \
                    self.lists[list_name][new_index], self.lists[list_name][index]

                # Обновляем отображение
                self.refresh_list(list_name)

                # Выделяем перемещенный элемент
                listbox.selection_set(new_index)

                self.auto_save()

    def delete_item(self, list_name):
        """Удаляет элемент в корзину"""
        listbox = self.list_widgets.get(list_name)
        if not listbox:
            return

        selection = listbox.curselection()

        if selection:
            index = selection[0]
            item = self.lists[list_name][index]

            # Перемещаем в корзину
            self.deleted_items.append({
                'item': item,
                'original_list': list_name,
                'original_index': index
            })

            # Удаляем из списка
            del self.lists[list_name][index]
            self.refresh_list(list_name)
            self.auto_save()

    def move_to_other_list(self, list_name):
        """Перемещает элемент в другой список"""
        listbox = self.list_widgets.get(list_name)
        if not listbox:
            return

        selection = listbox.curselection()

        if selection:
            index = selection[0]
            item = self.lists[list_name][index]

            # Выбираем целевой список
            target_list = self.choose_target_list(list_name)
            if target_list:
                # Удаляем из текущего списка
                del self.lists[list_name][index]

                # Добавляем в целевой список
                self.lists[target_list].append(item)

                # Обновляем оба списка
                self.refresh_list(list_name)
                self.refresh_list(target_list)
                self.auto_save()

    def choose_target_list(self, exclude_list):
        """Выбор целевого списка для перемещения"""
        available_lists = [name for name in self.lists if name != exclude_list]

        if not available_lists:
            messagebox.showwarning("Нет списков", "Нет других списков для перемещения")
            return None

        # Диалог выбора списка
        choice_dialog = tk.Toplevel(self.root)
        choice_dialog.title("Выбор списка")
        choice_dialog.geometry("300x150")
        choice_dialog.transient(self.root)
        choice_dialog.grab_set()

        ttk.Label(choice_dialog, text="Выберите целевой список:").pack(pady=10)

        choice_var = tk.StringVar(value=available_lists[0])
        combobox = ttk.Combobox(choice_dialog, textvariable=choice_var, values=available_lists, state="readonly")
        combobox.pack(pady=5)

        result = [None]  # Используем список для передачи по ссылке

        def on_ok():
            result[0] = choice_var.get()
            choice_dialog.destroy()

        def on_cancel():
            choice_dialog.destroy()

        ttk.Button(choice_dialog, text="OK", command=on_ok).pack(side=tk.LEFT, padx=10, pady=10)
        ttk.Button(choice_dialog, text="Отмена", command=on_cancel).pack(side=tk.RIGHT, padx=10, pady=10)

        choice_dialog.wait_window()
        return result[0]

    def edit_item(self, list_name):
        """Редактирование элемента по двойному клику"""
        listbox = self.list_widgets.get(list_name)
        if not listbox:
            return

        selection = listbox.curselection()

        if selection:
            index = selection[0]
            current_value = self.lists[list_name][index]

            new_value = simpledialog.askstring(
                "Редактирование",
                "Введите новое значение:",
                initialvalue=current_value
            )

            if new_value is not None and new_value.strip():
                self.lists[list_name][index] = new_value.strip()
                self.refresh_list(list_name)
                self.auto_save()

    def show_trash(self):
        """Показывает окно с корзиной"""
        trash_window = tk.Toplevel(self.root)
        trash_window.title("Корзина")
        trash_window.geometry("400x300")

        # Listbox для корзины
        listbox_frame = ttk.Frame(trash_window, padding="10")
        listbox_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        # Заполняем корзину
        for item_data in self.deleted_items:
            listbox.insert(tk.END, f"{item_data['item']} (из '{item_data['original_list']}')")

        # Кнопки управления
        button_frame = ttk.Frame(trash_window, padding="5")
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Восстановить",
                   command=lambda: self.restore_from_trash(listbox, trash_window)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Очистить корзину",
                   command=lambda: self.clear_trash(listbox)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Закрыть",
                   command=trash_window.destroy).pack(side=tk.RIGHT)

    def restore_from_trash(self, listbox, window):
        """Восстанавливает элемент из корзины"""
        selection = listbox.curselection()
        if selection:
            index = selection[0]
            item_data = self.deleted_items[index]

            # Определяем в какой список восстанавливать
            target_list = item_data['original_list']

            # Если оригинального списка больше не существует, используем текущий активный список
            if target_list not in self.lists:
                target_list = self.get_current_list_name()
                messagebox.showinfo("Восстановление",
                                    f"Оригинальный список '{item_data['original_list']}' больше не существует.\n"
                                    f"Элемент будет восстановлен в список '{target_list}'.")

            # Восстанавливаем в выбранный список
            self.lists[target_list].append(item_data['item'])

            # Удаляем из корзины
            del self.deleted_items[index]

            # Обновляем отображение
            self.refresh_list(target_list)
            self.auto_save()
            window.destroy()
            self.show_trash()  # Переоткрываем окно корзины

    def clear_trash(self, listbox):
        """Очищает корзину"""
        if self.deleted_items:
            if messagebox.askyesno("Очистка корзины", "Вы уверены, что хотите очистить корзину?"):
                self.deleted_items.clear()
                listbox.delete(0, tk.END)
                self.auto_save()
        else:
            messagebox.showinfo("Корзина", "Корзина уже пуста")

    def import_txt_file(self):
        """Импортирует элементы из TXT файла в список '1'"""
        filename = filedialog.askopenfilename(
            title="Импорт из TXT файла",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                # Очищаем текущий список "1" и добавляем новые элементы
                self.lists["1"] = []
                for line in lines:
                    line = line.strip()
                    if line:  # Добавляем только непустые строки
                        self.lists["1"].append(line)

                # Обновляем отображение
                self.refresh_list("1")

                # Предлагаем сохранить как JSON
                if messagebox.askyesno("Импорт завершен",
                                       f"Импортировано {len(self.lists['1'])} элементов из TXT файла.\n"
                                       "Хотите сохранить как JSON файл?"):
                    self.save_as_file()
                else:
                    self.auto_save()

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось импортировать файл: {str(e)}")

    def open_json_file(self):
        """Открывает файл JSON с данными"""
        filename = filedialog.askopenfilename(
            title="Открыть JSON файл",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.lists = data.get('lists', {"1": []})
                self.deleted_items = data.get('trash', [])
                self.current_file = filename

                # Очищаем текущие вкладки
                for tab in self.notebook.tabs():
                    self.notebook.forget(tab)

                self.list_widgets = {}
                self.list_frames = {}

                # Создаем виджеты для всех списков
                for list_name in self.lists:
                    self.create_list_widget(list_name)

                messagebox.showinfo("Успех", f"Файл {os.path.basename(filename)} загружен")

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {str(e)}")

    def save_as_file(self):
        """Сохраняет данные в новый файл"""
        filename = filedialog.asksaveasfilename(
            title="Сохранить как JSON",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filename:
            self.current_file = filename
            self._save_to_file(filename)

    def _save_to_file(self, filename):
        """Внутренняя функция сохранения"""
        try:
            data = {
                'lists': self.lists,
                'trash': self.deleted_items
            }

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            messagebox.showinfo("Успех", f"Файл {os.path.basename(filename)} сохранен")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {str(e)}")

    def auto_save(self):
        """Автоматическое сохранение в текущий файл"""
        if self.current_file:
            try:
                data = {
                    'lists': self.lists,
                    'trash': self.deleted_items
                }
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"Ошибка автосохранения: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ListEditor(root)
    root.mainloop()