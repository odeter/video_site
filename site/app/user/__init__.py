from flask import Blueprint

user_main = Blueprint('user_main', __name__,  template_folder='templates', static_folder='static', static_url_path='/user_main/static')

from . import views
