from sqlalchemy.orm import Session

from .auth import get_password_hash
from .database import SessionLocal
from .init_db import init_database
from .models import User


ADMIN_EMAIL = "administrador@gmail.com"
ADMIN_PASSWORD = "marymar123"
ADMIN_USERNAME = "Administrador"


def seed_admin() -> None:
    init_database()
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.email == ADMIN_EMAIL).first()
        if user is None:
            user = User(
                email=ADMIN_EMAIL,
                username=ADMIN_USERNAME,
                password_hash=get_password_hash(ADMIN_PASSWORD),
                is_admin=True,
            )
            db.add(user)
        else:
            user.username = ADMIN_USERNAME
            user.password_hash = get_password_hash(ADMIN_PASSWORD)
            user.is_admin = True
        db.commit()
        print(f"Admin ready: {ADMIN_EMAIL}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()
