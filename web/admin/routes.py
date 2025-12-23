from flask import render_template, request, redirect, url_for, flash, session, current_app, send_file
from sqlalchemy.orm import Session
from datetime import datetime, date
import numpy as np, io, os, json, face_recognition
from pandas import DataFrame
from attendance_core.db import get_db
from attendance_core.models import Student, FaceEncoding, Attendance, AuditLog
from . import admin_bp
def require_admin():
    return session.get("role") == "admin"
@admin_bp.get("/dashboard")
def dashboard():
    if not require_admin(): return redirect(url_for("auth.login_get"))
    db: Session = next(get_db())
    total_students = db.query(Student).count()
    today = date.today()
    present = db.query(Attendance).filter(Attendance.date == today, Attendance.status == "PRESENT").count()
    absent = db.query(Attendance).filter(Attendance.date == today, Attendance.status == "ABSENT").count()
    return render_template("admin/dashboard.html", total_students=total_students, present=present, absent=absent)
@admin_bp.get("/students")
def students_list():
    if not require_admin(): return redirect(url_for("auth.login_get"))
    db: Session = next(get_db())
    students = db.query(Student).order_by(Student.created_at.desc()).all()
    return render_template("admin/students.html", students=students)
@admin_bp.get("/students/new")
def student_new_get():
    if not require_admin(): return redirect(url_for("auth.login_get"))
    return render_template("admin/student_new.html")
@admin_bp.post("/students/new")
def student_new_post():
    if not require_admin(): return redirect(url_for("auth.login_get"))
    reg_id = request.form.get("registration_id","").strip()
    full_name = request.form.get("full_name","").strip()
    email = request.form.get("official_email","").strip().lower()
    files = request.files.getlist("images")
    if len(files) < 5:
        flash("Upload at least 5 images.", "danger")
        return redirect(url_for("admin.student_new_get"))
    db: Session = next(get_db())
    if db.query(Student).filter(Student.registration_id == reg_id).first():
        flash("Registration ID already exists.", "warning")
        return redirect(url_for("admin.student_new_get"))
    s = Student(registration_id=reg_id, official_email=email, active=True)
    db.add(s); db.flush()
    student_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], reg_id)
    os.makedirs(student_dir, exist_ok=True)
    encs = []
    for idx, f in enumerate(files):
        filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{idx}.jpg"
        path = os.path.join(student_dir, filename)
        f.save(path)
        img = face_recognition.load_image_file(path)
        boxes = face_recognition.face_locations(img, model=current_app.config["RECOG_MODEL"])
        if len(boxes) != 1:
            db.rollback()
            flash(f"Image {filename}: must have exactly one clear face.", "danger")
            return redirect(url_for("admin.student_new_get"))
        enc = face_recognition.face_encodings(img, boxes)[0]
        encs.append(enc)
        db.add(FaceEncoding(student_id=s.id, encoding_vector=enc.astype(np.float64).tobytes(), image_path=path, is_average=False))
    avg = np.mean(np.vstack(encs), axis=0).astype(np.float64)
    avg_path = os.path.join(current_app.config["ENCODING_FOLDER"], f"{reg_id}_avg.npy")
    np.save(avg_path, avg)
    db.add(FaceEncoding(student_id=s.id, encoding_vector=avg.tobytes(), image_path=avg_path, is_average=True))
    db.add(AuditLog(user_id=session.get("uid"), action="student_create", ip_address=request.remote_addr, user_agent=request.headers.get("User-Agent",""), meta=json.dumps({"registration_id": reg_id, "full_name": full_name})))
    db.commit()
    flash("Student and encodings saved.", "success")
    return redirect(url_for("admin.students_list"))
@admin_bp.get("/attendance")
def attendance_view():
    if not require_admin(): return redirect(url_for("auth.login_get"))
    db: Session = next(get_db())
    today = date.today()
    rows = db.query(Attendance).filter(Attendance.date == today).all()
    return render_template("admin/attendance.html", rows=rows)
@admin_bp.get("/reports/export")
def export_csv():
    if not require_admin(): return redirect(url_for("auth.login_get"))
    db: Session = next(get_db())
    rows = db.query(Attendance).all()
    data = [{
        "registration_id": a.student.registration_id,
        "date": a.date.isoformat(),
        "time_in": a.time_in.isoformat() if a.time_in else "",
        "course_code": a.course_code,
        "camera_id": a.camera_id,
        "status": a.status
    } for a in rows]
    df = DataFrame(data)
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return send_file(io.BytesIO(buf.getvalue().encode("utf-8")), as_attachment=True, download_name="attendance.csv", mimetype="text/csv")
