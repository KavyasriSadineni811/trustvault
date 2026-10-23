from app import create_app
from app.extensions import db
from app.models import User


app = create_app()

with app.app_context():

    db.create_all()

    # ============================================================
    # OWNER
    # ============================================================

    owner_email = "owner@trustvault.local"
    owner_password = "owner123"

    owner = db.session.scalar(
        db.select(User).where(
            User.email == owner_email
        )
    )

    if owner is None:

        owner = User(
            name="TrustVault Owner",
            email=owner_email,
            role="owner",
            is_active=True
        )

        owner.set_password(owner_password)

        db.session.add(owner)

        print("Owner account created.")

    else:

        owner.name = "TrustVault Owner"
        owner.role = "owner"
        owner.is_active = True
        owner.set_password(owner_password)

        print("Owner account already exists.")
        print("Owner password reset.")

    # ============================================================
    # RECIPIENT
    # ============================================================

    recipient_email = "recipient@trustvault.local"
    recipient_password = "recipient123"

    recipient = db.session.scalar(
        db.select(User).where(
            User.email == recipient_email
        )
    )

    if recipient is None:

        recipient = User(
            name="TrustVault Recipient",
            email=recipient_email,
            role="viewer",
            is_active=True
        )

        recipient.set_password(recipient_password)

        db.session.add(recipient)

        print("Recipient account created.")

    else:

        recipient.name = "TrustVault Recipient"
        recipient.role = "viewer"
        recipient.is_active = True
        recipient.set_password(recipient_password)

        print("Recipient account already exists.")
        print("Recipient password reset.")

    # ============================================================
    # ADMIN
    # ============================================================

    admin_email = "admin@trustvault.local"
    admin_password = "admin123"

    admin = db.session.scalar(
        db.select(User).where(
            User.email == admin_email
        )
    )

    if admin is None:

        admin = User(
            name="TrustVault Admin",
            email=admin_email,
            role="admin",
            is_active=True
        )

        admin.set_password(admin_password)

        db.session.add(admin)

        print("Admin account created.")

    else:

        admin.name = "TrustVault Admin"
        admin.role = "admin"
        admin.is_active = True
        admin.set_password(admin_password)

        print("Admin account already exists.")
        print("Admin password reset.")

    # ============================================================
    # SAVE
    # ============================================================

    db.session.commit()

    print()
    print("==============================================")
    print("       TRUSTVAULT ACCOUNTS READY")
    print("==============================================")

    print()
    print("OWNER ACCOUNT")
    print("----------------------------------------------")
    print("Name     :", owner.name)
    print("Email    :", owner.email)
    print("Password :", owner_password)

    print()
    print("RECIPIENT ACCOUNT")
    print("----------------------------------------------")
    print("Name     :", recipient.name)
    print("Email    :", recipient.email)
    print("Password :", recipient_password)

    print()
    print("ADMIN ACCOUNT")
    print("----------------------------------------------")
    print("Name     :", admin.name)
    print("Email    :", admin.email)
    print("Password :", admin_password)

    print()
    print("==============================================")