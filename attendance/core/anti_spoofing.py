import os
import cv2
import math
from ultralytics import YOLO


class AntiSpoofing:
    """
    Class xử lý anti-spoofing (liveness detection) bằng YOLO model.

    Cách dùng:
        anti_spoof = AntiSpoofing(model_path="models/best.pt", conf_threshold=0.8)
        is_live, confidence, label = anti_spoof.check_liveness(face_crop_bgr)
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AntiSpoofing, cls).__new__(cls)
        return cls._instance

    def __init__(self,
                 model_path=None,
                 conf_threshold=0.7, #0.8
                 classes=["fake", "real"]):

        if hasattr(self, "_initialized") and self._initialized:
            return
        self._initialized = True

        self.conf_threshold = conf_threshold
        self.classes = classes

        # ====== RESOLVE MODEL PATH CHUẨN ======
        if model_path is None:
            BASE_DIR = os.path.dirname(
                os.path.abspath(__file__))   # attendance/core
            PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
            model_path = os.path.join(
                PROJECT_ROOT,
                "anti-spoofing",
                "models",
                "best.pt"
            )

        model_path = os.path.abspath(model_path)
        self.model_path = model_path

        print("[AntiSpoofing] Model path resolved to:")
        print(" ", model_path)

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Không tìm thấy model anti-spoofing tại:\n{model_path}"
            )

        self.model = YOLO(model_path)
        print("[AntiSpoofing] Model loaded successfully")

    def check_liveness(self, face_crop_bgr):
        """
        Kiểm tra khuôn mặt có phải thật (live) hay không.

        Args:
            face_crop_bgr (np.ndarray): Ảnh khuôn mặt crop ở định dạng BGR (từ cv2)

        Returns:
            tuple: (is_live: bool, confidence: float, label: str)
                - is_live: True nếu là khuôn mặt thật (real/live)
                - confidence: confidence cao nhất
                - label: "real" hoặc "fake"
        """
        if face_crop_bgr is None or face_crop_bgr.size == 0:
            return False, 0.0, "invalid"

        # Chạy inference
        results = self.model(face_crop_bgr, stream=True, verbose=False)

        max_conf = 0.0
        best_label = "fake"

        for r in results:
            boxes = r.boxes
            for box in boxes:
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                if conf > max_conf:
                    max_conf = conf
                    best_label = self.classes[cls_id]

        is_live = (best_label == "real") and (max_conf >= self.conf_threshold)

        return is_live, max_conf, best_label

    def draw_result(self, img_bgr, bbox, is_live, conf, label):
        """
        Vẽ kết quả lên ảnh (dùng để debug hoặc hiển thị realtime)

        Args:
            img_bgr (np.ndarray): Ảnh gốc
            bbox (tuple): (left, top, right, bottom)
            is_live, conf, label: kết quả từ check_liveness

        Returns:
            img_bgr đã vẽ
        """
        left, top, right, bottom = bbox
        if is_live:
            color = (0, 255, 0)
            text = f"REAL {conf:.2f}"
        else:
            color = (0, 0, 255)
            text = f"SPOOF {conf:.2f}"

        cv2.rectangle(img_bgr, (left, top), (right, bottom), color, 2)
        cv2.putText(img_bgr, text, (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        return img_bgr
