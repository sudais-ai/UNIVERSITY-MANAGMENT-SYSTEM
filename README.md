# Real-time University Attendance (Face Recognition)
- Create venv: python -m venv .venv; .\.venv\Scripts\activate
- Install: pip install -r requirements.txt
- Env (PowerShell): \ = "postgresql://attendance_user:password@localhost:5432/attendance_db"
- Init DB:
  python -c "from app import app; from attendance_core.db import Base,_engine; Base.metadata.create_all(bind=_engine)"
- Run web:
  \ = "app.py"; flask run --host=0.0.0.0 --port=5000
- Make admin (SQL): update users set role='admin' where email='YOUR_EMAIL';
- Add students: /admin/students/new (5+ images)
- Open window: python -c "from attendance_core.tasks import open_window; open_window('CS101')"
- Run camera:
  \="RoomA-Cam1"; \="CS101"; \="0"; python .\run_camera.py
