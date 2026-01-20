import tkinter as tk
from PIL import Image, ImageTk
import cv2

from gui.base_ui import BaseFrame
from core.camera import Camera
from core.face_matcher import FaceMatcher
from database.db_manager import AttendanceDB
from core.attendance_logger import AttendanceLogger
from core.insightface_singleton import InsightFaceSingleton


class AttendanceUI(BaseFrame):
    # ================= CONFIG =================
    SIMILARITY_THRESHOLD = 0.45
    COOLDOWN_MAX = 60
    DETECT_INTERVAL = 2

    # =========================================
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # Layout
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        tk.Label(self, text="ĐIỂM DANH REALTIME",
                 font=("Arial", 20, "bold")).grid(row=0, column=0, pady=15)

        self.video_label = tk.Label(self, bg="black")
        self.video_label.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.status = tk.Label(self, text="Nhấn 'Bắt đầu' để điểm danh",
                               fg="blue", font=("Arial", 12))
        self.status.grid(row=2, column=0, pady=5)

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=3, column=0, pady=10)

        self.btn_start = tk.Button(btn_frame, text="Bắt đầu",
                                   width=15, command=self.start)
        self.btn_start.grid(row=0, column=0, padx=8)

        self.btn_stop = tk.Button(btn_frame, text="Dừng",
                                  width=15, command=self.stop, state="disabled")
        self.btn_stop.grid(row=0, column=1, padx=8)

        tk.Button(self, text="Quay lại", width=15,
                  command=self.back).grid(row=4, column=0, pady=15)

        # Runtime
        self.camera = None
        self.running = False
        self.photo_image = None
        self.frame_count = 0

        # InsightFace
        self.app = InsightFaceSingleton.get_instance(
            name="buffalo_l",
            providers=["CPUExecutionProvider"],
            det_size=(640, 640),
            ctx_id=0
        )

        self.matcher = FaceMatcher()
        self.db = AttendanceDB()
        self.attendance_logger = AttendanceLogger()

        self.cooldown_frames = 0
        self.marked_ids = set()

    # ==========================
    def start(self):
        try:
            self.camera = Camera()
            self.running = True
            self.marked_ids.clear()
            self.cooldown_frames = 0
            self.frame_count = 0

            self.status.config(text="Đang điểm danh... Nhìn thẳng camera",
                               fg="green")
            self.btn_start.config(state="disabled")
            self.btn_stop.config(state="normal")

            self.update_frame()

        except Exception as e:
            self.status.config(text=f"Lỗi camera: {e}", fg="red")

    # ==========================
    def update_frame(self):
        if not self.running or self.camera is None:
            return

        frame_bgr = self.camera.read()
        if frame_bgr is None:
            self.after(30, self.update_frame)
            return

        self.frame_count += 1

        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

        faces = []
        if self.frame_count % self.DETECT_INTERVAL == 0:
            small = cv2.resize(frame_rgb, None, fx=0.75, fy=0.75)
            faces = self.app.get(small)

        for face in faces:
            bbox = (face.bbox * (1 / 0.75)).astype(int)
            left, top, right, bottom = bbox

            embedding = face.normed_embedding
            if embedding is None:
                continue

            student_id, name, similarity = self.matcher.match(embedding)

            if student_id and similarity >= self.SIMILARITY_THRESHOLD:
                color = (0, 255, 0)
                label = f"{name} ({similarity:.2f})"

                if self.cooldown_frames <= 0 and student_id not in self.marked_ids:
                    if self.db.mark(student_id, name):
                        self.attendance_logger.log_attendance(
                            student_id, name, "Có mặt"
                        )
                        self.marked_ids.add(student_id)
                        self.cooldown_frames = self.COOLDOWN_MAX
                        self.status.config(
                            text=f"✅ Điểm danh thành công: {name}",
                            fg="#2ecc71"
                        )
            else:
                color = (0, 0, 255)
                label = "Unknown"

            cv2.rectangle(frame_bgr, (left, top),
                          (right, bottom), color, 2)
            cv2.putText(frame_bgr, label,
                        (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, color, 2)

        if self.cooldown_frames > 0:
            self.cooldown_frames -= 1

        img = Image.fromarray(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB))
        self.photo_image = ImageTk.PhotoImage(img)
        self.video_label.config(image=self.photo_image)

        self.after(30, self.update_frame)

    # ==========================
    def stop(self):
        self.running = False
        if self.camera:
            self.camera.release()
            self.camera = None

        self.photo_image = None  # (4)
        self.video_label.config(image="")

        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        self.status.config(text="Đã dừng. Nhấn 'Bắt đầu' để tiếp tục",
                           fg="blue")

    def back(self):
        self.stop()
        self.controller.show_frame("HomeUI")
