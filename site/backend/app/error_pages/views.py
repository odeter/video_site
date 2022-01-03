from . import error_pages
from flask import current_app as app
from flask import render_template, redirect, url_for
from flask_login import current_user
from app.models import db

def problems(custom_content, title, description, nav, logoinf, right_bar):
    custom_content['title'] = title
    custom_content['page_headT'] = description
    return render_template('error_pages.msg_page.html', logoinf=logoinf, right_bar=right_bar,
                           navigation_bar=nav, custom_content=custom_content)

def page_not_permitted(e):
    if current_user.is_authenticated:
        err = '403 - Access not permitted'
        err_disp = ('The following page is forbidden. '
                    'Beware yee who threads beyond the laws of admin.')
        return error(err, err_disp), 403
    else:
        return redirect(url_for('login_b.login'))

def page_not_found(e):
    err = '404 - Page not found'
    err_disp = ('The page you are looking for might '
                'have been removed or had its name '
                'changed or is temporarily unavailable.')
    return error(err, err_disp), 404

def error(err, err_disp):
    custom_content = {'error_title': err,
                      'error_description' : err_disp, 'link' : '/index'}
    return render_template('error_pages.error.html', custom_content=custom_content)
