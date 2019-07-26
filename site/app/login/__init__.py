from flask import Blueprint

login_b = Blueprint('login_b', __name__, template_folder='templates', static_folder='static', static_url_path='/login/static')

from . import views
