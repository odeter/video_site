from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_uploads import UploadSet, IMAGES
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, HiddenField, SelectField, HiddenField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User, Video, Role
from app.custom_functions import calc_file_hash
from flask import url_for
from flask_login import current_user


class SearchForm(FlaskForm):
    gal_search = StringField('Search By', render_kw={"class": "form-control"})
    gal_filter =  SelectField('Filter By', choices=[('ct', 'Upload Time'), ('li', 'Likes')], validators=[DataRequired()], render_kw={"class": "form-control"})
    gal_sort =  SelectField('Sort By', choices=[('high', 'High to Low'), ('low', 'Low to High')], validators=[DataRequired()], render_kw={"class": "form-control"})
    submit = SubmitField('Search')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class VideoEditForm(FlaskForm):
    name = StringField('Title', render_kw={"class": "form-control"},
                       validators=[DataRequired(), Length(max=25, message=('Max 25 chars'))])
    description = TextAreaField('Description', render_kw={"class": "form-control"},
                            validators=[Length(max=512, message=('Max 512 chars'))])
    submit = SubmitField('Save Changes')
    submit_delete = SubmitField('Delete Video')
    edit_video = None

    def set_video(self, video):
        self.edit_video = video


class FileuploadForm(VideoEditForm):
    upFile = FileField('Video File', render_kw={"class": "form-control"}, id='fiup',
                       validators=[FileRequired(), FileAllowed(['gif', 'mkv', 'mp4', 'webm'],
                                                               'Videos only!')])
    submit = SubmitField('Upload')

    def validate_upFile(self, upFile):
        print("------- is called -----------")
        f_hash = calc_file_hash(upFile.data)
        vid = Video.query.filter_by(vid_hash=f_hash).first()
        if vid is not None:
            raise ValidationError(['Video already exists', url_for('admin.play', filename=vid.filepath)])
        else:
            upFile.data.seek(0)

class CommentForm(FlaskForm):
    comment = TextAreaField('Your Comment', render_kw={"class": "form-control", "rows":"6"},
                            validators=[Length(max=1024, message=('Max 1024 chars'))])
    parent = HiddenField('parent')
    submit = SubmitField('Submit')


class RoleForm(FlaskForm):
    role_name = StringField('Role Name', validators=[DataRequired()], render_kw={"placeholder": "Role Name", "class": "form-control"})
    parent_name = SelectField('Parent Name', render_kw={"class": "form-control"})
    submit = SubmitField('Create Role')

    def __init__(self, *args, **kwargs):
        super(RoleForm, self).__init__(*args, **kwargs)
        self.parent_name.choices = [('', '-- None --')] + Role.get_all_roles()

    def validate_role_name(self, role_name):
        role = Role.get_by_name(role_name)
        if role is not None:
            raise ValidationError('Please use a different username.')

    def validate_parent_nameole(self, parent_name):
        if(parent_name):
            parent_role = Role.get_by_name(parent_role)
            if parent_role is None:
                raise ValidationError('Parent role do not exist.')

class ProfileImageForm(FlaskForm):
    pro_pic = HiddenField('Profile Image', validators=[DataRequired()], render_kw={"class": "form-control"}, id='fiup')
    submit_pro = SubmitField('Change profile image',
                             render_kw={"class": "btn btn-info btn-fill"})

class AccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={"placeholder": "Username", "class": "form-control"})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Email", "class": "form-control"})
    password = PasswordField('New Password', validators=[], render_kw={"placeholder": "Password", "class": "form-control"})
    password2 = PasswordField(
        'Repeat New Password', validators=[EqualTo('password')], render_kw={"placeholder": "Password", "class": "form-control"})
    about_me = TextAreaField('About Me', render_kw={"class": "form-control", "rows":"6"},
                             validators=[Length(max=512, message=('Max 512 chars'))])
    submit_acc = SubmitField('Change Information',
                             render_kw={"class": "btn btn-info btn-fill"})

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        print("-.------ heyooooo------")
        if user is not None and current_user.username != user.username:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None and current_user.email != user.email:
            raise ValidationError('Please use a different email address.')

class RegistrationForm(AccountForm):
    submit = SubmitField('Create User')
    roles = SelectField('Role', render_kw={"class": "form-control"})

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.roles.choices = Role.get_all_roles()


class UserAlterForm(RegistrationForm):
    submit = SubmitField('Edit User')
    active = BooleanField('Active')
    edit_user = None

    def set_user(self, user):
        self.edit_user = user

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None and self.edit_user.username != user.username:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None and self.edit_user.email != user.email:
            raise ValidationError('Please use a different email address.')
