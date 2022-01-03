import hashlib
import os
from flask import current_app as app, url_for

def make_navigation(user):
    role_dict = user.get_role_dict()
    if 'admin' in role_dict:
        return (app.config['NAVIGATION_BAR'] + app.config['NAVIGATION_BAR_ADMIN'])
    return app.config['NAVIGATION_BAR']

def calc_file_hash(file_name):
    BLOCKSIZE = 65536
    hasher = hashlib.sha1()
    buf = file_name.read(BLOCKSIZE)
    while len(buf) > 0:
        hasher.update(buf)
        buf = file_name.read(BLOCKSIZE)
    return hasher.hexdigest()

def calc_string_hash(in_string):
    bys = str.encode(in_string)
    hash_object = hashlib.sha256(bys)
    return hash_object.hexdigest()

## Comments helping functions for the play site

def get_profile_pic(user):
    if not user.profile_pic:
        return url_for('static', filename=os.path.join("img",app.config['DEFAULT_PROFILE_PIC']))
    else:
        return url_for('api_r.pro_pic',  filename=user.profile_pic.filepath)

def comment_sub(comments):
    done_comments = []
    for comment in comments:
        subcomments = None
        if comment.get_subcomments() is not None:
            subcomments = comment_sub(comment.get_subcomments())
        done_comments.append([comment.own_user.username, comment.content, comment.likes,
                              comment.dislikes, (comment.pub_date).strftime("%Y-%m-%d %H:%M:%S"),
                              url_for('api_r.pro_pic', filename=profile_pic(comment.own_user)),
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
                                  url_for('api_r.pro_pic', filename=profile_pic(comment.own_user)),
                                  comment.respons_num, comment.id, comment.is_deleted, subcomments])
    return done_comments
