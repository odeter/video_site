import os
from os import environ, path
from werkzeug.utils import secure_filename

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'lkjh21DSAFK6JLs'
    SENTRY_DSN = ""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIN_STATIC_IMG = os.path.join(basedir, 'app/static')
    DEFAULT_PROFILE_PIC = "default-avatar.png"
    SUB_COMMENT_MAX_DEPTH = 5
    NUM_OF_VID_SCROLL = 12
    MAX_CONTENT_LENGTH = 56 * 1024 * 1024
    USER_STATIC = os.path.join(basedir, 'app/user/static')
    CONTENT_FOLDER = os.path.join(basedir, 'app/content')
    TEST_FOLDER = os.path.join(basedir, '../test_data')
    RBAC_USE_WHITE = True
    LOGO_INFO = {'title': 'Lasha', 'logo_href':'/index', 'copyright' : 'Lasha'}
    NAVIGATION_BAR = [['/index', 'home', 'Home', 'pe-7s-home'],
	              ['/upload', 'upload', 'Upload', 'pe-7s-upload'],
                      ['/gallery', 'gallery', 'Gallery', 'pe-7s-photo-gallery']]
    NAVIGATION_BAR_ADMIN = [['/register', 'reg', 'New Users', 'pe-7s-add-user'],
                            ['/roles', 'role', 'Roles', 'pe-7s-science'],
                            ['/users', 'users', 'User List', 'pe-7s-users']]
    RIGHT_BAR = [['/account', 'fa fa-user-circle'], ['/settings', 'fa fa-cog'], ['/logout', 'fa fa-sign-out-alt']]
    MAX_CONTENT_LENGTH=50000000

class DevelopmentConfig(Config):
    """
    Development configurations
    """

    FLASK_ENV = 'development'
    DEBUG = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')


class ProductionConfig(Config):
    """
    Production configurations
    """

    FLASK_ENV = 'production'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
