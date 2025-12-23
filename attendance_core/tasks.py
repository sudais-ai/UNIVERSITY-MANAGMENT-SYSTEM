from datetime import date
from sqlalchemy.orm import Session
from .db import get_db
from .models import Student, Attendance
def open_window(course_code: str):
    db: Session = next(get_db())
    today = date.today()
    students = db.query(Student).filter(Student.active == True).all()
    for s in students:
        exists = db.query(Attendance).filter(Attendance.student_id==s.id, Attendance.date==today, Attendance.course_code==course_code).first()
        if not exists:
            db.add(Attendance(student_id=s.id, date=today, course_code=course_code, status="ABSENT"))
    db.commit()
def close_window(course_code: str):
    pass
