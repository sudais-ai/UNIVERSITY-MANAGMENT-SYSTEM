from flask import render_template, session, redirect, url_for
from sqlalchemy.orm import Session
from attendance_core.db import get_db
from attendance_core.models import User, Student, Attendance
from . import student_bp
@student_bp.get("/dashboard")
def dashboard():
    if session.get("role") != "student":
        return redirect(url_for("auth.login_get"))
    db: Session = next(get_db())
    user_id = session.get("uid")
    user = db.get(User, user_id)
    stu = db.query(Student).filter(Student.user_id == user_id).first()
    records, pct = [], 0.0
    if stu:
        q = db.query(Attendance).filter(Attendance.student_id == stu.id)
        total = q.count()
        present = q.filter(Attendance.status == "PRESENT").count()
        pct = (present/total*100.0) if total else 0.0
        records = q.order_by(Attendance.date.desc()).limit(120).all()
    return render_template("student/dashboard.html", user=user, records=records, pct=pct)
