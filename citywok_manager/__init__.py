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
login_manager.login_view = 'user.login'
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
        from citywok_manager.user.routes import user
        from citywok_manager.employee.routes import employee
        from citywok_manager.main.routes import main
        from citywok_manager.supplier.routes import supplier
        from citywok_manager.registry.routes import registry

        # blueprints
        app.register_blueprint(user)
        app.register_blueprint(employee)
        app.register_blueprint(main)
        app.register_blueprint(supplier)
        app.register_blueprint(registry)

        # create_database

        return app
