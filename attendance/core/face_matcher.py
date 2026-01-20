import numpy as np
import pickle
import os

class FaceMatcher:
    def __init__(self, db_path="database/embeddings.pkl", threshold=0.45):
        """
        threshold: cosine similarity threshold (0.0 đến 1.0)
        - > 0.5: khá nghiêm ngặt
        - 0.4 ~ 0.5: khuyến nghị khởi điểm cho InsightFace buffalo_l
        """
        self.threshold = threshold
        self.embeddings = None  # np.array shape (N, 512)
        self.ids = []
        self.names = []

        if os.path.exists(db_path):
            with open(db_path, "rb") as f:
                data = pickle.load(f)

            if data:
                # Tách thành lists trước rồi chuyển thành np.array
                self.embeddings = np.array([item["embedding"] for item in data])
                self.ids = [item["id"] for item in data]
                self.names = [item["name"] for item in data]

                # Đảm bảo tất cả embeddings đã normalize (norm=1)
                norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
                self.embeddings /= np.maximum(norms, 1e-10)  # tránh chia 0

            print(f"Loaded {len(self.ids)} known faces from {db_path}")
        else:
            print("Không tìm thấy file embeddings.pkl - chưa có dữ liệu nhận diện")

    def match(self, query_embedding):
        """
        Input: query_embedding (np.array shape (512,))
        Output: (student_id, name, similarity_score) hoặc (None, None, score)
        """
        if self.embeddings is None or len(self.embeddings) == 0:
            return None, None, 0.0

        # Đảm bảo query cũng đã normalize (InsightFace thường đã làm)
        query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-10)

        # Tính cosine similarity = dot product (vì cả hai đã norm=1)
        similarities = np.dot(self.embeddings, query_norm)

        idx = np.argmax(similarities)
        best_sim = similarities[idx]

        if best_sim >= self.threshold:
            return self.ids[idx], self.names[idx], best_sim
        else:
            return None, None, best_sim