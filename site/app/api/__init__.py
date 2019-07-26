from flask import Blueprint

api_r = Blueprint('api_r', __name__,  template_folder='templates', static_folder='static', static_url_path='/api/static')

from . import views
