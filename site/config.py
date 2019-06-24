import os
from werkzeug.utils import secure_filename

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    #SECRET_KEY = os.environ.get('SECRET_KEY') or 'lkjh21DSAFK6JLs'
    SENTRY_DSN = ""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEFAULT_PROFILE_PIC = "default-avatar.png"
    SUB_COMMENT_MAX_DEPTH = 5
    NUM_OF_VID_SCROLL = 12
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    #     'sqlite:///' + os.path.join(basedir, 'app/app.db')
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 56 * 1024 * 1024
    ADMIN_FOLDER = os.path.join(basedir, 'app/main_static')
    CONTENT_FOLDER = os.path.join(basedir, 'app/content')
    STATIC_FOLDER = os.path.join(basedir, 'app/pub_static')
    RBAC_USE_WHITE = True

class DevelopmentConfig(Config):
    """
    Development configurations
    """

    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """
    Production configurations
    """

    DEBUG = False

app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
