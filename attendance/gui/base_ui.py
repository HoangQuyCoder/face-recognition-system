import tkinter as tk

class BaseFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")  # ← Thêm background
        self.controller = controller
        self.pack(fill="both", expand=True)   # ← Đảm bảo fill toàn màn hình

    def show(self):
        self.lift()