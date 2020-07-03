from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from citywok_manager.config import Config
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate

csrf = CSRFProtect()
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
migrate = Migrate()


def create_app(config_class=Config):
    # config the app
    app = Flask(__name__)
    app.config.from_object(config_class)

    # init extensions
    csrf.init_app(app)
    db.init_app(app)

    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        # imports
        from citywok_manager.users.routes import users
        from citywok_manager.employees.routes import employees
        from citywok_manager.main.routes import main
        from citywok_manager.suppliers.routes import suppliers

        # blueprints
        app.register_blueprint(users)
        app.register_blueprint(employees)
        app.register_blueprint(main)
        app.register_blueprint(suppliers)

        # create_database

        return app
