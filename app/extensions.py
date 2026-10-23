from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect


# ============================================================
# DATABASE
# ============================================================

# expire_on_commit=False is important for the test environment
# and prevents ORM objects from losing their loaded attributes
# immediately after db.session.commit().
db = SQLAlchemy(
    session_options={
        "expire_on_commit": False
    }
)


# ============================================================
# FLASK-MIGRATE
# ============================================================

migrate = Migrate()


# ============================================================
# FLASK-LOGIN
# ============================================================

login_manager = LoginManager()


# ============================================================
# CSRF PROTECTION
# ============================================================

csrf = CSRFProtect()