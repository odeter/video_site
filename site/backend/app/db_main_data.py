from flask import current_app as app
from app import thumbnail
from app.models import db, User, Video, Role, Comment
from app.custom_functions import calc_file_hash, calc_string_hash
import os
import time
import datetime
import io
from shutil import copy

#db.drop_all()
# create some user data #
def default_setup():
    create_userbase()
    create_vid_test(20)

def create_userbase():
    if not Role.query.filter_by(name='common_user').first():
        commen_user = Role(name="common_user")
        db.session.add(commen_user)
        db.session.commit()

    if not Role.query.filter_by(name='admin').first() and Role.query.filter_by(name='common_user').first():
            nrole = Role(name="admin")
            nrole.add_parent(Role.get_by_name('common_user'))
            db.session.add(nrole)
            db.session.commit()

    if not User.query.filter_by(email='chrismulvad@gmail.com').first():
        admin = User(username="chris", email="chrismulvad@gmail.com")
        admin.set_password("1234")
        admin.add_role(Role.get_by_name('admin'))
        db.session.add(admin)
        db.session.commit()


def clear_all_videos():
    all_videos = Video.query.all()
    for j in all_videos:
        vid_f = os.path.join(app.config['CONTENT_FOLDER'], 'uploads',  j.filepath)
        thu_f = os.path.join(app.config['CONTENT_FOLDER'], 'thumbnails', j.thumbpath)
        if os.path.exists(vid_f):
            os.remove(vid_f)
        if os.path.exists(thu_f):
            os.remove(thu_f)
    Video.query.delete()
    db.session.commit()

def clear_all_comments():
    Comment.query.delete()
    db.session.commit()

def create_vid_test(ran):
    for i in range(ran):
        user = User.query.first()
        vtitle = "test"
        vdescription = "test"
        #f = open(os.path.join(app.config['CONTENT_FOLDER'], 'uploads',  "20190317040352.mp4"))
        f_hash = "test_"+str(i)+"_"+str(int(time.time()))
        vid_of_t = calc_string_hash(datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S') + str(user.id) + str(i))
        nfilename = vid_of_t + ".mp4"
        nthumbname = vid_of_t + ".png"
        filepath = os.path.join(app.config['CONTENT_FOLDER'], 'uploads',  nfilename)
        thumbpath = os.path.join(app.config['CONTENT_FOLDER'], 'thumbnails', nthumbname)
        copy(os.path.join(app.config['TEST_FOLDER'], 'video',  "test_1.mp4"),  filepath)
        thumbnail.generate_thumbnail(filepath, thumbpath, 5)
        video = Video(filepath=nfilename, title=vtitle, description=vdescription, thumbpath=nthumbname, vid_hash=f_hash, vid_of_id=vid_of_t)
        user.add_video(video)
        #video.set_owner(current_user)
        db.session.add(video)
        db.session.commit()

# if not User.query.filter_by(email='test@test.dk').first():
#     nuser = User(username="test", email="test@test.dk", profile_pic=standard_pic)
#     nuser.set_password("1234")
#     nuser.add_role(Role.get_by_name('n_user'))
#     db.session.add(nuser)
#     db.session.commit()
