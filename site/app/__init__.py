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

# db variable initialization
db = SQLAlchemy()

# after the db variable initialization
login_manager = LoginManager()
rbac_manager = RBAC()
mail_manager = Mail()

def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True, static_url_path='/pub_static')
    app.config.from_object(app_config[config_name])


    app.config.from_pyfile('config.py')
    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'login'
    migrate = Migrate(app, db)
    rbac_manager.init_app(app)
    mail_manager.init_app(app)
    from app import models
    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)
    from .error_pages import error_pages as error_blueprint
    app.register_blueprint(error_blueprint)
    # from .login import login_b as login_blueprint
    # app.register_blueprint(login_blueprint)

    return app
