from flask import current_app as app
from app import db, login_manager, rbac_manager, cus_error
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
#from flask import current_
#from app import db, login_manager, rbac
from datetime import datetime
import time
import os
from .flask_rbac import RoleMixin

users_roles = db.Table(
    'users_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

roles_parents = db.Table(
    'roles_parents',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
    db.Column('parent_id', db.Integer, db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)

    parents = db.relationship(
        'Role',
        secondary=roles_parents,
        primaryjoin=(id == roles_parents.c.role_id),
        secondaryjoin=(id == roles_parents.c.parent_id),
        backref=db.backref('children', lazy='dynamic')
    )

    def __init__(self, name):
        RoleMixin.__init__(self)
        self.name = name

    def add_parent(self, parent):
        # You don't need to add this role to parent's children set,
        # relationship between roles would do this work automatically
        self.parents.append(parent)

    def add_parents(self, *parents):
        for parent in parents:
            self.add_parent(parent)

    def get_name(self):
        return self.name

    def get_parents_list(self):
        p_list = []
        for parent in self.parents:
            p_list.append(parent.name)
        return p_list

    @staticmethod
    def get_by_name(name):
        return Role.query.filter_by(name=name).first()

    @staticmethod
    def get_all_roles():
        roles = Role.query.all()
        role_tuple = []
        for role in roles:
            role_tuple.append((role.get_name(), role.get_name()))
        return role_tuple

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    username = db.Column(db.String(64), index=True, unique=True)
    active = db.Column(db.Boolean, default=True)
    create_date = db.Column(db.DateTime, index=True,
                            default=datetime.utcnow)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(564))
    profile_pic = db.Column(db.String(120))
    is_deleted = db.Column(db.Boolean, default=False)

    videos = db.relationship('Video', backref='user', lazy=True)
    u_reactions = db.relationship('LikedBy', backref='user', lazy=True)
    roles = db.relationship(
        'Role',
        secondary=users_roles,
        backref=db.backref('roles', lazy='dynamic')
    )
    u_comments = db.relationship("Comment", backref='user', lazy=True)

    def add_reaction(self, reaction):
        self.u_reactions.append(reaction)

    def add_comment(self, comment):
        self.u_comments.append(comment)

    def add_video(self, video):
        self.videos.append(video)

    def set_role_single(self, role):
        self.roles = [role]

    def add_role(self, role):
        self.roles.append(role)

    def add_roles(self, roles):
        for role in roles:
            self.add_role(role)

    def get_roles(self):
        for role in self.roles:
            yield role

    def get_first_role(self):
        for role in self.roles:
            return role.get_name()

    def is_active(self):
        return self.active

    def get_by_id(id):
        return User.query.filter_by(id=id).first()

    def get_role_dict(self):
        dict_roles = {}
        for role in self.roles:
            dict_roles[role.get_name()] = 1
        return dict_roles

    def __repr__(self):
        return '<User {}>'.format(self.username)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vid_of_id = db.Column(db.String(256), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                         nullable=False)
    thumbpath = db.Column(db.String(256), index=True, unique=True)
    filepath  = db.Column(db.String(256), index=True, unique=True)
    title  = db.Column(db.String(128))
    description  = db.Column(db.String(512))
    pub_date = db.Column(db.DateTime, index=True,
                         default=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)
    vid_hash = db.Column(db.String(256))
    is_deleted = db.Column(db.Boolean, default=False)

    v_reactions = db.relationship('LikedBy', backref='video', lazy=True)
    vid_comments = db.relationship('Comment', backref=db.backref('vid_comments', lazy=True),
                                   order_by="desc(Comment.likes), Comment.id")

    def remove_video(self):
        if not (self.is_deleted):
            self.title = None
            self.description = None
            self.vid_hash = None
            self.is_deleted = True
            os.remove(os.path.join(app.config['CONTENT_FOLDER'], 'uploads', self.filepath))
            os.remove(os.path.join(app.config['CONTENT_FOLDER'], 'thumbnails', self.thumbpath))
            self.thumbpath = None
            self.filepath = None
        else:
            raise cus_error.Al_Deleted("Video already deleted")

    def add_reaction(self, reaction, user_id):
        reac_id = reaction.owner_id
        pre_like = LikedBy.query.filter_by(owner_id=user_id, video_id=self.id).first()
        if(self.is_deleted):
            raise cus_error.Al_Deleted("Deleted videos can not be liked/disliked")
        if(not pre_like):
            self.v_reactions.append(reaction)
            if(reaction.liked):
                self.likes = self.likes+1
            else:
                self.dislikes = self.dislikes+1
        elif(pre_like.liked != reaction.liked):
            pre_like.liked = reaction.liked
            if(reaction.liked):
                self.likes = self.likes+1
                self.dislikes = self.dislikes-1
            else:
                self.dislikes = self.dislikes+1
                self.likes = self.likes-1
        else:
            raise cus_error.Al_Exists("Exact reaction already exists")

    def get_owner(self):
        return User.query.get(self.owner_id)

    def own_name(self):
        return (User.query.get(self.owner_id)).username

    def add_comment(self, comment):
        self.vid_comments.append(comment)

    def get_comments(self):
        return self.vid_comments

    def get_by_id(id):
        return Video.query.filter_by(id=id).first()

    def __repr__(self):
        return '<title: {0} filepath: {1} thumbpath: {2} comment: {3} pub_date: {4} >'.format(self.title, self.filepath, self.thumbpath, self.comment, self.pub_date)
    def set_title(self, newtitle):
        self.title = newtitle

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'))
    parent = db.Column(db.Integer, db.ForeignKey('comment.id'))
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)
    respons_num = db.Column(db.Integer, default=0)
    depth_num = db.Column(db.Integer, default=0)
    content = db.Column(db.String(512))
    pub_date = db.Column(db.DateTime, index=True,
                         default=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)

    own_user = db.relationship("User", foreign_keys=user_id)
    responses = db.relationship("Comment",
                                backref=db.backref('comment', remote_side=[id]))
    c_reactions = db.relationship('LikedBy', backref='comment', lazy=True)


    def remove_comment(self, owner_id):
        if(not self.is_deleted):
            if(self.user_id == owner_id):
                self.content = None
                self.is_deleted = True
            else:
                raise cus_error.Wrong_Own()
        else:
            raise cus_error.Al_Deleted()

    def get_vid(self):
        img = (Video.query.filter_by(id=self.video_id).first())
        return img

    def get_vid_img(self):
        img = (Video.query.filter_by(id=self.video_id).first()).thumbpath
        return img

    def get_vid_of_id(self):
        vid_of = (Video.query.filter_by(id=self.video_id).first()).vid_of_id
        return vid_of

    def add_reaction(self, reaction, user_id):
        reac_id = reaction.owner_id
        pre_like = LikedBy.query.filter_by(owner_id=user_id, comment_id=self.id).first()
        vid_del = (Video.query.filter_by(id=self.video_id).first()).is_deleted
        if(vid_del or self.is_deleted):
            raise cus_error.Al_Deleted()
        if(not pre_like):
            self.c_reactions.append(reaction)
            if(reaction.liked):
                self.likes = self.likes+1
            else:
                self.dislikes = self.dislikes+1
        elif(pre_like.liked != reaction.liked):
            pre_like.liked = reaction.liked
            if(reaction.liked):
                self.likes = self.likes+1
                self.dislikes = self.dislikes-1
            else:
                self.dislikes = self.dislikes+1
                self.likes = self.likes-1
        else:
            raise cus_error.Al_Exists("Exact reaction already exists")

    def add_subcomment(self, comment):
        self.responses.append(comment)
        self.respons_num = self.respons_num + 1

    def add_depth(self, parent):
        self.depth_num = parent.depth_num + 1

    def own_name(self):
        return self.own_user.username

    def get_subcomments(self):
        return self.responses

    def get_by_id(id):
        return Comment.query.filter_by(id=id).first()


class LikedBy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    liked = db.Column(db.Boolean, nullable=False)
    #own_user = db.relationship("User", foreign_keys=user_id)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

rbac_manager.set_role_model(Role)
rbac_manager.set_user_model(User)
