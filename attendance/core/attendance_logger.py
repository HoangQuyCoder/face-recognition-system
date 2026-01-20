import os
import csv
import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog

class AttendanceLogger:
    def __init__(self, log_path="database/attendance_log.csv"):
        self.log_path = log_path
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        # Tạo file header nếu chưa tồn tại
        if not os.path.exists(log_path):
            with open(log_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Mã SV", "Họ tên", "Thời gian điểm danh", "Ngày", "Trạng thái"])

    def log_attendance(self, student_id, name, status="Có mặt"):
        """Ghi log điểm danh"""
        now = datetime.datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%Y-%m-%d")

        with open(self.log_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([student_id, name, time_str, date_str, status])

    def get_logs_by_date(self, date_str):
        """Lấy danh sách điểm danh theo ngày (YYYY-MM-DD)"""
        if not os.path.exists(self.log_path):
            return []

        logs = []
        with open(self.log_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # Bỏ header
            for row in reader:
                if len(row) >= 4 and row[3] == date_str:
                    logs.append(row)
        return logs

    def get_all_logs(self):
        """Lấy toàn bộ lịch sử"""
        if not os.path.exists(self.log_path):
            return []
        logs = []
        with open(self.log_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                logs.append(row)
        return logs


class AttendanceLogWindow(tk.Toplevel):
    """Cửa sổ xem lịch sử điểm danh"""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Lịch sử điểm danh")
        self.geometry("1000x700")
        self.resizable(True, True)

        self.logger = AttendanceLogger()

        # Tiêu đề
        tk.Label(self, text="LỊCH SỬ ĐIỂM DANH",
                 font=("Arial", 18, "bold")).pack(pady=10)

        # Frame lọc
        filter_frame = tk.Frame(self)
        filter_frame.pack(pady=10, fill="x", padx=20)

        tk.Label(filter_frame, text="Chọn ngày:", font=("Arial", 11)).pack(side="left", padx=5)
        self.date_entry = tk.Entry(filter_frame, width=15)
        self.date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        self.date_entry.pack(side="left", padx=5)

        tk.Button(filter_frame, text="Lọc theo ngày", command=self.load_by_date).pack(side="left", padx=10)
        tk.Button(filter_frame, text="Xem tất cả", command=self.load_all).pack(side="left", padx=10)
        tk.Button(filter_frame, text="Xuất CSV", command=self.export_csv).pack(side="left", padx=10)

        # Treeview hiển thị
        columns = ("Mã SV", "Họ tên", "Thời gian", "Ngày", "Trạng thái")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=25)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        # Load mặc định hôm nay
        self.load_by_date()

    def load_by_date(self):
        date_str = self.date_entry.get().strip()
        try:
            datetime.datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Lỗi", "Định dạng ngày không đúng (YYYY-MM-DD)")
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        logs = self.logger.get_logs_by_date(date_str)
        for log in logs:
            self.tree.insert("", "end", values=log)

        if not logs:
            self.tree.insert("", "end", values=("", "Chưa có điểm danh nào trong ngày này", "", "", ""))

    def load_all(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        logs = self.logger.get_all_logs()
        for log in logs:
            self.tree.insert("", "end", values=log)

        if not logs:
            self.tree.insert("", "end", values=("", "Chưa có lịch sử điểm danh", "", "", ""))

    def export_csv(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Xuất lịch sử điểm danh"
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Mã SV", "Họ tên", "Thời gian", "Ngày", "Trạng thái"])
                for item in self.tree.get_children():
                    values = self.tree.item(item)["values"]
                    writer.writerow(values)
            messagebox.showinfo("Thành công", f"Đã xuất file: {file_path}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất file: {e}")