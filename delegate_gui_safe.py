import tkinter as tk
from tkinter import scrolledtext, messagebox
import requests
import time
import threading

class DelegationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Делегирование Яндекс 360 — Ввод Токена и ORG_ID")
        self.root.geometry("760x750")
        self.root.resizable(False, False)

        # === Заголовок ===
        title = tk.Label(root, text="Делегирование почты", font=("Arial", 16, "bold"))
        title.pack(pady=10)

        # === Поле ввода токена ===
        token_frame = tk.LabelFrame(root, text=" OAuth Токен (вставьте полностью) ", font=("Arial", 11, "bold"), padx=10, pady=10)
        token_frame.pack(padx=20, pady=10, fill="x")

        tk.Label(token_frame, text="Полный OAuth-токен:", font=("Arial", 10)).pack(anchor="w")
        self.token_entry = tk.Entry(token_frame, width=80, font=("Consolas", 9), show="*")
        self.token_entry.pack(pady=5, fill="x")
        self.token_entry.insert(0, "y0_AgAAAA...")  # Подсказка

        show_token_var = tk.BooleanVar()
        show_token_cb = tk.Checkbutton(token_frame, text="Показать токен", variable=show_token_var,
                                       command=lambda: self.toggle_token(show_token_var))
        show_token_cb.pack(anchor="w", pady=2)

        paste_token_btn = tk.Button(token_frame, text="Вставить токен", width=15, command=lambda: self.paste_to(self.token_entry))
        paste_token_btn.pack(anchor="w", pady=2)

        # === Поле ORG_ID ===
        org_frame = tk.LabelFrame(root, text=" ID Организации ", font=("Arial", 11, "bold"), padx=10, pady=5)
        org_frame.pack(padx=20, pady=5, fill="x")
        tk.Label(org_frame, text="ORG_ID:", font=("Arial", 10)).pack(anchor="w")
        self.org_id_entry = tk.Entry(org_frame, width=20, font=("Consolas", 10))
        self.org_id_entry.pack(pady=2)
        self.org_id_entry.insert(0, "8098389")  # ← ТВОЙ ORG_ID

        # === Поля email ===
        input_frame = tk.LabelFrame(root, text=" Email ", font=("Arial", 11, "bold"), padx=15, pady=10)
        input_frame.pack(padx=20, pady=10, fill="x")

        tk.Label(input_frame, text="Email владельца:(кого делегируем)", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.owner_email_entry = tk.Entry(input_frame, width=38, font=("Arial", 10))
        self.owner_email_entry.grid(row=0, column=1, padx=(5, 0), pady=5)
        self.owner_email_entry.insert(0, "mail@digital.gov.ru")

        paste_owner_btn = tk.Button(input_frame, text="Вставить", width=8, command=lambda: self.paste_to(self.owner_email_entry))
        paste_owner_btn.grid(row=0, column=2, padx=5, pady=5)

        tk.Label(input_frame, text="Email делегата:(кому даём доступ)", font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5)
        self.delegate_email_entry = tk.Entry(input_frame, width=38, font=("Arial", 10))
        self.delegate_email_entry.grid(row=1, column=1, padx=(5, 0), pady=5)
        self.delegate_email_entry.insert(0, "mail@digital.gov.ru")

        paste_delegate_btn = tk.Button(input_frame, text="Вставить", width=8, command=lambda: self.paste_to(self.delegate_email_entry))
        paste_delegate_btn.grid(row=1, column=2, padx=5, pady=5)

        # === Контекстное меню ===
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Вставить", command=lambda: self.root.focus_get().event_generate("<<Paste>>"))

        def show_context_menu(e):
            try:
                self.context_menu.tk_popup(e.x_root, e.y_root)
            finally:
                self.context_menu.grab_release()

        for entry in [self.token_entry, self.owner_email_entry, self.delegate_email_entry, self.org_id_entry]:
            entry.bind("<Button-3>", show_context_menu)
            entry.bind("<Control-v>", lambda e, ent=entry: self.paste_to(ent))

        # === Кнопки ===
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=15)

        self.enable_btn = tk.Button(btn_frame, text="ВКЛЮЧИТЬ ДЕЛЕГИРОВАНИЕ", font=("Arial", 11, "bold"),
                                    bg="#4CAF50", fg="white", width=28, height=2,
                                    command=lambda: self.run_task("enable"))
        self.enable_btn.pack(side="left", padx=10)

        self.disable_btn = tk.Button(btn_frame, text="ОТКЛЮЧИТЬ ДЕЛЕГИРОВАНИЕ", font=("Arial", 11, "bold"),
                                     bg="#F44336", fg="white", width=28, height=2,
                                     command=lambda: self.run_task("disable"))
        self.disable_btn.pack(side="right", padx=10)

        # === Лог ===
        log_label = tk.Label(root, text="Лог выполнения:", anchor="w", font=("Arial", 10, "bold"))
        log_label.pack(anchor="w", padx=20, pady=(10, 5))

        self.log_text = scrolledtext.ScrolledText(root, height=18, font=("Consolas", 9), state="disabled")
        self.log_text.pack(padx=20, pady=5, fill="both", expand=True)

        self.status = tk.Label(root, text="Введите токен и ORG_ID", relief="sunken", anchor="w", font=("Arial", 9))
        self.status.pack(side="bottom", fill="x")

    def toggle_token(self, var):
        self.token_entry.config(show="" if var.get() else "*")

    def paste_to(self, entry):
        try:
            entry.delete(0, tk.END)
            text = entry.clipboard_get()
            entry.insert(0, text)
            self.log(f"Вставлено: {text[:30]}... ({len(text)} символов)")
        except Exception as e:
            self.log(f"Ошибка вставки: {e}")

    def log(self, message):
        self.log_text.configure(state="normal")
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
        self.root.update()

    def set_status(self, text, color="black"):
        self.status.config(text=text, fg=color)

    def get_headers(self):
        token = self.token_entry.get().strip()
        if not token or len(token) < 50:
            raise Exception("Токен слишком короткий! Вставьте полный OAuth-токен.")
        return {
            "Authorization": f"OAuth {token}",
            "Content-Type": "application/json"
        }

    def run_task(self, mode):
        owner_email = self.owner_email_entry.get().strip()
        delegate_email = self.delegate_email_entry.get().strip()
        org_id = self.org_id_entry.get().strip()

        if not all([owner_email, delegate_email, org_id]):
            messagebox.showwarning("Ошибка", "Заполните все поля!")
            return

        self.enable_btn.config(state="disabled")
        self.disable_btn.config(state="disabled")
        self.set_status("Выполняется...", "blue")
        threading.Thread(target=self.execute, args=(mode, owner_email, delegate_email, org_id), daemon=True).start()

    def execute(self, mode, owner_email, delegate_email, org_id):
        try:
            headers = self.get_headers()
            self.log(f"ORG_ID: {org_id}")

            owner_id = self.get_user_id_by_email(owner_email, headers, org_id)
            delegate_id = self.get_user_id_by_email(delegate_email, headers, org_id)
            self.log(f"Владелец: {owner_id}")
            self.log(f"Делегат: {delegate_id}")

            if mode == "enable":
                self.enable_flow(owner_id, delegate_id, headers, org_id)
            elif mode == "disable":
                self.disable_flow(owner_id, delegate_id, headers, org_id)

            self.log("ГОТОВО!")
            self.set_status("Успешно", "green")
            messagebox.showinfo("Успех", "Операция завершена!")

        except Exception as e:
            self.log(f"ОШИБКА: {e}")
            self.set_status("Ошибка", "red")
            messagebox.showerror("Ошибка", str(e))
        finally:
            self.enable_btn.config(state="normal")
            self.disable_btn.config(state="normal")

    def get_user_id_by_email(self, email, headers, org_id):
        page = 1
        per_page = 100
        while True:
            url = f"https://api360.yandex.net/directory/v1/org/{org_id}/users"
            params = {"page": page, "perPage": per_page}
            r = requests.get(url, headers=headers, params=params)
            if r.status_code != 200:
                raise Exception(f"Ошибка API: {r.status_code} {r.text}")

            data = r.json()
            users = data.get("users", [])
            for user in users:
                if user.get("email", "").lower() == email.lower():
                    return user["id"]

            if len(users) < per_page:
                break
            page += 1

        raise Exception(f"Пользователь '{email}' не найден")

    def is_enabled(self, user_id, headers, org_id):
        url = f"https://api360.yandex.net/admin/v1/org/{org_id}/mailboxes/delegated/{user_id}"
        r = requests.get(url, headers=headers)
        return r.status_code == 200

    def enable_flow(self, user_id, delegate_id, headers, org_id):
        if self.is_enabled(user_id, headers, org_id):
            self.log("Делегирование уже включено.")
        else:
            self.log("Включаем делегирование...")
            r = requests.put(f"https://api360.yandex.net/admin/v1/org/{org_id}/mailboxes/delegated",
                             headers=headers, json={"resourceId": user_id})
            if r.status_code not in [200, 409]:
                raise Exception(f"Ошибка: {r.status_code} {r.text}")
            self.log("Делегирование включено.")

        self.log("Назначаем доступ...")
        r = requests.post(
            f"https://api360.yandex.net/admin/v1/org/{org_id}/mailboxes/set/{user_id}",
            headers=headers,
            params={"actorId": delegate_id, "notify": "none"},
            json={"roles": ["shared_mailbox_owner"]}
        )
        if r.status_code != 200:
            raise Exception(f"Ошибка: {r.status_code} {r.text}")
        task_id = r.json().get("taskId")
        self.log(f"Задача: {task_id}")
        self.wait_task(task_id, headers, org_id)

    def disable_flow(self, user_id, delegate_id, headers, org_id):
        self.log(f"Отключаем доступ...")
        r = requests.post(
            f"https://api360.yandex.net/admin/v1/org/{org_id}/mailboxes/set/{user_id}",
            headers=headers,
            params={"actorId": delegate_id, "notify": "none"},
            json={"roles": []}
        )
        if r.status_code == 200:
            task_id = r.json().get("taskId")
            self.log(f"Задача: {task_id}")
            self.wait_task(task_id, headers, org_id)
        else:
            self.log(f"Доступ уже снят: {r.status_code}")

        if self.is_enabled(user_id, headers, org_id):
            self.log("Выключаем делегирование...")
            r = requests.delete(f"https://api360.yandex.net/admin/v1/org/{org_id}/mailboxes/delegated/{user_id}",
                                headers=headers)
            if r.status_code != 200:
                raise Exception(f"Ошибка: {r.status_code}")
            self.log("Делегирование выключено.")
        else:
            self.log("Делегирование уже выключено.")

    def wait_task(self, task_id, headers, org_id):
        url = f"https://api360.yandex.net/admin/v1/org/{org_id}/mailboxes/tasks/{task_id}"
        self.log("Ожидание...")
        for i in range(30):
            time.sleep(4)
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                status = r.json().get("status")
                self.log(f"  [{i+1}] {status}")
                if status == "complete":
                    self.log("ЗАДАЧА ЗАВЕРШЕНА!")
                    return
                elif status == "failed":
                    raise Exception(f"Провал: {r.json().get('error')}")
        raise Exception("Таймаут")

# === ЗАПУСК ===
if __name__ == "__main__":
    root = tk.Tk()
    app = DelegationApp(root)
    root.mainloop()
