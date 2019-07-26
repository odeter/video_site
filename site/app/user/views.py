from . import user_main

import os
import datetime
import time
#import app
from flask import current_app as app, Flask, render_template, session, redirect, url_for, request, flash, send_from_directory, jsonify
#from lasha import app
from app.error_pages.views import problems
from app import db, thumbnail, mail_manager, rbac_manager, cus_error
from flask_login import current_user, login_user, logout_user, login_required
from app.custom_functions import calc_file_hash, calc_string_hash, make_navigation, comment_sub, comments_to_list, profile_pic
from app.models import User, Video, Role, Comment, LikedBy
from app.forms import FileuploadForm, AccountForm, CommentForm, VideoEditForm, SearchForm
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from pyee import EventEmitter
from flask_mail import Message

@user_main.route('/user_static/<path:filename>')
@rbac_manager.allow(['common_user'], methods=['GET', 'POST'])
def static_locked(filename):
    (fpath, f) = os.path.split(filename)
    return send_from_directory(
        os.path.join(app.config['USER_STATIC'], fpath),
        f)

@user_main.route('/')
@user_main.route('/index')
@rbac_manager.allow(['common_user'], methods=['GET', 'POST'])
def index():
    nav = make_navigation(current_user)
    logoinf = app.config['LOGO_INFO']
    right_bar = app.config['RIGHT_BAR']
    custom_content = {'title': 'Home', 'active_page': 'home',
                      'page_headT': "Dashboard", 'update': None}
    vid = Video.query.filter_by(is_deleted=False).order_by(Video.pub_date.desc()).all()
    video_info = []
    for nv in vid:
        print(nv.vid_hash)
        m_title = nv.title if (len(nv.title) < 10) else nv.title[:10] + "..."
        m_description = nv.description if (len(nv.description) < 15) else nv.description[:15] + "..."
        video_info.append([url_for('user_main.play', fileh=nv.vid_of_id), m_title,
                           url_for('api_r.img_pri', filename=nv.thumbpath), nv.pub_date, m_description])
    return render_template('user_main.home.html', video_info=video_info, logoinf=logoinf,
                           navigation_bar=nav, right_bar=right_bar,
                           custom_content=custom_content)

@user_main.route('/settings', methods=['GET', 'POST'])
@rbac_manager.allow(['common_user'], methods=['GET', 'POST'])
def settings():
    nav = make_navigation(current_user)
    logoinf = app.config['LOGO_INFO']
    right_bar = app.config['RIGHT_BAR']
    form = AccountForm()
    custom_content = {'title': 'Account Settings', 'active_page': '',
                      'page_headT': "Information", 'update': None,
                      'user_inf': [current_user.username, current_user.email,
                                   current_user.about_me,
                                   url_for('api_r.pro_pic', filename=profile_pic(current_user)),
                                   url_for('user_main.static_locked', filename="assets/img/avatar_back.jpg")],
                      'u_video_head' : [], 'u_videos' : [], 'u_com_head' : [], 'u_comment': []}

    custom_content['u_video_head'] = ['Thumbnail','Title', 'Creation Date', 'Likes', 'Dislikes']
    custom_content['u_com_head'] = ['Thumbnail', 'Video Title', 'Comment', 'Creation Date', 'Likes', 'Dislikes', 'Delete' ]

    u_videos = Video.query.filter_by(owner_id=current_user.id, is_deleted=False).order_by(Video.pub_date.desc())
    for vid in u_videos:
        (custom_content['u_videos']).append([url_for('user_main.video_edit', id_v=vid.id),
                                             url_for('api_r.img_pri', filename=vid.thumbpath),
                                             [vid.title, vid.pub_date, vid.likes, vid.dislikes]])

    u_comment = Comment.query.filter_by(user_id=current_user.id, is_deleted=False).order_by(Comment.pub_date.desc())
    for com in u_comment:
        vid = com.get_vid()
        vid_thumb = url_for('api_r.img_pri', filename=vid.thumbpath) if vid.thumbpath else None
        content = com.content if (len(com.content) < 10) else com.content[:10] + "..."
        (custom_content['u_comment']).append([url_for('user_main.play', fileh=vid.vid_of_id),
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
                                      url_for('api_r.pro_pic', filename=profile_pic(current_user)),
                                      url_for('user_main.static_locked', filename="assets/img/avatar_back.jpg")]
        custom_content['update'] = ['Congratulations, you updated your information!', 'success']
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.about_me.data = current_user.about_me
    return render_template('user_main.u_settings.html', logoinf=logoinf, right_bar=right_bar, form=form,
                           navigation_bar=nav, custom_content=custom_content)


@user_main.route('/account', methods=['GET', 'POST'])
@rbac_manager.allow(['common_user'], methods=['GET', 'POST'])
def account():
    return redirect(url_for('user_main.index'))

@user_main.route('/upload', methods=['GET', 'POST'])
@rbac_manager.allow(['common_user'], methods=['GET', 'POST'])
def upload_file():
    nav = make_navigation(current_user)
    logoinf = app.config['LOGO_INFO']
    right_bar = app.config['RIGHT_BAR']
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
    return render_template('user_main.upload.html', form=form, logoinf=logoinf,
                           navigation_bar=nav, right_bar=right_bar,
                           custom_content=custom_content)

@user_main.route('/gallery', methods=['GET', 'POST'])
@rbac_manager.allow(['common_user'], methods=['GET', 'POST'])
def gallery():
    nav = make_navigation(current_user)
    logoinf = app.config['LOGO_INFO']
    right_bar = app.config['RIGHT_BAR']
    custom_content = {'title': 'Gallery', 'active_page': 'gallery',
                      'page_headT': "Video Gallery", 'update': None}
    video_info = []
    form = SearchForm()
    max_load = app.config['NUM_OF_VID_SCROLL']
    vid = Video.query.filter_by(is_deleted=False).order_by(Video.pub_date.desc()).all()

    re_vid = vid if len(vid) < max_load else vid[:max_load]
    custom_content["last_id"] = len(re_vid)
    for nv in re_vid:
        #print(nv.vid_hash)
        m_title = nv.title if (len(nv.title) < 10) else nv.title[:10] + "..."
        m_description = nv.description if (len(nv.description) < 15) else nv.description[:15] + "..."
        video_info.append([url_for('user_main.play', fileh=nv.vid_of_id), m_title,
                           url_for('api_r.img_pri', filename=nv.thumbpath), nv.pub_date, m_description, nv.likes, nv.dislikes])
    return render_template('user_main.gallery.html', video_info=video_info, logoinf=logoinf,
                           navigation_bar=nav, right_bar=right_bar, form=form,
                           custom_content=custom_content)

@user_main.route('/player/<fileh>', methods=['GET', 'POST'])
@rbac_manager.allow(['common_user'], methods=['GET', 'POST'])
def play(fileh):
    nav = make_navigation(current_user)
    logoinf = app.config['LOGO_INFO']
    right_bar = app.config['RIGHT_BAR']
    form = CommentForm()
    vid = Video.query.filter_by(vid_of_id=fileh).first()
    custom_content = {'title': "Video Player", 'active_page': 'gallery',
                      'page_headT': "", 'update': None, 'comments': None}

    if (vid is not None):
        owner = vid.get_owner()
        video_info = {'deleted': False, 'pub_date' : vid.pub_date,
                          'owner' : owner.username, 'owner_pic' : url_for('api_r.pro_pic', filename=profile_pic(owner)),
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
            video_info['video_url'] = url_for('api_r.protected', filename=vid.filepath)
            video_info['title'] = vid.title
            video_info['description'] = vid.description
            video_info['video_thumb'] = url_for('api_r.img_pri', filename=vid.thumbpath)
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
        return render_template('user_main.play.html', video_info=video_info, logoinf=logoinf,
                               navigation_bar=nav, right_bar=right_bar, form=form,
                               custom_content=custom_content)
    else:
        return problems(custom_content, "Video not found", "Video can't be found.", nav, logoinf, right_bar)

@user_main.route('/videdit/<id_v>', methods=['GET', 'POST'])
@rbac_manager.allow(['common_user'], methods=['GET', 'POST'])
def video_edit(id_v):
    nav = make_navigation(current_user)
    logoinf = app.config['LOGO_INFO']
    right_bar = app.config['RIGHT_BAR']
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
        custom_content['video_thumb'] = url_for('api_r.img_pri', filename=edit_video.thumbpath)
        custom_content['video_url']   = url_for('api_r.protected', filename=edit_video.filepath)
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
        return render_template('user_main.video_edit.html', logoinf=logoinf, right_bar=right_bar, form=form,
                               navigation_bar=nav, custom_content=custom_content)
    else:
        return problems(custom_content, "Video not found", "Video can't be found or isn't editable.", nav)
