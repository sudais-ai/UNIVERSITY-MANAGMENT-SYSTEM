import cv2, time, face_recognition
from datetime import datetime, date
from sqlalchemy.orm import Session
from attendance_core.db import get_db
from attendance_core.models import Attendance
from .utils import is_blurry, ensure_min_face_size, face_distance_to_conf
from .recognizer import Recognizer
from .registry import RecognitionRegistry
class CameraWorker:
    def __init__(self, camera_id: str, course_code: str, source=0, cfg=None):
        self.camera_id = camera_id
        self.course_code = course_code
        self.source = source
        self.cfg = cfg
        self.cap = cv2.VideoCapture(self.source)
        self.recognizer = Recognizer(cfg["RECOG_DISTANCE_THRESHOLD"], cfg["RECOG_MODEL"])
        self.registry = RecognitionRegistry(cfg["RECOG_CONSEC_FRAMES"])
        self.running = True
    def run(self):
        while self.running:
            ok, frame = self.cap.read()
            if not ok:
                time.sleep(0.05); continue
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if is_blurry(gray, self.cfg["RECOG_BLUR_THRESHOLD"]):
                time.sleep(self.cfg["CAMERA_POLL_INTERVAL"]); continue
            boxes = face_recognition.face_locations(rgb, model=self.cfg["RECOG_MODEL"])
            if not boxes:
                time.sleep(self.cfg["CAMERA_POLL_INTERVAL"]); continue
            encs = face_recognition.face_encodings(rgb, boxes)
            for box, enc in zip(boxes, encs):
                if not ensure_min_face_size(box, self.cfg["RECOG_MIN_FACE_SIZE"]):
                    continue
                sid, dist = self.recognizer.match(enc)
                conf = face_distance_to_conf(dist)
                if sid is not None and conf >= 0.90:
                    self.registry.push_candidate(self.camera_id, sid)
                    confirmed = self.registry.get_confirmed(self.camera_id)
                    if confirmed:
                        self._mark_present_once(confirmed)
            time.sleep(self.cfg["CAMERA_POLL_INTERVAL"])
    def _mark_present_once(self, student_id: int):
        db: Session = next(get_db())
        today = date.today()
        rec = db.query(Attendance).filter(Attendance.student_id == student_id, Attendance.date == today, Attendance.course_code == self.course_code).first()
        if rec:
            if rec.status != "PRESENT":
                rec.status = "PRESENT"
                rec.time_in = datetime.utcnow()
                rec.camera_id = self.camera_id
                db.commit()
            return
        db.add(Attendance(student_id=student_id, date=today, time_in=datetime.utcnow(), course_code=self.course_code, camera_id=self.camera_id, status="PRESENT"))
        db.commit()
    def stop(self):
        self.running = False
        self.cap.release()
