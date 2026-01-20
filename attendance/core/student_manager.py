import os
import pickle
import tkinter as tk
from tkinter import ttk, messagebox

class StudentManager:
    def __init__(self, db_path="database/embeddings.pkl"):
        self.db_path = db_path
        self.students = self.load_students()

    def load_students(self):
        """Đọc danh sách sinh viên từ file pickle"""
        if not os.path.exists(self.db_path):
            return []
        try:
            with open(self.db_path, "rb") as f:
                data = pickle.load(f)
            return data  # list of dict: {"id": ..., "name": ..., "embedding": ...}
        except Exception as e:
            print(f"Lỗi đọc file embeddings.pkl: {e}")
            return []

    def get_all_students(self):
        return self.students

    def get_student_by_id(self, student_id):
        for student in self.students:
            if student["id"] == student_id:
                return student
        return None

    def delete_student(self, student_id):
        """Xóa sinh viên theo mã SV"""
        self.students = [s for s in self.students if s["id"] != student_id]
        # Lưu lại file
        try:
            with open(self.db_path, "wb") as f:
                pickle.dump(self.students, f)
            return True
        except Exception as e:
            print(f"Lỗi xóa sinh viên: {e}")
            return False


class StudentListWindow(tk.Toplevel):
    """Cửa sổ hiển thị danh sách sinh viên đã đăng ký"""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Danh sách sinh viên đã đăng ký")
        self.geometry("800x600")
        self.resizable(True, True)

        self.manager = StudentManager()

        # Tiêu đề
        tk.Label(self, text="DANH SÁCH SINH VIÊN",
                 font=("Arial", 18, "bold")).pack(pady=10)

        # Treeview hiển thị danh sách
        columns = ("Mã SV", "Họ tên", "Số mẫu đăng ký")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=20)
        self.tree.heading("Mã SV", text="Mã SV")
        self.tree.heading("Họ tên", text="Họ tên")
        self.tree.heading("Số mẫu đăng ký", text="Số mẫu đăng ký")

        self.tree.column("Mã SV", width=150, anchor="center")
        self.tree.column("Họ tên", width=300)
        self.tree.column("Số mẫu đăng ký", width=200, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Nút xóa (chọn sinh viên rồi nhấn xóa)
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Xóa sinh viên đã chọn", bg="#e74c3c", fg="white",
                  command=self.delete_selected).pack(side="left", padx=10)

        tk.Button(btn_frame, text="Làm mới danh sách", bg="#3498db", fg="white",
                  command=self.refresh_list).pack(side="left", padx=10)

        tk.Button(btn_frame, text="Đóng", bg="#95a5a6", fg="white",
                  command=self.destroy).pack(side="left", padx=10)

        # Load danh sách lần đầu
        self.refresh_list()

    def refresh_list(self):
        """Tải lại và hiển thị danh sách"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        students = self.manager.get_all_students()
        for student in students:
            # Vì chúng ta lưu trung bình embedding, không lưu số mẫu gốc
            # Ở đây hiển thị placeholder hoặc bạn có thể sửa để lưu thêm info
            self.tree.insert("", "end", values=(
                student["id"],
                student["name"],
                "Đã đăng ký"  # Có thể thay bằng số lượng nếu bạn lưu thêm
            ))

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một sinh viên để xóa!")
            return

        values = self.tree.item(selected[0])["values"]
        student_id = values[0]
        name = values[1]

        if messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc muốn xóa sinh viên\nMã SV: {student_id}\nHọ tên: {name}?"):
            if self.manager.delete_student(student_id):
                messagebox.showinfo("Thành công", "Đã xóa sinh viên!")
                self.refresh_list()
            else:
                messagebox.showerror("Lỗi", "Không thể xóa sinh viên!")