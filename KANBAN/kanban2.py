import tkinter as tk
from tkinter import simpledialog, messagebox
import json
import os

FILE = "kanban_data.json"

class KanbanApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tablero Kanban")
        self.data = {"Qué hacer": [], "Haciendo": [], "Hecho": []}
        self.drag_data = {"widget": None, "x": 0, "y": 0}

        self.create_menu()
        self.main_frame = None

        if os.path.exists(FILE):
            self.load_data()

    def create_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="KANBAN VISUAL", font=("Arial", 20)).pack(pady=10)

        tk.Button(self.root, text="Empezar", command=self.start_board, width=20).pack(pady=5)
        tk.Button(self.root, text="Reiniciar todo", command=self.reset_all, width=20).pack(pady=5)
        tk.Button(self.root, text="Salir", command=self.root.quit, width=20).pack(pady=5)

    def start_board(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.columns = {}

        for col in ["Qué hacer", "Haciendo", "Hecho"]:
            frame = tk.Frame(self.main_frame, bg="#ddd", width=200)
            frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
            tk.Label(frame, text=col, font=("Arial", 14, "bold")).pack(pady=5)
            self.columns[col] = frame

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Añadir", command=self.add_task).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Quitar", command=self.remove_task).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Menú", command=self.create_menu).pack(side=tk.LEFT, padx=10)

        self.render_tasks()

    def create_postit(self, parent, text, col_name):
        postit = tk.Label(parent, text=text, bg="lightyellow", relief=tk.RAISED, bd=2, padx=5, pady=5)
        postit.pack(pady=4, padx=10, fill=tk.X)
        postit.bind("<ButtonPress-1>", self.on_start_drag)
        postit.bind("<ButtonRelease-1>", lambda e, w=postit, c=col_name: self.on_drop(e, w, c))
        postit.bind("<B1-Motion>", self.on_drag)

    def on_start_drag(self, event):
        widget = event.widget
        self.drag_data["widget"] = widget
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        widget.lift()

    def on_drag(self, event):
        widget = self.drag_data["widget"]
        widget.place(in_=self.root, x=event.x_root - self.drag_data["x"],
                y=event.y_root - self.drag_data["y"])

    def on_drop(self, event, widget, from_col):
        widget.place_forget()
        for col, frame in self.columns.items():
            if frame.winfo_rootx() < event.x_root < frame.winfo_rootx() + frame.winfo_width():
                self.data[from_col].remove(widget["text"])
                self.data[col].append(widget["text"])
                self.render_tasks()
                self.save_data()
                return

    def add_task(self):
        task = simpledialog.askstring("Nueva tarea", "Escribe el nombre de la tarea:")
        if task:
            self.data["Qué hacer"].append(task)
            self.render_tasks()
            self.save_data()

    def remove_task(self):
        task = simpledialog.askstring("Eliminar tarea", "Escribe el nombre exacto de la tarea:")
        if task:
            for col in self.data:
                if task in self.data[col]:
                    self.data[col].remove(task)
                    self.render_tasks()
                    self.save_data()
                    return
            messagebox.showinfo("No encontrado", "Esa tarea no existe.")

    def render_tasks(self):
        for col, frame in self.columns.items():
            for widget in frame.winfo_children():
                if isinstance(widget, tk.Label) and widget["text"] != col:
                    widget.destroy()
            for task in self.data[col]:
                self.create_postit(frame, task, col)

    def reset_all(self):
        if os.path.exists(FILE):
            os.remove(FILE)
        self.data = {"Qué hacer": [], "Haciendo": [], "Hecho": []}
        messagebox.showinfo("Reinicio", "Tablero y papelera vaciados.")
        self.create_menu()

    def save_data(self):
        with open(FILE, "w") as f:
            json.dump(self.data, f)

    def load_data(self):
        with open(FILE, "r") as f:
            self.data = json.load(f)

if __name__ == "__main__":
    root = tk.Tk()
    app = KanbanApp(root)
    root.geometry("700x500")
    root.mainloop()
