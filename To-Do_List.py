import tkinter as tk
from tkinter import simpledialog, messagebox
from datetime import datetime

class ToDoListApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List")
        self.tasks = self.load_tasks()
        
        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=80)

        # Title Label
        self.title_label = tk.Label(self.root, text="To-do List", font=("Papyrus", 16))
        self.title_label.pack(pady=(10, 5))
        self.title_label.place(relx=0.5, rely=0.025, anchor="center")

        self.listbox_font = ("Papyrus", 12)  # Set the font to Papyrus and size to 12
        self.listbox = tk.Listbox(self.frame, selectmode=tk.SINGLE, width=100, height=40, font=self.listbox_font)
        self.listbox.pack(side=tk.LEFT)

        self.scrollbar = tk.Scrollbar(self.frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)

        self.add_button = tk.Button(self.root, text="Add Task", command=self.add_task)
        self.add_button.pack(pady=5)

        self.remove_button = tk.Button(self.root, text="Remove Task", command=self.remove_task)
        self.remove_button.pack(pady=5)

        self.refresh_button = tk.Button(self.root, text="Refresh & Sort", command=self.refresh_and_sort)
        self.refresh_button.pack(pady=5)

        # Drag-and-drop setup
        self.listbox.bind('<ButtonPress-1>', self.on_button_press)
        self.listbox.bind('<ButtonRelease-1>', self.on_button_release)
        self.listbox.bind('<B1-Motion>', self.on_drag)

        self.listbox.bind('<Button-3>', self.edit_task_right_click)

        self.dragged_index = None

        self.update_listbox()

    def add_task(self):
        task = simpledialog.askstring("Add Task", "Enter a task:")
        if task:
            while True:
                deadline = simpledialog.askstring("Deadline of said task", "Enter deadline (YYYY-MM-DD or YYYY-MM-DD HH:MM):")
                if deadline is None:  # If the user cancels the dialog
                    deadline = "="
                    break
                elif self.validate_deadline(deadline):
                    break
                else:
                    messagebox.showerror("Invalid Deadline", "Please enter a valid deadline in the format YYYY-MM-DD, YYYY-MM-DD HH:MM, or =.")
            self.tasks.append({"text": task, "status": "empty", "deadline": deadline})  
            self.sort_tasks()  # Sort tasks after adding
            self.update_listbox()
            self.save_tasks()

    def remove_task(self):
        selected_index = self.listbox.curselection()
        if selected_index:
            del self.tasks[selected_index[0]]
            self.update_listbox()
            self.save_tasks()

    def refresh_and_sort(self):
        self.sort_tasks()

    def edit_task_right_click(self, event):
        selected_index = self.listbox.nearest(event.y)  # Get the task nearest to the clicked position
        if selected_index is not None:
            old_task = self.tasks[selected_index]["text"]  # Get the current task text
            old_deadline = self.tasks[selected_index]["deadline"]  # Get the current task deadline
            new_task = simpledialog.askstring("Edit Task", "Edit your task (name):", initialvalue=old_task)
            if new_task:  # If the user provides a new task
                self.tasks[selected_index]["text"] = new_task  # Update the task in the list

            while True:
                new_deadline = simpledialog.askstring("Edit Task", "Edit your task (deadline):", initialvalue=old_deadline)
                if new_deadline is None:  # If the user cancels the dialog
                    new_deadline = "="
                    break
                elif self.validate_deadline(new_deadline):
                    break
                else:
                    messagebox.showerror("Invalid Deadline", "Please enter a valid deadline in the format YYYY-MM-DD, YYYY-MM-DD HH:MM, or =.")

            self.tasks[selected_index]["deadline"] = new_deadline  
            self.sort_tasks()  # Sort tasks after editing
            self.update_listbox()  # Refresh the listbox
            self.save_tasks()  # Save the updated tasks to the file

    def validate_deadline(self, deadline):
        if deadline == "=":
            return True  # Allow "=" as a valid deadline
        try:
            # Check for YYYY-MM-DD format
            if len(deadline) == 10:
                datetime.strptime(deadline, "%Y-%m-%d")
                return True
            # Check for YYYY-MM-DD HH:MM format
            elif len(deadline) == 16:
                datetime.strptime(deadline, "%Y-%m-%d %H:%M")
                return True
            return False
        except ValueError:
            return False

    def sort_tasks(self):
        # Sort tasks by deadline, considering the format "YYYY-MM-DD HH:MM"
        def sort_key(task):
            if task["deadline"] == "=":
                return datetime.max  # Treat "=" as the latest possible date
            try:
                # Ensure all dates are in standard format
                if len(task["deadline"]) == 10:
                    return datetime.strptime(task["deadline"], "%Y-%m-%d")
                else:
                    return datetime.strptime(task["deadline"], "%Y-%m-%d %H:%M")
            except ValueError:
                return datetime.max  # Handle any invalid date formats by treating them as the latest date

        self.tasks.sort(key=sort_key)
        self.update_listbox()

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for task in self.tasks:
            status_symbol = self.get_status_symbol(task["status"])
            display_text = f"{status_symbol} {task['text']} {task['deadline']}"
            self.listbox.insert(tk.END, display_text)

    def get_status_symbol(self, status):
        if status == "empty":
            return "[ ]"
        elif status == "tick":
            return "[✔]"
        elif status == "cross":
            return "[✖]"
        else:
            return "[ ]"

    def toggle_status(self, event):
        selected_index = self.listbox.curselection()
        if selected_index:
            task = self.tasks[selected_index[0]]
            # Cycle through the statuses in the order: empty -> tick -> cross -> empty
            if task["status"] == "empty":
                task["status"] = "tick"
            elif task["status"] == "tick":
                task["status"] = "cross"
            elif task["status"] == "cross":
                task["status"] = "empty"
            self.update_listbox()
            self.save_tasks()  # Save changes to file

    def on_button_press(self, event):
        self.dragged_index = self.listbox.nearest(event.y)

    def on_button_release(self, event):
        self.dragged_index = None

    def on_drag(self, event):
        if self.dragged_index is not None:
            index = self.listbox.nearest(event.y)
            if index != self.dragged_index:
                self.tasks.insert(index, self.tasks.pop(self.dragged_index))
                self.update_listbox()
                self.dragged_index = index

    def save_tasks(self):
        with open("tasks.txt", "w") as f:
            for task in self.tasks:
                f.write(f"{task['text']}|{task['status']}|{task['deadline']}\n")

    def load_tasks(self):
        try:
            with open("tasks.txt", "r") as f:
                tasks = []
                for line in f.readlines():
                    parts = line.strip().split('|')
                    if len(parts) == 3:  # Ensure each line has text, status, and deadline
                        tasks.append({"text": parts[0], "status": parts[1], "deadline": parts[2]})
                return tasks
        except FileNotFoundError:
            return []

if __name__ == "__main__":
    root = tk.Tk()
    app = ToDoListApp(root)
    root.bind('<Button-1>', app.toggle_status)  # Toggle status on left click
    root.mainloop()