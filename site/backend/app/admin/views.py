from . import admin

import os
import datetime
import time
#import app
from flask import current_app as app, Flask, render_template, session, redirect, url_for, request, flash, send_from_directory, jsonify
#from lasha import app
from app import thumbnail, mail_manager, rbac_manager, cus_error
from flask_login import current_user
from app.custom_functions import make_navigation
from app.models import db, User, Video, Role, Comment, LikedBy
from app.forms import RegistrationForm, UserAlterForm, RoleForm
from flask_mail import Message
#from raven.contrib.flask import Sentry

@admin.route('/register', methods=['GET', 'POST'])
@rbac_manager.allow(['admin'], methods=['GET', 'POST'])
def register():
    nav = make_navigation(current_user)
    logoinf = app.config['LOGO_INFO']
    right_bar = app.config['RIGHT_BAR']
    form = RegistrationForm()
    custom_content = {'title': 'New User', 'active_page': 'reg',
                      'page_headT': "Register", 'update': None}
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data,
                    about_me=form.about_me.data)
        user.set_password(form.password.data)
        user.add_role(Role.get_by_name(form.roles.data))
        db.session.add(user)
        db.session.commit()
        custom_content['update'] = ['Congratulations, you created a new user!', 'success']
    return render_template('admin.register.html', logoinf=logoinf, form=form,
                           navigation_bar=nav, right_bar=right_bar,
                           custom_content=custom_content)

@admin.route('/add_Role', methods=['GET', 'POST'])
@rbac_manager.allow(['admin'], methods=['GET', 'POST'])
def add_roles():
    nav = make_navigation(current_user)
    logoinf = app.config['LOGO_INFO']
    right_bar = app.config['RIGHT_BAR']
    form = RoleForm()
    custom_content = {'title': 'New Role', 'active_page': 'role',
                      'page_headT': "Role register", 'update': None}
    if form.validate_on_submit():
        nrole = Role(name=form.role_name.data)
        if(form.parent_name.data):
            nrole.add_parent(Role.get_by_name(form.parent_name.data))
        db.session.add(nrole)
        db.session.commit()
        custom_content['update'] = ['Congratulations, you created a new role!', 'success']
    return render_template('admin.role_register.html', logoinf=logoinf, form=form,
                           navigation_bar=nav, right_bar=right_bar,
                           custom_content=custom_content)

@admin.route('/roles', methods=['GET', 'POST'])
@rbac_manager.allow(['admin'], methods=['GET', 'POST'])
def role_administration():
    nav = make_navigation(current_user)
    logoinf = app.config['LOGO_INFO']
    right_bar = app.config['RIGHT_BAR']
    custom_content = {'title': 'Roles', 'active_page': 'role',
                      'page_headT': "Role List", 'update': None,
                      'role_list_head': None, 'role_list': None, 'add_role_link' : "/add_Role"}
    #print(Role.get_all_roles())
    roles = Role.query.all()
    role_list_head = ['ID', 'Name', 'Parent List']
    role_list = []
    for role in roles:
        role_list.append([role.id, role.name, ','.join(role.get_parents_list())])
    custom_content['role_list_head'] = role_list_head
    custom_content['role_list'] = role_list
    return render_template('admin.role_ad.html', logoinf=logoinf,
                           navigation_bar=nav, right_bar=right_bar,
                           custom_content=custom_content)

@admin.route('/users', methods=['GET', 'POST'])
@rbac_manager.allow(['admin'], methods=['GET', 'POST'])
def user_administration():
    nav = make_navigation(current_user)
    logoinf = app.config['LOGO_INFO']
    right_bar = app.config['RIGHT_BAR']
    custom_content = {'title': 'User Administration', 'active_page': 'users',
                      'page_headT': "User List", 'update': None,
                      'user_list_head': None, 'user_list': None}
    users = User.query.all()
    user_list_head = ['ID', 'User Name', 'Email', 'Active', 'Creation Date']
    user_list = []
    for user in users:
        user_list.append([url_for('admin.user_edit', id_u=user.id),
                          [user.id, user.username, user.email, user.active, user.create_date ]])
    custom_content['user_list_head'] = user_list_head
    custom_content['user_list'] = user_list
    return render_template('admin.user_list.html', logoinf=logoinf,
                           navigation_bar=nav, right_bar=right_bar,
                           custom_content=custom_content)

@admin.route('/useredit/<id_u>', methods=['GET', 'POST'])
@rbac_manager.allow(['admin'], methods=['GET', 'POST'])
def user_edit(id_u):
    nav = make_navigation(current_user)
    logoinf = app.config['LOGO_INFO']
    right_bar = app.config['RIGHT_BAR']
    edit_user = User.get_by_id(id_u)
    form = UserAlterForm()
    form.set_user(edit_user)
    custom_content = {'title': 'Account Settings', 'active_page': 'users',
                      'page_headT': "Information", 'update': None}
    if form.validate_on_submit():
        edit_user.username = form.username.data
        edit_user.about_me = form.about_me.data
        edit_user.active = form.active.data
        if edit_user.email != form.email.data:
            edit_user.email = form.email.data
        if form.password.data:
            edit_user.set_password(form.password.data)
        edit_user.set_role_single(Role.get_by_name(form.roles.data))
        db.session.commit()
        custom_content['update'] = ['Congratulations, you updated '+ form.username.data +' information!', 'success']
    elif request.method == 'GET':
        form.username.data = edit_user.username
        form.email.data = edit_user.email
        form.active.data = edit_user.active
        form.about_me.data = edit_user.about_me
        form.roles.data = edit_user.get_first_role()
        print(edit_user.get_first_role())
    return render_template('admin.edit_user.html', logoinf=logoinf, right_bar=right_bar, form=form,
                           navigation_bar=nav, custom_content=custom_content)
