import numpy as np, face_recognition
from sqlalchemy.orm import Session
from attendance_core.db import get_db
from attendance_core.models import FaceEncoding
class Recognizer:
    def __init__(self, distance_threshold: float, model: str):
        self.distance_threshold = distance_threshold
        self.model = model
        self.student_ids = []
        self.known_encodings = None
        self._load()
    def _load(self):
        db: Session = next(get_db())
        rows = db.query(FaceEncoding).filter(FaceEncoding.is_average == True).all()
        rows.sort(key=lambda r: r.student_id)
        encs, sids = [], []
        for r in rows:
            encs.append(np.frombuffer(r.encoding_vector, dtype=np.float64))
            sids.append(r.student_id)
        self.student_ids = sids
        self.known_encodings = np.vstack(encs) if encs else np.empty((0,128), dtype=np.float64)
    def match(self, face_encoding):
        if self.known_encodings is None or self.known_encodings.shape[0] == 0:
            return None, 1.0
        distances = face_recognition.face_distance(self.known_encodings, face_encoding)
        idx = int(np.argmin(distances))
        best_dist = float(distances[idx])
        if best_dist <= self.distance_threshold:
            return self.student_ids[idx], best_dist
        return None, best_dist
