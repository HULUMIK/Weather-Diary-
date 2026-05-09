import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary - Дневник погоды")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Загрузка данных
        self.entries = self.load_entries()

        # Создание интерфейса
        self.create_widgets()

        # Обновление таблицы
        self.update_table()

    def create_widgets(self):
        # === Панель ввода ===
        input_frame = tk.LabelFrame(self.root, text="Добавление новой записи", 
                                     font=("Arial", 10, "bold"), padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Дата
        tk.Label(input_frame, text="📅 Дата (ГГГГ-ММ-ДД):", font=("Arial", 9)).grid(row=0, column=0, sticky="w", pady=5)
        self.date_entry = tk.Entry(input_frame, width=20, font=("Arial", 9))
        self.date_entry.grid(row=0, column=1, padx=10, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))  # сегодняшняя дата по умолчанию

        # Температура
        tk.Label(input_frame, text="🌡️ Температура (°C):", font=("Arial", 9)).grid(row=1, column=0, sticky="w", pady=5)
        self.temp_entry = tk.Entry(input_frame, width=20, font=("Arial", 9))
        self.temp_entry.grid(row=1, column=1, padx=10, pady=5)

        # Описание погоды
        tk.Label(input_frame, text="☁️ Описание погоды:", font=("Arial", 9)).grid(row=2, column=0, sticky="w", pady=5)
        self.desc_entry = tk.Entry(input_frame, width=40, font=("Arial", 9))
        self.desc_entry.grid(row=2, column=1, padx=10, pady=5)

        # Осадки
        self.precipitation_var = tk.BooleanVar()
        tk.Checkbutton(input_frame, text="🌧️ Осадки", variable=self.precipitation_var, 
                      font=("Arial", 9)).grid(row=3, column=1, sticky="w", padx=10, pady=5)

        # Кнопка добавления
        tk.Button(input_frame, text="➕ Добавить запись", command=self.add_entry,
                 bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
                 cursor="hand2", padx=20).grid(row=4, column=0, columnspan=2, pady=10)

        # === Панель фильтрации ===
        filter_frame = tk.LabelFrame(self.root, text="Фильтрация записей", 
                                      font=("Arial", 10, "bold"), padx=10, pady=5)
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Фильтр по дате
        tk.Label(filter_frame, text="📅 Фильтр по дате:", font=("Arial", 9)).grid(row=0, column=0, sticky="w", pady=5)
        self.filter_date_entry = tk.Entry(filter_frame, width=15, font=("Arial", 9))
        self.filter_date_entry.grid(row=0, column=1, padx=10, pady=5)
        self.filter_date_entry.insert(0, "ГГГГ-ММ-ДД")
        self.filter_date_entry.bind("<FocusIn>", lambda e: self.filter_date_entry.delete(0, tk.END) if self.filter_date_entry.get() == "ГГГГ-ММ-ДД" else None)

        # Фильтр по температуре
        tk.Label(filter_frame, text="🌡️ Температура выше:", font=("Arial", 9)).grid(row=1, column=0, sticky="w", pady=5)
        self.filter_temp_entry = tk.Entry(filter_frame, width=10, font=("Arial", 9))
        self.filter_temp_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Button(filter_frame, text="🔍 Применить фильтр", command=self.apply_filter,
                 bg="#3498db", fg="white", cursor="hand2").grid(row=2, column=0, padx=5, pady=5)
        tk.Button(filter_frame, text="🔄 Сбросить фильтр", command=self.reset_filter,
                 bg="#95a5a6", fg="white", cursor="hand2").grid(row=2, column=1, padx=5, pady=5)

        # === Таблица записей ===
        table_frame = tk.LabelFrame(self.root, text="Записи о погоде", 
                                     font=("Arial", 10, "bold"), padx=5, pady=5)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Создание Treeview
        columns = ("date", "temperature", "description", "precipitation")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)

        # Настройка заголовков
        self.tree.heading("date", text="📅 Дата")
        self.tree.heading("temperature", text="🌡️ Температура (°C)")
        self.tree.heading("description", text="☁️ Описание")
        self.tree.heading("precipitation", text="🌧️ Осадки")

        # Настройка ширины колонок
        self.tree.column("date", width=120)
        self.tree.column("temperature", width=120)
        self.tree.column("description", width=300)
        self.tree.column("precipitation", width=80)

        # Скроллбар
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # === Кнопки управления ===
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill="x", padx=10, pady=5)

        tk.Button(control_frame, text="🗑 Удалить выбранную запись", command=self.delete_entry,
                 bg="#e74c3c", fg="white", cursor="hand2").pack(side="left", padx=5)
        tk.Button(control_frame, text="💾 Сохранить в JSON", command=self.save_to_json,
                 bg="#f39c12", fg="white", cursor="hand2").pack(side="left", padx=5)
        tk.Button(control_frame, text="📂 Загрузить из JSON", command=self.load_from_json,
                 bg="#9b59b6", fg="white", cursor="hand2").pack(side="left", padx=5)

        # Статусная строка
        self.status_bar = tk.Label(self.root, text="Готов к работе", 
                                    bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                    font=("Arial", 8))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def validate_date(self, date_string):
        """Проверка корректности даты"""
        try:
            datetime.strptime(date_string, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def add_entry(self):
        """Добавление новой записи с проверкой ввода"""
        date = self.date_entry.get().strip()
        temperature = self.temp_entry.get().strip()
        description = self.desc_entry.get().strip()
        precipitation = self.precipitation_var.get()

        # Валидация
        if not date:
            messagebox.showerror("Ошибка", "Дата не может быть пустой!")
            return

        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты!\nИспользуйте ГГГГ-ММ-ДД (например, 2024-01-15)")
            return

        try:
            temp_value = float(temperature)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом!")
            return

        if not description:
            messagebox.showerror("Ошибка", "Описание погоды не может быть пустым!")
            return

        # Добавление записи
        entry = {
            "date": date,
            "temperature": temp_value,
            "description": description,
            "precipitation": precipitation
        }

        self.entries.append(entry)
        self.sort_entries()  # Сортировка по дате
        self.update_table()
        self.clear_input_fields()

        self.status_bar.config(text=f"✅ Добавлена запись: {date}, {temp_value}°C")
        messagebox.showinfo("Успех", "Запись успешно добавлена!")

    def sort_entries(self):
        """Сортировка записей по дате (от новых к старым)"""
        self.entries.sort(key=lambda x: x["date"], reverse=True)

    def clear_input_fields(self):
        """Очистка полей ввода"""
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precipitation_var.set(False)

    def update_table(self, filtered_entries=None):
        """Обновление таблицы записей"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Выбор данных для отображения
        display_entries = filtered_entries if filtered_entries is not None else self.entries

        for entry in display_entries:
            precipitation_text = "Да 🌧️" if entry["precipitation"] else "Нет ☀️"
            self.tree.insert("", tk.END, values=(
                entry["date"],
                f"{entry['temperature']}°C",
                entry["description"],
                precipitation_text
            ))

        self.status_bar.config(text=f"📊 Показано записей: {len(display_entries)} из {len(self.entries)}")

    def apply_filter(self):
        """Применение фильтров"""
        filter_date = self.filter_date_entry.get().strip()
        filter_temp_str = self.filter_temp_entry.get().strip()

        filtered = self.entries.copy()

        # Фильтр по дате
        if filter_date and filter_date != "ГГГГ-ММ-ДД":
            if not self.validate_date(filter_date):
                messagebox.showerror("Ошибка", "Неверный формат даты в фильтре!\nИспользуйте ГГГГ-ММ-ДД")
                return
            filtered = [e for e in filtered if e["date"] == filter_date]

        # Фильтр по температуре
        if filter_temp_str:
            try:
                min_temp = float(filter_temp_str)
                filtered = [e for e in filtered if e["temperature"] > min_temp]
            except ValueError:
                messagebox.showerror("Ошибка", "Температура для фильтра должна быть числом!")
                return

        self.update_table(filtered)
        self.status_bar.config(text=f"🔍 Применён фильтр: показано {len(filtered)} записей")

    def reset_filter(self):
        """Сброс фильтров"""
        self.filter_date_entry.delete(0, tk.END)
        self.filter_date_entry.insert(0, "ГГГГ-ММ-ДД")
        self.filter_temp_entry.delete(0, tk.END)
        self.update_table()
        self.status_bar.config(text="🔄 Фильтр сброшен")

    def delete_entry(self):
        """Удаление выбранной записи"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запись для удаления")
            return

        # Получение данных выбранной записи
        values = self.tree.item(selected[0])["values"]
        date = values[0]
        temp = values[1].replace("°C", "")

        # Поиск и удаление записи
        for i, entry in enumerate(self.entries):
            if entry["date"] == date and float(entry["temperature"]) == float(temp):
                del self.entries[i]
                break

        self.sort_entries()
        self.update_table()
        self.status_bar.config(text=f"🗑 Удалена запись: {date}, {temp}°C")
        messagebox.showinfo("Успех", "Запись удалена!")

    def save_to_json(self):
        """Сохранение записей в JSON файл"""
        try:
            with open("weather_diary.json", "w", encoding="utf-8") as f:
                json.dump(self.entries, f, ensure_ascii=False, indent=2)
            self.status_bar.config(text=f"💾 Сохранено {len(self.entries)} записей в weather_diary.json")
            messagebox.showinfo("Успех", f"Сохранено {len(self.entries)} записей в файл weather_diary.json")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {str(e)}")

    def load_from_json(self):
        """Загрузка записей из JSON файла"""
        if not os.path.exists("weather_diary.json"):
            messagebox.showwarning("Предупреждение", "Файл weather_diary.json не найден!")
            return

        try:
            with open("weather_diary.json", "r", encoding="utf-8") as f:
                loaded_entries = json.load(f)

            # Валидация загруженных данных
            valid_entries = []
            for entry in loaded_entries:
                if all(key in entry for key in ["date", "temperature", "description", "precipitation"]):
                    valid_entries.append(entry)
                else:
                    print(f"Пропущена некорректная запись: {entry}")

            self.entries = valid_entries
            self.sort_entries()
            self.update_table()
            self.status_bar.config(text=f"📂 Загружено {len(self.entries)} записей из weather_diary.json")
            messagebox.showinfo("Успех", f"Загружено {len(self.entries)} записей из файла!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {str(e)}")

    def load_entries(self):
        """Загрузка записей при запуске (если файл существует)"""
        if os.path.exists("weather_diary.json"):
            try:
                with open("weather_diary.json", "r", encoding="utf-8") as f:
                    entries = json.load(f)
                return entries
            except:
                return self.get_sample_entries()
        return self.get_sample_entries()

    def get_sample_entries(self):
        """Пример записей для демонстрации"""
        return [
            {"date": "2024-01-15", "temperature": -5.0, "description": "Солнечно, снег", "precipitation": True},
            {"date": "2024-03-20", "temperature": 8.0, "description": "Пасмурно, дождь", "precipitation": True},
            {"date": "2024-06-10", "temperature": 22.5, "description": "Ясно, тепло", "precipitation": False},
            {"date": "2024-09-05", "temperature": 15.0, "description": "Облачно, без осадков", "precipitation": False},
            {"date": "2024-12-01", "temperature": -10.0, "description": "Морозно, снегопад", "precipitation": True}
        ]

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiary(root)

    # Центрирование окна
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    root.mainloop()