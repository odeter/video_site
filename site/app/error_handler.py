from flask import current_app as app
#import app.error_pages as dd
from app.error_pages.views import page_not_permitted, page_not_found

@app.errorhandler(403)
def ep403(e):
    return page_not_permitted(e)

@app.errorhandler(404)
def e404(e):
    return page_not_found(e)
