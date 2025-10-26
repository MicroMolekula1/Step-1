import tkinter as tk
from tkinter import scrolledtext, Entry, Button, Label, StringVar
import re
import os


class VFSEmulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Virtual File System (VFS) Emulator")
        self.current_dir = "/home/user"
        self.file_system = {
            "/home/user": ["file1.txt", "file2.txt", "documents", "pictures"],
            "/home/user/documents": ["report.doc", "notes.txt", "projects"],
            "/home/user/documents/projects": ["project1.py", "project2.java"],
            "/home/user/pictures": ["photo1.jpg", "photo2.png"]
        }

        self.create_widgets()

    def create_widgets(self):
        self.output_area = scrolledtext.ScrolledText(self.root, width=80, height=20, state='disabled')
        self.output_area.pack(padx=10, pady=10)

        input_frame = tk.Frame(self.root)
        input_frame.pack(padx=10, pady=5, fill=tk.X)

        self.current_dir_label = Label(input_frame, text=f"{self.current_dir}$")
        self.current_dir_label.pack(side=tk.LEFT)

        self.input_var = StringVar()
        self.input_entry = Entry(input_frame, textvariable=self.input_var, width=70)
        self.input_entry.pack(side=tk.LEFT, padx=5)
        self.input_entry.bind('<Return>', self.process_command)

        Button(input_frame, text="Execute", command=self.process_command).pack(side=tk.LEFT)

        self.print_output("Добро пожаловать в VFS Emulator v1.0")
        self.print_output("Доступные команды: ls, cd, pwd, exit")
        self.print_output("")

    def print_output(self, text):
        self.output_area.config(state='normal')
        self.output_area.insert(tk.END, text + "\n")
        self.output_area.see(tk.END)
        self.output_area.config(state='disabled')

    def update_prompt(self):
        self.current_dir_label.config(text=f"{self.current_dir}$")

    def parse_command(self, input_text):
        tokens = re.findall(r'\"([^\"]*)\"|\'([^\']*)\'|(\S+)', input_text)
        return [token[0] or token[1] or token[2] for token in tokens if any(token)]

    def normalize_path(self, path):
        """Нормализация пути с учетом текущей директории"""
        if path.startswith('/'):
            return path
        else:
            # Исправлено: правильное объединение путей
            if self.current_dir == "/":
                return f"/{path}"
            else:
                return f"{self.current_dir}/{path}"

    def path_exists(self, path):
        return path in self.file_system

    def process_command(self, event=None):
        command_text = self.input_var.get().strip()
        self.input_var.set("")

        if not command_text:
            return

        self.print_output(f"{self.current_dir}$ {command_text}")

        tokens = self.parse_command(command_text)
        if not tokens:
            return

        command = tokens[0].lower()
        args = tokens[1:]

        if command == "exit":
            self.print_output("Завершение работы VFS Emulator...")
            self.root.after(1000, self.root.destroy)

        elif command == "ls":
            self.cmd_ls(args)

        elif command == "cd":
            self.cmd_cd(args)

        elif command == "pwd":
            self.cmd_pwd(args)

        else:
            self.print_output(f"Ошибка: неизвестная команда '{command}'")

    def cmd_ls(self, args):
        if args:
            path = self.normalize_path(args[0])
            if self.path_exists(path):
                files = self.file_system[path]
                self.print_output(f"Содержимое {path}:")
                for file in files:
                    self.print_output(f"  {file}")
            else:
                self.print_output(f"ls: невозможно получить доступ к '{args[0]}': Нет такого файла или каталога")
        else:
            files = self.file_system[self.current_dir]
            self.print_output("Содержимое текущей директории:")
            for file in files:
                self.print_output(f"  {file}")

    def cmd_cd(self, args):
        if len(args) == 0:
            self.current_dir = "/home/user"
            self.update_prompt()
            self.print_output(f"Переход в домашнюю директорию: {self.current_dir}")

        elif len(args) > 1:
            self.print_output("cd: слишком много аргументов")

        else:
            target_path = self.normalize_path(args[0])

            # Обработка ..
            if args[0] == "..":
                if self.current_dir != "/":
                    parent_dir = os.path.dirname(self.current_dir)
                    if parent_dir == "":
                        parent_dir = "/"
                    self.current_dir = parent_dir
                    self.update_prompt()
                    self.print_output(f"Переход в родительскую директорию: {self.current_dir}")
                else:
                    self.print_output("cd: уже в корневой директории")

            elif args[0] == ".":
                self.print_output(f"Остаемся в текущей директории: {self.current_dir}")

            elif self.path_exists(target_path):
                self.current_dir = target_path
                self.update_prompt()
                self.print_output(f"Переход в директорию: {self.current_dir}")

            else:
                self.print_output(f"cd: невозможно перейти в '{args[0]}': Нет такого файла или каталога")

    def cmd_pwd(self, args):
        self.print_output(self.current_dir)


def main():
    root = tk.Tk()
    emulator = VFSEmulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()