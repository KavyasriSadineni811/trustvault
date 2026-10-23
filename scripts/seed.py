

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app import create_app
from app.extensions import db
from app.models import User

app = create_app()

with app.app_context():
    db.create_all()

    owner_email = "owner@trustvault.local"
    owner = db.session.scalar(
        db.select(User).where(User.email == owner_email)
    )

    if owner is None:
        owner = User(
            name="TrustVault Owner",
            email=owner_email,
            role="owner",
            is_active=True,
        )
        owner.set_password("Owner@12345")
        db.session.add(owner)
        db.session.commit()
        print("Owner account created successfully.")
    else:
        print("Owner account already exists. No changes made.")

    print("Database tables created successfully.")

