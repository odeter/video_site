from flask import Blueprint

error_pages = Blueprint('error_pages', __name__)

from . import views
