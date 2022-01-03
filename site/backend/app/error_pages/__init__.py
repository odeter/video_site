from flask import Blueprint

error_pages = Blueprint('error_pages', __name__, template_folder='templates', static_folder='static', static_url_path='/error_pages/static')

from . import views
