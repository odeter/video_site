from . import api_r

import os
import datetime
import time
#import app
from flask import current_app as app
from flask import Flask, render_template, session, redirect, url_for, request, flash, send_from_directory, jsonify
#from lasha import app
from app import thumbnail, mail_manager, rbac_manager, cus_error
from flask_login import current_user, login_user, logout_user, login_required
from app.models import db, User, Video, Role, Comment, LikedBy
from pyee import EventEmitter
from flask_mail import Message

#from raven.contrib.flask import Sentry

@api_r.route('/api', methods=['POST'])
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
                video_info.append([url_for('user_main.play', fileh=nv.vid_of_id), m_title,
                                   url_for('api_r.img_pri', filename=nv.thumbpath), nv.pub_date, m_description, nv.likes, nv.dislikes])
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

@api_r.route('/thumbs/<path:filename>')
@rbac_manager.allow(['common_user'], methods=['GET', 'POST'])
def img_pri(filename):
    return send_from_directory(
        os.path.join(app.config['CONTENT_FOLDER'], 'thumbnails'),
        filename
    )

@api_r.route('/video/<path:filename>')
@rbac_manager.allow(['common_user'], methods=['GET', 'POST'])
def protected(filename):
    return send_from_directory(
        os.path.join(app.config['CONTENT_FOLDER'], 'uploads'),
        filename
    )

@api_r.route('/profile_pics/<path:filename>')
@rbac_manager.allow(['common_user'], methods=['GET', 'POST'])
def pro_pic(filename):
    return send_from_directory(
        os.path.join(app.config['CONTENT_FOLDER'], 'profile_pics'),
        filename
    )
