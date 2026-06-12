"""Idempotent seed script for development.

Creates the default pustakawan account if it does not exist.
Safe to run multiple times.

Usage: python -m app.seed
"""

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.enums import PeranPengguna
from app.models.pengguna import Pengguna

PUSTAKAWAN_EMAIL = "pustakawan@biblio.ac.id"
PUSTAKAWAN_PASSWORD = "admin1234"
PUSTAKAWAN_NAMA = "Admin Perpustakaan"


def run() -> None:
    db = SessionLocal()
    try:
        existing = (
            db.query(Pengguna)
            .filter(Pengguna.email == PUSTAKAWAN_EMAIL)
            .first()
        )

        if existing:
            print(
                f"Seed: pustakawan {PUSTAKAWAN_EMAIL} already exists, skipping."
            )
            return

        pustakawan = Pengguna(
            nama=PUSTAKAWAN_NAMA,
            email=PUSTAKAWAN_EMAIL,
            kata_sandi=hash_password(PUSTAKAWAN_PASSWORD),
            peran=PeranPengguna.pustakawan,
        )
        db.add(pustakawan)
        db.commit()
        print(f"Seed: created pustakawan {PUSTAKAWAN_EMAIL}.")
    except Exception as exc:
        db.rollback()
        print(f"Seed error: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
