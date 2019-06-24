from flask import Blueprint

login_b = Blueprint('login_b', __name__, template_folder='templates')

from . import views
