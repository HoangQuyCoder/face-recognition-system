import tkinter as tk
from gui.base_ui import BaseFrame

class HomeUI(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        tk.Label(self, text="FACE ATTENDANCE SYSTEM",
                 font=("Arial", 24, "bold")).pack(pady=40)

        tk.Button(self, text="Đăng ký sinh viên",
                  width=30, height=2,
                  command=lambda: controller.show_frame("EnrollUI")).pack(pady=10)

        tk.Button(self, text="Điểm danh",
                  width=30, height=2,
                  command=lambda: controller.show_frame("AttendanceUI")).pack(pady=10)

        tk.Button(self, text="Quản lý sinh viên đã đăng ký",
                  width=30, height=2,
                  command=self.open_student_list).pack(pady=10)

        tk.Button(self, text="Xem lịch sử điểm danh",
                width=30, height=2,
                command=self.open_attendance_log).pack(pady=10)
        
        tk.Button(self, text="Thoát",
                  width=30, height=2,
                  command=controller.quit).pack(pady=20)

    def open_student_list(self):
        from core.student_manager import StudentListWindow
        StudentListWindow(self)

    def open_attendance_log(self):
        from core.attendance_logger import AttendanceLogWindow
        AttendanceLogWindow(self)