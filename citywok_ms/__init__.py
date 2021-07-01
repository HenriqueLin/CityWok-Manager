import logging
import os
from logging.handlers import RotatingFileHandler

import flask_babel
import sentry_sdk
from config import Config
from flask import Flask, current_app, request
from flask.logging import default_handler
from flask_admin import Admin
from flask_babel import Babel
from flask_login import LoginManager, current_user
from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment
from flask_principal import Principal, RoleNeed, UserNeed, identity_loaded
from flask_rq2 import RQ
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sentry_sdk.integrations.flask import FlaskIntegration
from sqlalchemy import MetaData
from sqlalchemy_utils import i18n

from citywok_ms.utils.admin import MyAdminIndexView
from citywok_ms.utils.logging import formatter

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=convention)

csrf = CSRFProtect()
db = SQLAlchemy(metadata=metadata)
babel = Babel()
moment = Moment()
login = LoginManager()
principal = Principal()
mail = Mail()
migrate = Migrate()
f_admin = Admin(template_mode="bootstrap4", index_view=MyAdminIndexView())
rq = RQ()


def create_app(config_class=Config):
    # create the app instance
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    i18n.get_locale = flask_babel.get_locale

    # init extensions
    db.init_app(app)
    csrf.init_app(app)
    babel.init_app(app)
    moment.init_app(app)
    login.init_app(app)
    principal.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    rq.init_app(app)
    f_admin.init_app(app)

    if not app.testing and not app.debug:  # test: no cover
        sentry_sdk.init(
            dsn=app.config["SENTRY_DNS"],
            integrations=[FlaskIntegration()],
            traces_sample_rate=app.config["SENTRY_RATE"],
            environment="production",
        )

    with app.app_context():
        # imports
        from citywok_ms.admin.routes import admin_bp
        from citywok_ms.auth.routes import auth_bp
        from citywok_ms.cli import command_bp
        from citywok_ms.employee.routes import employee_bp
        from citywok_ms.error.handlers import error_bp
        from citywok_ms.file.routes import file_bp
        from citywok_ms.main.routes import main_bp
        from citywok_ms.supplier.routes import supplier_bp
        from citywok_ms.movement.order.routes import order_bp

        # blueprints
        app.register_blueprint(auth_bp)
        app.register_blueprint(employee_bp)
        app.register_blueprint(supplier_bp)
        app.register_blueprint(file_bp)
        app.register_blueprint(command_bp)
        app.register_blueprint(main_bp)
        app.register_blueprint(error_bp)
        app.register_blueprint(admin_bp)
        app.register_blueprint(order_bp)

        app.logger.removeHandler(default_handler)
        if not app.testing:  # test: no cover
            if app.debug:
                log = logging.getLogger("werkzeug")
                log.setLevel(logging.ERROR)

                stream_handler = logging.StreamHandler()
                stream_handler.setFormatter(formatter)
                stream_handler.setLevel(logging.INFO)
                app.logger.addHandler(stream_handler)
            else:
                app.logger.setLevel(logging.INFO)
                os.makedirs("logs", exist_ok=True)
                file_handler = RotatingFileHandler(
                    "logs/citywok_ms.log", maxBytes=5 * 1024 * 1024, backupCount=10
                )
                file_handler.setFormatter(formatter)
                file_handler.setLevel(logging.INFO)
                app.logger.addHandler(file_handler)

        app.logger.info("citywok_ms startup")

        @identity_loaded.connect_via(app)
        def on_identity_loaded(sender, identity):
            # Set the identity user object
            identity.user = current_user

            # Add the UserNeed to the identity, this may not be used
            if hasattr(current_user, "id"):
                identity.provides.add(UserNeed(current_user.id))

            # Update the identity with the roles that the user provides
            if hasattr(current_user, "role"):
                identity.provides.add(RoleNeed(current_user.role))

        @app.shell_context_processor
        def make_shell_context():
            from citywok_ms.employee.models import Employee
            from citywok_ms.file.models import EmployeeFile, File, SupplierFile
            from citywok_ms.supplier.models import Supplier

            return {
                "app": app,
                "db": db,
                "Employee": Employee,
                "Supplier": Supplier,
                "File": File,
                "EmployeeFile": EmployeeFile,
                "SupplierFile": SupplierFile,
            }

        return app


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config["LANGUAGES"])
