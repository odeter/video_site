from . import admin

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


def profile_pic(user):
    if not user.profile_pic:
        return app.config['DEFAULT_PROFILE_PIC']
    else:
        return user.profile_pic

def make_navigation(user):
    role_dict = user.get_role_dict()
    if 'admin' in role_dict:
        return (navigation_bar + navigation_bar_admin)
    return navigation_bar

def comment_sub(comments):
    done_comments = []
    for comment in comments:
        subcomments = None
        if comment.get_subcomments() is not None:
            subcomments = comment_sub(comment.get_subcomments())
        done_comments.append([comment.own_user.username, comment.content, comment.likes,
                              comment.dislikes, (comment.pub_date).strftime("%Y-%m-%d %H:%M:%S"),
                              url_for('admin.pro_pic', filename=profile_pic(comment.own_user)),
                              comment.respons_num, comment.id, comment.is_deleted, subcomments])
    return done_comments

def comments_to_list(comments):
    done_comments = []
    for comment in comments:
        subcomments = None
        if comment.depth_num == 0:
            if comment.get_subcomments() is not None:
                subcomments = comment_sub(comment.get_subcomments())
            done_comments.append([comment.own_user.username, comment.content, comment.likes,
                                  comment.dislikes, (comment.pub_date).strftime("%Y-%m-%d %H:%M:%S"),
                                  url_for('admin.pro_pic', filename=profile_pic(comment.own_user)),
                                  comment.respons_num, comment.id, comment.is_deleted, subcomments])
    return done_comments

logoinf = {'title': 'Lasha', 'logo_href':'/index', 'copyright' : 'Lasha'}


navigation_bar = [['/index', 'home', 'Home', 'pe-7s-home'],
	         ['/upload', 'upload', 'Upload', 'pe-7s-upload'],
	         ['/gallery', 'gallery', 'Gallery', 'pe-7s-photo-gallery']]

navigation_bar_admin = [['/register', 'reg', 'New Users', 'pe-7s-add-user'],
                        ['/roles', 'role', 'Roles', 'pe-7s-science'],
                        ['/users', 'users', 'User List', 'pe-7s-users']]

right_bar = [['/account', 'fa fa-user-circle'], ['/settings', 'fa fa-cog'], ['/logout', 'fa fa-sign-out-alt']]

# function to display minor error pages
def problems(custom_content, title, description, nav):
    custom_content['title'] = title
    custom_content['page_headT'] = description
    return render_template('msg_page.html', logoinf=logoinf, right_bar=right_bar,
                           navigation_bar=nav, custom_content=custom_content)

@admin.route('/')
@admin.route('/index')
@rbac_manager.allow(['common_user'], methods=['GET', 'POST'])
def index():
    nav = make_navigation(current_user)
    custom_content = {'title': 'Home', 'active_page': 'home',
                      'page_headT': "Dashboard", 'update': None}
    vid = Video.query.filter_by(is_deleted=False).order_by(Video.pub_date.desc()).all()
    video_info = []
    for nv in vid:
        print(nv.vid_hash)
        m_title = nv.title if (len(nv.title) < 10) else nv.title[:10] + "..."
        m_description = nv.description if (len(nv.description) < 15) else nv.description[:15] + "..."
        video_info.append([url_for('admin.play', fileh=nv.vid_of_id), m_title,
                           url_for('admin.img_pri', filename=nv.thumbpath), nv.pub_date, m_description])
    return render_template('home.html', video_info=video_info, logoinf=logoinf,
                           navigation_bar=nav, right_bar=right_bar,
                           custom_content=custom_content)

@admin.route('/login', methods=['GET', 'POST'])
@rbac_manager.exempt
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))
    form = LoginForm()
    custom_content = {'title': 'Sign In', 'update': None, 'error' : None, 'logincheck' : url_for('admin.logincheck')}
    return render_template('login.html', form=form, custom_content=custom_content)

@admin.route('/logincheck', methods=['POST'])
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
                next_page = url_for('admin.index')
            return jsonify(data={'su_re': next_page})
    for fieldName, errorMessages in form.errors.items():
        for err in errorMessages:
            errors.append(err)
    return jsonify(data={'errors': errors})

@admin.route('/logout')
@rbac_manager.exempt
def logout():
    logout_user()
    return redirect(url_for('admin.login'))

@admin.route('/settings', methods=['GET', 'POST'])
@rbac_manager.allow(['common_user'], methods=['GET', 'POST'])
def settings():
    nav = make_navigation(current_user)
    form = AccountForm()
    custom_content = {'title': 'Account Settings', 'active_page': '',
                      'page_headT': "Information", 'update': None,
                      'user_inf': [current_user.username, current_user.email,
                                   current_user.about_me,
                                   url_for('admin.pro_pic', filename=profile_pic(current_user)),
                                   url_for('admin.admin_s', filename="assets/img/avatar_back.jpg")],
                      'u_video_head' : [], 'u_videos' : [], 'u_com_head' : [], 'u_comment': []}

    custom_content['u_video_head'] = ['Thumbnail','Title', 'Creation Date', 'Likes', 'Dislikes']
    custom_content['u_com_head'] = ['Thumbnail', 'Video Title', 'Comment', 'Creation Date', 'Likes', 'Dislikes', 'Delete' ]

    u_videos = Video.query.filter_by(owner_id=current_user.id, is_deleted=False).order_by(Video.pub_date.desc())
    for vid in u_videos:
        (custom_content['u_videos']).append([url_for('admin.video_edit', id_v=vid.id),
                                             url_for('admin.img_pri', filename=vid.thumbpath),
                                             [vid.title, vid.pub_date, vid.likes, vid.dislikes]])

    u_comment = Comment.query.filter_by(user_id=current_user.id, is_deleted=False).order_by(Comment.pub_date.desc())
    for com in u_comment:
        vid = com.get_vid()
        vid_thumb = url_for('admin.img_pri', filename=vid.thumbpath) if vid.thumbpath else None
        content = com.content if (len(com.content) < 10) else com.content[:10] + "..."
        (custom_content['u_comment']).append([url_for('admin.play', fileh=vid.vid_of_id),
                                              vid_thumb, [vid.title, content, com.pub_date, com.likes, com.dislikes], com.id])

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        if current_user.email != form.email.data:
            current_user.email = form.email.data
        if form.password.data:
            current_user.set_password(form.password.data)
        f = form.pro_pic.data
        if f is not None:
            _, file_extension = os.path.splitext(f.filename)
            st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
            nfilename = st + file_extension
            filepath = os.path.join(app.config['CONTENT_FOLDER'], 'profile_pics', nfilename)
            f.save(filepath)
            os.remove(os.path.join(app.config['CONTENT_FOLDER'], 'profile_pics', old_filepath))
            current_user.profile_pic = nfilename
        db.session.commit()
        custom_content['user_inf'] = [current_user.username, current_user.email,
                                      current_user.about_me,
                                      url_for('admin.pro_pic', filename=profile_pic(current_user)),
                                      url_for('admin.admin_s', filename="assets/img/avatar_back.jpg")]
        custom_content['update'] = ['Congratulations, you updated your information!', 'success']
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.about_me.data = current_user.about_me
    return render_template('u_settings.html', logoinf=logoinf, right_bar=right_bar, form=form,
                           navigation_bar=nav, custom_content=custom_content)


@admin.route('/account', methods=['GET', 'POST'])
@rbac_manager.allow(['common_user'], methods=['GET', 'POST'])
def account():
    nav = make_navigation(current_user)
    form = AccountForm()
    custom_content = {'title': 'Account Settings', 'active_page': '',
                      'page_headT': "Information", 'update': None,
                      'user_inf': [current_user.username, current_user.email,
                                   current_user.about_me,
                                   url_for('admin.pro_pic', filename=profile_pic(current_user)),
                                   url_for('admin.admin_s', filename="assets/img/avatar_back.jpg")],
                      'u_video_head' : [], 'u_videos' : [], 'u_com_head' : [], 'u_comment': []}

    custom_content['u_video_head'] = ['Thumbnail','Title', 'Creation Date', 'Likes', 'Dislikes']
    custom_content['u_com_head'] = ['Thumbnail', 'Video Title', 'Comment', 'Creation Date', 'Likes', 'Dislikes', 'Delete' ]

    u_videos = Video.query.filter_by(owner_id=current_user.id, is_deleted=False).order_by(Video.pub_date.desc())
    for vid in u_videos:
        (custom_content['u_videos']).append([url_for('admin.video_edit', id_v=vid.id),
                                             url_for('admin.img_pri', filename=vid.thumbpath),
                                             [vid.title, vid.pub_date, vid.likes, vid.dislikes]])

    u_comment = Comment.query.filter_by(user_id=current_user.id, is_deleted=False).order_by(Comment.pub_date.desc())
    for com in u_comment:
        vid = com.get_vid()
        vid_thumb = url_for('admin.img_pri', filename=vid.thumbpath) if vid.thumbpath else None
        content = com.content if (len(com.content) < 10) else com.content[:10] + "..."
        (custom_content['u_comment']).append([url_for('admin.play', fileh=vid.vid_of_id),
                                              vid_thumb, [vid.title, content, com.pub_date, com.likes, com.dislikes], com.id])

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        if current_user.email != form.email.data:
            current_user.email = form.email.data
        if form.password.data:
            current_user.set_password(form.password.data)
        f = form.pro_pic.data
        if f is not None:
            _, file_extension = os.path.splitext(f.filename)
            st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
            nfilename = st + file_extension
            filepath = os.path.join(app.config['CONTENT_FOLDER'], 'profile_pics', nfilename)
            f.save(filepath)
            os.remove(os.path.join(app.config['CONTENT_FOLDER'], 'profile_pics', old_filepath))
            current_user.profile_pic = nfilename
        db.session.commit()
        custom_content['user_inf'] = [current_user.username, current_user.email,
                                      current_user.about_me,
                                      url_for('admin.pro_pic', filename=profile_pic(current_user)),
                                      url_for('admin.admin_s', filename="assets/img/avatar_back.jpg")]
        custom_content['update'] = ['Congratulations, you updated your information!', 'success']
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.about_me.data = current_user.about_me
    return render_template('u_settings.html', logoinf=logoinf, right_bar=right_bar, form=form,
                           navigation_bar=nav, custom_content=custom_content)

@admin.route('/upload', methods=['GET', 'POST'])
@rbac_manager.allow(['common_user'], methods=['GET', 'POST'])
def upload_file():
    nav = make_navigation(current_user)
    custom_content = {'title': 'Upload', 'active_page': 'upload',
                      'page_headT': "Video upload", 'update': None}
    form = FileuploadForm()
    if form.validate_on_submit():
        f = form.upFile.data
        f_hash = calc_file_hash(f)
        f.seek(0)
        vtitle = form.name.data
        vdescription = form.description.data
        filename, file_extension = os.path.splitext(f.filename)
        vid_of_t = calc_string_hash(datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S') + str(current_user.id))
        nfilename = vid_of_t + file_extension
        nthumbname = vid_of_t + ".png"
        filepath = os.path.join(app.config['CONTENT_FOLDER'], 'uploads', nfilename)
        thumbpath = os.path.join(app.config['CONTENT_FOLDER'], 'thumbnails', nthumbname)
        f.save(filepath)
        thumbnail.generate_thumbnail(filepath, thumbpath, 5)
        video = Video(filepath=nfilename, title=vtitle, description=vdescription, thumbpath=nthumbname, vid_hash=f_hash, vid_of_id=vid_of_t)
        current_user.add_video(video)
        #video.set_owner(current_user)
        db.session.add(video)
        db.session.commit()
        custom_content['update'] = ["File Saved!", 'success']
    return render_template('upload.html', form=form, logoinf=logoinf,
                           navigation_bar=nav, right_bar=right_bar,
                           custom_content=custom_content)

@admin.route('/gallery', methods=['GET', 'POST'])
@rbac_manager.allow(['common_user'], methods=['GET', 'POST'])
def gallery():
    nav = make_navigation(current_user)
    custom_content = {'title': 'Gallery', 'active_page': 'gallery',
                      'page_headT': "Video Gallery", 'update': None}
    video_info = []
    form = SearchForm()
    #vid = Video.query.filter_by(is_deleted=False).order_by(Video.pub_date.desc()).all()
    # if form.validate_on_submit():
    #     search_word = "%"+form.gal_search.data+"%"
    #     filter_word = form.gal_filter.data
    #     sort_word = form.gal_sort.data

    #     s_query = Video.query.filter_by(is_deleted=False).filter((Video.title.like(search_word)) |
    #                                                              (Video.description.like(search_word)))
    #     if filter_word == 'li' and sort_word == 'high':
    #         vid = s_query.order_by(Video.likes.desc()).all()
    #     elif filter_word == 'li' and sort_word == 'low':
    #         vid = s_query.order_by(Video.likes.asc()).all()
    #     elif filter_word == 'ct' and sort_word == 'high':
    #         vid = s_query.order_by(Video.pub_date.desc()).all()
    #     elif filter_word == 'ct' and sort_word == 'low':
    #         vid = s_query.order_by(Video.pub_date.asc()).all()
    max_load = app.config['NUM_OF_VID_SCROLL']
    vid = Video.query.filter_by(is_deleted=False).order_by(Video.pub_date.desc()).all()

    re_vid = vid if len(vid) < max_load else vid[:max_load]
    custom_content["last_id"] = len(re_vid)
    for nv in re_vid:
        #print(nv.vid_hash)
        m_title = nv.title if (len(nv.title) < 10) else nv.title[:10] + "..."
        m_description = nv.description if (len(nv.description) < 15) else nv.description[:15] + "..."
        video_info.append([url_for('admin.play', fileh=nv.vid_of_id), m_title,
                           url_for('admin.img_pri', filename=nv.thumbpath), nv.pub_date, m_description, nv.likes, nv.dislikes])
    return render_template('gallery.html', video_info=video_info, logoinf=logoinf,
                           navigation_bar=nav, right_bar=right_bar, form=form,
                           custom_content=custom_content)

@admin.route('/player/<fileh>', methods=['GET', 'POST'])
@rbac_manager.allow(['common_user'], methods=['GET', 'POST'])
def play(fileh):
    nav = make_navigation(current_user)
    form = CommentForm()
    vid = Video.query.filter_by(vid_of_id=fileh).first()
    custom_content = {'title': "Video Player", 'active_page': 'gallery',
                      'page_headT': "", 'update': None, 'comments': None}

    if (vid is not None):
        owner = vid.get_owner()
        video_info = {'deleted': False, 'pub_date' : vid.pub_date,
                          'owner' : owner.username, 'owner_pic' : url_for('admin.pro_pic', filename=profile_pic(owner)),
                          'id' : vid.id, 'likes' : vid.likes, 'dislikes' : vid.dislikes,
                          'like_procent' : (((vid.likes + vid.dislikes) / vid.likes) *100 if vid.likes else 101)}
        if (vid.is_deleted):
            custom_content['page_headT'] = "Deleted Video"
            video_info['video_url'] = ""
            video_info['title'] = "Deleted Video"
            video_info['description'] = "Video was deleted"
            video_info['video_thumb'] = ""
            video_info['deleted'] = True
            if form.validate_on_submit():
                custom_content['update'] = ["You can't comment on an deleted video", 'warning']
        else:
            custom_content['page_headT'] = vid.title
            video_info['video_url'] = url_for('admin.protected', filename=vid.filepath)
            video_info['title'] = vid.title
            video_info['description'] = vid.description
            video_info['video_thumb'] = url_for('admin.img_pri', filename=vid.thumbpath)
            if form.validate_on_submit():
                comment = Comment(content=form.comment.data)
                com_parent = Comment.query.filter_by(id=form.parent.data).first()
                if(form.parent.data == "" or com_parent.depth_num <= app.config['SUB_COMMENT_MAX_DEPTH']):
                    current_user.add_comment(comment)
                    vid.add_comment(comment)
                    if(form.parent.data != ""):
                        com_parent.add_subcomment(comment)
                        comment.add_depth(com_parent)
                    db.session.add(comment)
                    db.session.commit()
                    custom_content['update'] = ['Your comment was added!', 'success']
                else:
                    custom_content['update'] = ['Subcomments can only reach a depth of '+ str(app.config['SUB_COMMENT_MAX_DEPTH']), 'warning']

                form.comment.data = ""

        pre_comments = vid.get_comments()
        done_comments = comments_to_list(pre_comments)
        custom_content['comments'] = done_comments
        return render_template('play.html', video_info=video_info, logoinf=logoinf,
                               navigation_bar=nav, right_bar=right_bar, form=form,
                               custom_content=custom_content)
    else:
        return problems(custom_content, "Video not found", "Video can't be found.", nav)

@admin.route('/api', methods=['POST'])
@rbac_manager.allow(['common_user'], methods=['POST'])
def api():
    rec_data = request.get_json()
    ap_type = rec_data['c_type']
    accept_react = {"comment", "video"}
    if(ap_type == "react" and (rec_data['target'] in accept_react)):
        t_id = rec_data['target_id']
        like = rec_data['like']
        target = rec_data['target']
        try:
            reaction = LikedBy(liked=like)
            current_user.add_reaction(reaction)
            if(target == "comment"):
                react_tag = Comment.query.filter_by(id=t_id).first()
            elif(target == "video"):
                react_tag = Video.query.filter_by(id=t_id).first()
            owned_by = react_tag.own_name()
            react_tag.add_reaction(reaction, current_user.id)
            db.session.add(reaction)
            db.session.commit()
            if(like):
                data = {'update_msg' : ("You liked "+owned_by+"'s "+rec_data['target']),
                        'note_type': 'success', 'c_likes' : react_tag.likes,
                        'c_dislikes': react_tag.dislikes}
            else:
                data = {'update_msg' : ("You disliked "+owned_by+"'s "+rec_data['target']),
                        'note_type': 'success', 'c_likes' : react_tag.likes,
                        'c_dislikes': react_tag.dislikes}
            resp = jsonify(data)
            resp.status_code = 200
        except cus_error.Al_Exists:
            if(like):
                data = {'update_msg' : "You already liked "+owned_by+"'s "+rec_data['target'],
                        'note_type' : 'info'}
            else:
                data = {'update_msg' : "You already disliked "+owned_by+"'s "+rec_data['target'],
                        'note_type' : 'info'}
            resp = jsonify(data)
            resp.status_code = 200
        except cus_error.Al_Deleted:
            if(like):
                data = {'update_msg' : "You can't like an deleted video or comment",
                        'note_type' : 'info'}
            else:
                data = {'update_msg' :  "You can't dislike an deleted video or comment",
                        'note_type' : 'info'}
            resp = jsonify(data)
            resp.status_code = 200
    elif(ap_type == "del"):
        t_id = rec_data['target_id']
        target = rec_data['target']
        if(target == 'comment'):
            com = Comment.query.filter_by(id=t_id).first()
            try:
                com.remove_comment(current_user.id)
                db.session.commit()
                data = {'update_msg' : 'Comment deleted', 'note_type': 'success'}
            except cus_error.Al_Deleted:
                data = {'update_msg' : 'Comment already deleted', 'note_type': 'info'}
            except cus_error.Wrong_Own:
                data = {'update_msg' : 'Not owner of comment', 'note_type': 'danger'}
        else:
            data = {'update_msg' : 'Target not known', 'note_type': 'danger'}
        resp = jsonify(data)
        resp.status_code = 200
    elif(ap_type == "search"):
        target = rec_data['target']
        query = rec_data['query']
        sort_by = rec_data['sort_by']
        sort_desc = rec_data['sort_desc']

        first_id = rec_data['last_index']
        last_id = first_id + app.config['NUM_OF_VID_SCROLL']
        new_id = last_id

        if(target == 'video'):
            video_info = []
            search_word = "%"+query+"%"
            s_query = Video.query.filter_by(is_deleted=False).filter((Video.title.like(search_word)) |
                                                                 (Video.description.like(search_word)))
            if sort_by == 'li' and sort_desc:
                vid = s_query.order_by(Video.likes.desc()).all()
            elif sort_by == 'up' and sort_desc:
                vid = s_query.order_by(Video.pub_date.desc()).all()
            elif sort_by == 'up':
                vid = s_query.order_by(Video.pub_date).all()
            else:
                vid = s_query.order_by(Video.likes).all()

            end_of_s = False
            if len(vid) > last_id:
                vid = vid[first_id:last_id]
            else:
                new_id = len(vid)
                vid = [] if (len(vid) <= first_id) else vid[first_id:]
                end_of_s = True

            for nv in vid:
                m_title = nv.title if (len(nv.title) < 10) else nv.title[:10] + "..."
                m_description = nv.description if (len(nv.description) < 15) else nv.description[:15] + "..."
                video_info.append([url_for('admin.play', fileh=nv.vid_of_id), m_title,
                                   url_for('admin.img_pri', filename=nv.thumbpath), nv.pub_date, m_description, nv.likes, nv.dislikes])
            data = {'vid_search' : video_info, 'end': end_of_s, 'end_id': new_id}
        else:
            data = {'update_msg' : 'Target not known', 'note_type': 'danger'}
        resp = jsonify(data)
        resp.status_code = 200
    else:
        data = {}
        resp = jsonify(data)
        resp.status_code = 400
    return resp

@admin.route('/thumbs/<path:filename>')
@rbac_manager.allow(['common_user'], methods=['GET', 'POST'])
def img_pri(filename):
    return send_from_directory(
        os.path.join(app.config['CONTENT_FOLDER'], 'thumbnails'),
        filename
    )

@admin.route('/video/<path:filename>')
@rbac_manager.allow(['common_user'], methods=['GET', 'POST'])
def protected(filename):
    return send_from_directory(
        os.path.join(app.config['CONTENT_FOLDER'], 'uploads'),
        filename
    )

@admin.route('/profile_pics/<path:filename>')
@rbac_manager.allow(['common_user'], methods=['GET', 'POST'])
def pro_pic(filename):
    return send_from_directory(
        os.path.join(app.config['CONTENT_FOLDER'], 'profile_pics'),
        filename
    )

@admin.route('/admin_static/<path:filename>')
@rbac_manager.allow(['common_user'], methods=['GET', 'POST'])
def admin_s(filename):
    (fpath, f) = os.path.split(filename)
    return send_from_directory(
        os.path.join(app.config['ADMIN_FOLDER'], fpath),
        f)

@admin.route('/register', methods=['GET', 'POST'])
@rbac_manager.allow(['admin'], methods=['GET', 'POST'])
def register():
    nav = make_navigation(current_user)
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
    return render_template('register.html', logoinf=logoinf, form=form,
                           navigation_bar=nav, right_bar=right_bar,
                           custom_content=custom_content)

@admin.route('/add_Role', methods=['GET', 'POST'])
@rbac_manager.allow(['admin'], methods=['GET', 'POST'])
def add_roles():
    nav = make_navigation(current_user)
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
    return render_template('role_register.html', logoinf=logoinf, form=form,
                           navigation_bar=nav, right_bar=right_bar,
                           custom_content=custom_content)

@admin.route('/roles', methods=['GET', 'POST'])
@rbac_manager.allow(['admin'], methods=['GET', 'POST'])
def role_administration():
    nav = make_navigation(current_user)
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
    return render_template('role_ad.html', logoinf=logoinf,
                           navigation_bar=nav, right_bar=right_bar,
                           custom_content=custom_content)

@admin.route('/users', methods=['GET', 'POST'])
@rbac_manager.allow(['admin'], methods=['GET', 'POST'])
def user_administration():
    nav = make_navigation(current_user)
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
    return render_template('user_list.html', logoinf=logoinf,
                           navigation_bar=nav, right_bar=right_bar,
                           custom_content=custom_content)

@admin.route('/useredit/<id_u>', methods=['GET', 'POST'])
@rbac_manager.allow(['admin'], methods=['GET', 'POST'])
def user_edit(id_u):
    nav = make_navigation(current_user)
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
    return render_template('edit_user.html', logoinf=logoinf, right_bar=right_bar, form=form,
                           navigation_bar=nav, custom_content=custom_content)

@admin.route('/videdit/<id_v>', methods=['GET', 'POST'])
@rbac_manager.allow(['common_user'], methods=['GET', 'POST'])
def video_edit(id_v):
    nav = make_navigation(current_user)
    edit_video = Video.get_by_id(id_v)
    custom_content = {'title': 'Video Information', 'active_page': 'upload',
                          'page_headT': "Information", 'update': None}
    if(edit_video is not None and
       current_user.id == edit_video.owner_id
       and edit_video.is_deleted):
        return problems(custom_content, "Deleted Video", "Video is deleted and can not be changed.", nav)
    elif(edit_video is not None and
         current_user.id == edit_video.owner_id
         and not edit_video.is_deleted):
        form = VideoEditForm()
        form.set_video(edit_video)
        custom_content['video_thumb'] = url_for('admin.img_pri', filename=edit_video.thumbpath)
        custom_content['video_url']   = url_for('admin.protected', filename=edit_video.filepath)
        if (form.validate_on_submit() and form.submit.data):
            edit_video.title = form.name.data
            edit_video.description = form.description.data
            db.session.commit()
            custom_content['update'] = ['Congratulations, you updated the information of the video "'+ form.name.data +'"', 'success']
        elif request.method == 'GET':
            form.name.data = edit_video.title
            form.description.data = edit_video.description
        elif form.submit_delete.data:
            try:
                edit_video.remove_video()
                db.session.commit()
                custom_content['update'] = ['Video succesfully deleted', 'success']
            except cus_error.Al_Deleted:
                custom_content['update'] = ['Video is already deleted', 'danger']
        return render_template('video_edit.html', logoinf=logoinf, right_bar=right_bar, form=form,
                               navigation_bar=nav, custom_content=custom_content)
    else:
        return problems(custom_content, "Video not found", "Video can't be found or isn't editable.", nav)
