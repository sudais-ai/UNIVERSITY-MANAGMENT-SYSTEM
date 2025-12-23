from flask import render_template, request, redirect, url_for, flash, session
from sqlalchemy.orm import Session
from attendance_core.db import get_db
from attendance_core.models import User, AuditLog
from attendance_core.security import hash_password, verify_password, create_session
from attendance_core.validators import is_valid_university_email, strong_password
from . import auth_bp
@auth_bp.get("/login")
def login_get():
    return render_template("auth/login.html")
@auth_bp.post("/login")
def login_post():
    email = request.form.get("email","").strip().lower()
    password = request.form.get("password","")
    db: Session = next(get_db())
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        flash("Invalid credentials", "danger")
        return redirect(url_for("auth.login_get"))
    create_session(user.id, user.role)
    db.add(AuditLog(user_id=user.id, action="login", ip_address=request.remote_addr, user_agent=request.headers.get("User-Agent","")))
    db.commit()
    return redirect(url_for("admin.dashboard" if user.role == "admin" else "student.dashboard"))
@auth_bp.get("/register")
def register_get():
    return render_template("auth/register.html")
@auth_bp.post("/register")
def register_post():
    full_name = request.form.get("full_name","").strip()
    email = request.form.get("email","").strip().lower()
    password = request.form.get("password","")
    if not is_valid_university_email(email) or not strong_password(password):
        flash("Use valid university email and strong password.", "danger")
        return redirect(url_for("auth.register_get"))
    db: Session = next(get_db())
    if db.query(User).filter(User.email == email).first():
        flash("Email already registered.", "warning")
        return redirect(url_for("auth.register_get"))
    u = User(full_name=full_name, email=email, password_hash=hash_password(password), role="student")
    db.add(u)
    db.add(AuditLog(user_id=None, action="register", ip_address=request.remote_addr, user_agent=request.headers.get("User-Agent","")))
    db.commit()
    flash("Registration successful. Please login.", "success")
    return redirect(url_for("auth.login_get"))
@auth_bp.get("/logout")
def logout():
    uid = session.get("uid")
    db: Session = next(get_db())
    db.add(AuditLog(user_id=uid, action="logout", ip_address=request.remote_addr, user_agent=request.headers.get("User-Agent","")))
    db.commit()
    session.clear()
    return redirect(url_for("auth.login_get"))
