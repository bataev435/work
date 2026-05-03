import tkinter as tk
from tkinter import tk, messagebox
import requests
import json
import os

# Конфигурация
GITHUB_API_URL = "https://api.github.com"
FAVORITES_FILE = "favorites.json"

# Загрузка избранных пользователей
def load_favorites():
    if os.path.exists(FAVORITES_FILE):
        with open(FAVORITES_FILE, 'r', encoding='utf-8') as file:
            return json.load(f)
    return []

# Сохранение избранных пользователей
def save_favorites(favorites):
    with open(FAVORITES_FILE, 'w', encoding='utf-8') as file:
        json.dump(favorites, f, ensure_ascii=False, indent=2)

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("800x600")

        # Загрузка избранных пользователей
        self.favorites = load_favorites()

        self.setup_ui()

    def setup_ui(self):
        # Поле ввода для поиска
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=10, padx=10, fill='x')

        tk.Label(search_frame, text="Поиск пользователя GitHub:").pack(side='left')
        self.search_entry = tk.Entry(search_frame, width=50)
        self.search_entry.pack(side='left', padx=5)
        tk.Button(search_frame, text="Найти", command=self.search_users).pack(side='left')

        # Вкладки для результатов и избранного
        self.notebook = tk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Вкладка результатов поиска
        self.results_frame = tk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="Результаты поиска")

        self.results_tree = ttk.Treeview(
            self.results_frame,
            columns=('Login', 'Name', 'Type'),
            show='headings',
            height=15
        )
        self.results_tree.heading('Login', text='Логин')
        self.results_tree.heading('Name', text='Имя')
        self.results_tree.heading('Type', text='Тип')
        self.results_tree.pack(fill='both', expand=True)

        # Кнопка добавления в избранное
        tk.Button(
            self.results_frame,
            text="Добавить в избранное",
            command=self.add_to_favorites
        ).pack(pady=5)

        # Вкладка избранного
        self.favorites_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.favorites_frame, text="Избранное")

        self.favorites_tree = ttk.Treeview(
            self.favorites_frame,
            columns=('Login', 'Name', 'Type'),
            show='headings',
            height=15
        )
        self.favorites_tree.heading('Login', text='Логин')
        self.favorites_tree.heading('Name', text='Имя')
        self.favorites_tree.heading('Type', text='Тип')
        self.favorites_tree.pack(fill='both', expand=True)

        # Кнопка удаления из избранного
        tk.Button(
            self.favorites_frame,
            text="Удалить из избранного",
            command=self.remove_from_favorites
        ).pack(pady=5)

        self.refresh_favorites_display()

    def search_users(self):
        query = self.search_entry.get().strip()

        # Проверка корректности ввода
        if not query:
            messagebox.showerror("Ошибка", "Поле поиска не должно быть пустым!")
            return

        try:
            response = requests.get(f"{GITHUB_API_URL}/search/users?q={query}")
            response.raise_for_status()
            data = response.json()

            # Очистка предыдущего результата
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)

            # Отображение результатов
            for user in data['items'][:10]:  # Ограничение до 10 результатов
                self.results_tree.insert(
                    '', 'end',
                    values=(user['login'], user['name'] or 'Не указано', user['type'])
                )

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Ошибка при запросе к GitHub API: {e}")

    def add_to_favorites(self):
        selection = self.results_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для добавления в избранное!")
            return

        item = self.results_tree.item(selection[0])
        user_data = {
            'login': item['values'][0],
            'name': item['values'][1],
            'type': item['values'][2]
        }

        if user_data not in self.favorites:
            self.favorites.append(user_data)
            save_favorites(self.favorites)
            self.refresh_favorites_display()
            messagebox.showinfo("Успех", f"Пользователь {user_data['login']} добавлен в избранное!")
        else:
            messagebox.showinfo("Информация", "Этот пользователь уже в избранном!")

    def remove_from_favorites(self):
        selection = self.favorites_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для удаления из избранного!")
            return

        item = self.favorites_tree.item(selection[0])
        login = item['values'][0]

        self.favorites = [user for user in self.favorites if user['login'] != login]
        save_favorites(self.favorites)
        self.refresh_favorites_display()
        messagebox.showinfo("Успех", f"Пользователь {login} удалён из избранного!")

    def refresh_favorites_display(self):
        # Очистка и обновление отображения избранного
        for item in self.favorites_tree.get_children():
            self.favorites_tree.delete(item)

        for user in self.favorites:
            self.favorites_tree.insert(
                '', 'end',
                values=(user['login'], user['name'], user['type'])
            )

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()
