"""empty message

Revision ID: 8204f55829cd
Revises: 3c394c57c3b1
Create Date: 2019-04-12 18:36:06.441656

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8204f55829cd'
down_revision = '3c394c57c3b1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('create_date', sa.DateTime(), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('about_me', sa.String(length=564), nullable=True),
    sa.Column('profile_pic', sa.String(length=120), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_create_date'), 'user', ['create_date'], unique=False)
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('roles_parents',
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['role.id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], )
    )
    op.create_table('users_roles',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], )
    )
    op.create_table('video',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('vid_of_id', sa.String(length=128), nullable=False),
    sa.Column('owner_id', sa.Integer(), nullable=False),
    sa.Column('thumbpath', sa.String(length=120), nullable=True),
    sa.Column('filepath', sa.String(length=120), nullable=True),
    sa.Column('title', sa.String(length=128), nullable=True),
    sa.Column('description', sa.String(length=512), nullable=True),
    sa.Column('pub_date', sa.DateTime(), nullable=True),
    sa.Column('likes', sa.Integer(), nullable=True),
    sa.Column('dislikes', sa.Integer(), nullable=True),
    sa.Column('vid_hash', sa.String(length=128), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_video_filepath'), 'video', ['filepath'], unique=True)
    op.create_index(op.f('ix_video_pub_date'), 'video', ['pub_date'], unique=False)
    op.create_index(op.f('ix_video_thumbpath'), 'video', ['thumbpath'], unique=True)
    op.create_table('comment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('video_id', sa.Integer(), nullable=True),
    sa.Column('parent', sa.Integer(), nullable=True),
    sa.Column('likes', sa.Integer(), nullable=True),
    sa.Column('dislikes', sa.Integer(), nullable=True),
    sa.Column('respons_num', sa.Integer(), nullable=True),
    sa.Column('depth_num', sa.Integer(), nullable=True),
    sa.Column('content', sa.String(length=512), nullable=True),
    sa.Column('pub_date', sa.DateTime(), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['parent'], ['comment.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['video_id'], ['video.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comment_pub_date'), 'comment', ['pub_date'], unique=False)
    op.create_table('liked_by',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('comment_id', sa.Integer(), nullable=True),
    sa.Column('video_id', sa.Integer(), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.Column('liked', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['comment_id'], ['comment.id'], ),
    sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['video_id'], ['video.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('liked_by')
    op.drop_index(op.f('ix_comment_pub_date'), table_name='comment')
    op.drop_table('comment')
    op.drop_index(op.f('ix_video_thumbpath'), table_name='video')
    op.drop_index(op.f('ix_video_pub_date'), table_name='video')
    op.drop_index(op.f('ix_video_filepath'), table_name='video')
    op.drop_table('video')
    op.drop_table('users_roles')
    op.drop_table('roles_parents')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_index(op.f('ix_user_create_date'), table_name='user')
    op.drop_table('user')
    op.drop_table('role')
    # ### end Alembic commands ###
