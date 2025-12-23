import os
from config import Config
from attendance_engine.camera_worker import CameraWorker
if __name__ == "__main__":
    cfg = {
        "RECOG_DISTANCE_THRESHOLD": Config.RECOG_DISTANCE_THRESHOLD,
        "RECOG_MODEL": Config.RECOG_MODEL,
        "RECOG_BLUR_THRESHOLD": Config.RECOG_BLUR_THRESHOLD,
        "RECOG_CONSEC_FRAMES": Config.RECOG_CONSEC_FRAMES,
        "RECOG_MIN_FACE_SIZE": Config.RECOG_MIN_FACE_SIZE,
        "CAMERA_POLL_INTERVAL": Config.CAMERA_POLL_INTERVAL,
    }
    worker = CameraWorker(
        camera_id=os.environ.get("CAMERA_ID","RoomA-Cam1"),
        course_code=os.environ.get("COURSE_CODE","CS101"),
        source=int(os.environ.get("VIDEO_SOURCE","0")),
        cfg=cfg
    )
    try:
        worker.run()
    except KeyboardInterrupt:
        worker.stop()
