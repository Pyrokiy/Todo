import customtkinter as ctk
from plyer import notification
import threading
import time
import datetime
import json
import os

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

DATA_FILE = "tasks.json"

class TaskManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("タスク管理ツール")
        self.geometry("400x600")
        self.resizable(False, False)

        self.task_list = []
        self.load_tasks()

        self.theme_mode = "light"

        self.create_widgets()
        threading.Thread(target=self.check_reminders, daemon=True).start()

    def create_widgets(self):
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(pady=10, padx=10, fill="x")

        self.task_input = ctk.CTkEntry(self.input_frame, placeholder_text="タスク内容")
        self.task_input.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self.priority_menu = ctk.CTkOptionMenu(self.input_frame, values=["高", "中", "低"])
        self.priority_menu.set("中")
        self.priority_menu.pack(side="left")

        self.add_button = ctk.CTkButton(self, text="追加", command=self.add_task)
        self.add_button.pack(pady=5)

        self.task_frame = ctk.CTkScrollableFrame(self, width=380, height=400)
        self.task_frame.pack(pady=10)

        self.filter_button = ctk.CTkButton(self, text="未完了のみ表示", command=self.toggle_filter)
        self.filter_button.pack(pady=5)

        self.theme_button = ctk.CTkButton(self, text="テーマ切替", command=self.toggle_theme)
        self.theme_button.pack(pady=5)

        self.filtered = False
        self.render_tasks()

    def add_task(self):
        content = self.task_input.get()
        priority = self.priority_menu.get()
        if content:
            task = {
                "content": content,
                "priority": priority,
                "done": False,
                "remind_at": (datetime.datetime.now() + datetime.timedelta(hours=1)).isoformat()
            }
            self.task_list.append(task)
            self.save_tasks()
            self.render_tasks()
            self.task_input.delete(0, "end")

    def render_tasks(self):
        for widget in self.task_frame.winfo_children():
            widget.destroy()

        sorted_tasks = sorted(self.task_list, key=lambda x: {"高": 0, "中": 1, "低": 2}[x['priority']])
        if self.filtered:
            sorted_tasks = [t for t in sorted_tasks if not t['done']]

        for task in sorted_tasks:
            self.render_task(task)

    def render_task(self, task):
        frame = ctk.CTkFrame(self.task_frame)
        frame.pack(fill="x", pady=2, padx=5)

        var = ctk.BooleanVar(value=task['done'])
        checkbox = ctk.CTkCheckBox(frame, text=f"[{task['priority']}] {task['content']}", variable=var,
                                   command=lambda: self.toggle_done(task, var))
        checkbox.pack(side="left", padx=5, pady=3, fill="x", expand=True)
        if task['done']:
            checkbox.configure(state="disabled")

        delete_button = ctk.CTkButton(frame, text="削除", width=50, command=lambda: self.delete_task(task))
        delete_button.pack(side="right", padx=5)

    def delete_task(self, task):
        self.task_list.remove(task)
        self.save_tasks()
        self.render_tasks()

    def toggle_done(self, task, var):
        task['done'] = var.get()
        self.save_tasks()
        self.render_tasks()

    def toggle_filter(self):
        self.filtered = not self.filtered
        self.filter_button.configure(text="すべて表示" if self.filtered else "未完了のみ表示")
        self.render_tasks()

    def toggle_theme(self):
        self.theme_mode = "dark" if self.theme_mode == "light" else "light"
        ctk.set_appearance_mode(self.theme_mode.capitalize())

    def check_reminders(self):
        while True:
            now = datetime.datetime.now()
            for task in self.task_list:
                if not task['done']:
                    remind_time = datetime.datetime.fromisoformat(task['remind_at'])
                    if now >= remind_time:
                        notification.notify(title="リマインダー通知", message=task['content'], timeout=5)
                        task['remind_at'] = (now + datetime.timedelta(days=1)).isoformat()
                        self.save_tasks()
            time.sleep(30)

    def save_tasks(self):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.task_list, f, ensure_ascii=False, indent=2)

    def load_tasks(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                self.task_list = json.load(f)

if __name__ == "__main__":
    app = TaskManagerApp()
    app.mainloop()
