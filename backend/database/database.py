from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mtg_tournament.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def init_admin_user():
    """Initialize or update admin user with password from environment."""
    from models import AdminConfig
    from services.auth import get_password_hash
    
    db = SessionLocal()
    try:
        default_password = os.getenv("ADMIN_PASSWORD", "admin")
        password_hash = get_password_hash(default_password)
        
        admin = db.query(AdminConfig).filter(AdminConfig.id == 1).first()
        
        if not admin:
            admin = AdminConfig(
                id=1,
                password_hash=password_hash
            )
            db.add(admin)
            db.commit()
            print(f"Admin user created with password from ADMIN_PASSWORD env var")
        else:
            # Always update password to match environment variable
            admin.password_hash = password_hash
            db.commit()
            print(f"Admin password updated from ADMIN_PASSWORD env var")
    finally:
        db.close()
