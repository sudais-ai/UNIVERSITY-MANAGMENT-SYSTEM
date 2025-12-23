from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
Base = declarative_base()
_engine = None
_SessionLocal = None
def init_engine(uri):
    global _engine, _SessionLocal
    _engine = create_engine(uri, pool_pre_ping=True, future=True)
    _SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False, future=True)
def get_db():
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()
