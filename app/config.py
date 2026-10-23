import os

from dotenv import load_dotenv


load_dotenv()


class Config:

    # ============================================================
    # SECURITY
    # ============================================================

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "development-only-secret"
    )

    # ============================================================
    # DATABASE
    # ============================================================

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///trustvault.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ============================================================
    # FILE UPLOAD SETTINGS
    # ============================================================

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    ALLOWED_EXTENSIONS = {
        "pdf",
        "txt",
        "doc",
        "docx",
        "png",
        "jpg",
        "jpeg",
    }