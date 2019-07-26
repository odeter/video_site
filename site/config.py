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
    #ADMIN_FOLDER = os.path.join(basedir, 'app/main_static')
    USER_STATIC = os.path.join(basedir, 'app/user/static')
    CONTENT_FOLDER = os.path.join(basedir, 'app/content')
    #STATIC_FOLDER = os.path.join(basedir, 'app/pub_static')
    RBAC_USE_WHITE = True
    LOGO_INFO = {'title': 'Lasha', 'logo_href':'/index', 'copyright' : 'Lasha'}
    NAVIGATION_BAR = [['/index', 'home', 'Home', 'pe-7s-home'],
	              ['/upload', 'upload', 'Upload', 'pe-7s-upload'],
                      ['/gallery', 'gallery', 'Gallery', 'pe-7s-photo-gallery']]
    NAVIGATION_BAR_ADMIN = [['/register', 'reg', 'New Users', 'pe-7s-add-user'],
                            ['/roles', 'role', 'Roles', 'pe-7s-science'],
                            ['/users', 'users', 'User List', 'pe-7s-users']]
    RIGHT_BAR = [['/account', 'fa fa-user-circle'], ['/settings', 'fa fa-cog'], ['/logout', 'fa fa-sign-out-alt']]

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
