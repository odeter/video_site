import sys
import os

# third-party imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_mail import Mail
from flask_login import LoginManager

# local imports
from config import app_config
from .flask_rbac import RBAC
import jinja2

# db variable initialization
db = SQLAlchemy()

# after the db variable initialization
login_manager = LoginManager()
rbac_manager = RBAC()
mail_manager = Mail()

class MyApp(Flask):
    def __init__(self, st_path):
        Flask.__init__(self, __name__, instance_relative_config=True, static_url_path=st_path)
        self.jinja_loader = jinja2.ChoiceLoader([
            self.jinja_loader,
            jinja2.PrefixLoader({}, delimiter = ".")
        ])
    def create_global_jinja_loader(self):
        return self.jinja_loader

    def register_blueprint(self, bp):
        Flask.register_blueprint(self, bp)
        self.jinja_loader.loaders[1].mapping[bp.name] = bp.jinja_loader

def create_app(config_name, st_path, login_view):
    app = MyApp(st_path)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    db.init_app(app)

    # initiate packages
    migrate = Migrate(app, db)
    rbac_manager.init_app(app)
    mail_manager.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = login_view

    # get blueprints
    # from .admin import admin as admin_blueprint
    from .user import user_main as user_blueprint
    from .api import api_r as api_blueprint
    from .login import login_b as login_blueprint
    from .error_pages import error_pages as error_blueprint
    from .admin import admin as admin_blueprint

    # app.register_blueprint(admin_blueprint)
    app.register_blueprint(api_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(login_blueprint)
    app.register_blueprint(error_blueprint)
    app.register_blueprint(admin_blueprint)

    # add permission for all to go to blueprint static folder
    rbac_manager.add_bp_static(app, login_blueprint)
    rbac_manager.add_bp_static(app, error_blueprint)

    return app
