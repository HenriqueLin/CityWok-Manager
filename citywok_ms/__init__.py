import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

import flask_babel
from config import Config
from flask import Flask, current_app, request
from flask.logging import default_handler
from flask_babel import Babel
from flask_login import LoginManager, current_user
from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment
from flask_principal import Principal, RoleNeed, UserNeed, identity_loaded
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy_utils import i18n

csrf = CSRFProtect()
db = SQLAlchemy()
babel = Babel()
moment = Moment()
login = LoginManager()
principal = Principal()
mail = Mail()
migrate = Migrate()


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
    migrate.init_app(app, db)

    with app.app_context():
        # imports
        from citywok_ms.auth.routes import auth
        from citywok_ms.cli import command
        from citywok_ms.employee.routes import employee
        from citywok_ms.error.handlers import error
        from citywok_ms.file.routes import file
        from citywok_ms.main.routes import main
        from citywok_ms.supplier.routes import supplier

        # blueprints
        app.register_blueprint(auth)
        app.register_blueprint(employee)
        app.register_blueprint(supplier)
        app.register_blueprint(file)
        app.register_blueprint(command)
        app.register_blueprint(main)
        app.register_blueprint(error)

        app.logger.removeHandler(default_handler)
        if not app.testing:
            if app.debug:
                stream_handler = logging.StreamHandler()
                stream_handler.setFormatter(
                    logging.Formatter(
                        "%(levelname)s: %(message)s [%(pathname)s:%(lineno)d]"
                    )
                )
                stream_handler.setLevel(logging.INFO)
                app.logger.addHandler(stream_handler)
            else:
                Path("logs").mkdir(exist_ok=True)
                file_handler = RotatingFileHandler(
                    "logs/citywok_ms.log", maxBytes=20480, backupCount=10
                )
                file_handler.setFormatter(
                    logging.Formatter(
                        "%(asctime)s %(levelname)s: %(message)s "
                        "[%(pathname)s:%(lineno)d]"
                    )
                )
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
                identity.provides.add(RoleNeed(current_user.role.code))

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
