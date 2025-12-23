import os
from datetime import timedelta
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL","postgresql://attendance_user:password@localhost:5432/attendance_db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "storage/face_images")
    ENCODING_FOLDER = os.environ.get("ENCODING_FOLDER", "storage/encodings")
    RECOG_CONSEC_FRAMES = 7
    RECOG_BLUR_THRESHOLD = 120.0
    RECOG_DISTANCE_THRESHOLD = 0.45
    RECOG_MIN_FACE_SIZE = 80
    RECOG_MODEL = "cnn"
    CAMERA_POLL_INTERVAL = 0.01
