from . import login_b

import os
import datetime
import time
#import app
from flask import current_app as app
from flask import Flask, render_template, session, redirect, url_for, request, flash, send_from_directory, jsonify
#from lasha import app
from app import db, thumbnail, mail_manager, rbac_manager, cus_error
from flask_login import current_user, login_user, logout_user, login_required
from app.custom_functions import calc_file_hash, calc_string_hash
from app.models import User, Video, Role, Comment, LikedBy
from app.forms import RegistrationForm, FileuploadForm, LoginForm, AccountForm, UserAlterForm, CommentForm, RoleForm, VideoEditForm, SearchForm
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from pyee import EventEmitter
from flask_mail import Message
#from raven.contrib.flask import Sentry

@login_b.route('/login', methods=['GET', 'POST'])
@rbac_manager.exempt
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user_main.index'))
    form = LoginForm()
    custom_content = {'title': 'Sign In', 'update': None, 'error' : None, 'logincheck' : url_for('login_b.logincheck')}
    return render_template('login_b.login.html', form=form, custom_content=custom_content)

@login_b.route('/logincheck', methods=['POST'])
@rbac_manager.exempt
def logincheck():
    form = LoginForm()
    errors = []
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            errors.append('Invalid username or password')
        elif not user.is_active():
            errors.append('Inactive User')
        else:
            login_user(user)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('user_main.index')
            return jsonify(data={'su_re': next_page})
    for fieldName, errorMessages in form.errors.items():
        for err in errorMessages:
            errors.append(err)
    return jsonify(data={'errors': errors})

@login_b.route('/logout')
@rbac_manager.exempt
def logout():
    logout_user()
    return redirect(url_for('login_b.login'))
