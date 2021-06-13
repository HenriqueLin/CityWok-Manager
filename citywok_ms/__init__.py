from config import Config
import flask_babel
from flask import Flask, current_app, request
from flask_babel import Babel
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import i18n
from flask_wtf.csrf import CSRFProtect
from flask_moment import Moment
from flask_login import LoginManager
from flask_principal import Principal

import os

csrf = CSRFProtect()
db = SQLAlchemy()
babel = Babel()
moment = Moment()
login = LoginManager()
principal = Principal()


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

    with app.app_context():
        # imports
        from citywok_ms.auth.routes import auth
        from citywok_ms.employee.routes import employee
        from citywok_ms.supplier.routes import supplier
        from citywok_ms.file.routes import file
        from citywok_ms.cli import command

        # blueprints
        app.register_blueprint(auth)
        app.register_blueprint(employee)
        app.register_blueprint(supplier)
        app.register_blueprint(file)
        app.register_blueprint(command)

        @app.shell_context_processor
        def make_shell_context():
            from citywok_ms.employee.models import Employee
            from citywok_ms.supplier.models import Supplier
            from citywok_ms.file.models import File, EmployeeFile, SupplierFile

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
