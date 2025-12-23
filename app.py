from flask import Flask
from config import Config
from attendance_core.db import init_engine, Base
from attendance_core import db as dbmod
from web.auth import auth_bp
from web.admin import admin_bp
from web.student import student_bp
from web.api import api_bp
import os
def create_app():
    app = Flask(__name__, instance_relative_config=True, static_folder="static", template_folder="templates")
    app.config.from_object(Config)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["ENCODING_FOLDER"], exist_ok=True)
    init_engine(app.config["SQLALCHEMY_DATABASE_URI"])
    Base.metadata.create_all(bind=dbmod._engine)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(student_bp, url_prefix="/student")
    app.register_blueprint(api_bp, url_prefix="/api")
    @app.after_request
    def set_headers(r):
        r.headers["X-Content-Type-Options"] = "nosniff"
        r.headers["X-Frame-Options"] = "SAMEORIGIN"
        r.headers["X-XSS-Protection"] = "1; mode=block"
        return r
    return app
app = create_app()
