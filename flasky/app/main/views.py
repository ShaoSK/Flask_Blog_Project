# -*- coding: utf-8 -*-
# @Time    : 2020/8/28 20:51
# @Author  : SSK
# @FileName: views.py
# @Software: PyCharm

from datetime import datetime
from flask import render_template, session, redirect, url_for,flash,request,abort,make_response
from . import main
from .forms import NameForm
from .. import db
from app.models import User,Role,Comment
from app.email import send_email
from config import config
import os
from flask import current_app
from flask_login import login_required, current_user
from ..decorators import admin_required,permission_required
from ..models import Permission,Post
from .forms import EditProfileForm,EditProfileAdminForm,PostForm,CommentForm

@main.route('/', methods=['GET', 'POST'])
def index():
    # 更新首页路由，展示博客
    form = PostForm()
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        # author是User模型中添加到Post模型中的对象实例属性，所以需要使用_get_current_object()获取当前对象实例
        post = Post(body=form.body.data,author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))

    # 添加显示所有用户的博客还是只显示关注用户的博客
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed',''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query

    # 修改首页路由，添加博客分页功能，也就是在每次查询数据库时，使用paginate函数返回一定数量的博客，返回的是一个Pagination类对象
    page = request.args.get('page',1,type=int)
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page,per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],error_out=False)
    posts = pagination.items
    return render_template('index.html',form=form,posts=posts,
                           show_followed=show_followed,pagination=pagination,current_time=datetime.utcnow())

# 设定show_followed cookie的值在两个新路由中设定
@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed','',max_age=30*24*60*60) #30天
    return resp

@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed','1',max_age=30*24*60*60)
    return resp

# @main.route('/admin')
# @login_required
# @admin_required
# def for_admin_only():
#     return "For administrators!"

# @main.route('/moderate')
# @login_required
# @permission_required(Permission.MODERATE)
# def for_moderator_only():
#     return "For comment moderators!"

# 为每一个用户创建资料可视化页面
# 改动资料页面，用以获取用户发表的文章列表
@main.route('/user/<username>')
def user(username):
    #
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html',user=user,posts=posts)

# 创建资料编辑路由
@main.route('/edit-profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        # 获取当前对象的数据库实例，并更新添加
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('You profile has been updated')
        return redirect(url_for('.user',username=current_user.username))
    # 这个表达式还能直接显示在表单中供用户编辑
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html',form=form)

# 创建管理员资料编辑路由
@main.route('/edit-profile/<int:id>',methods=['GET','POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        # form表单初始化时，role_id这个标识符被赋值给了form.role.data,查询时就使用这个Role模型中的role_id
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated')
        return redirect(url_for('.user',username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html',form=form,user=user)

# 定义路由，生成博客的url链接
# 修改博客路由，展示博客评论
@main.route('/post/<int:id>',methods=['GET','POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,post=post,author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been published!')
        # 这里的return 可以看到增加了额外的page参数，这个参数可以在request中被捕获到
        return redirect(url_for('.post',id=post.id,page=-1))
    page = request.args.get('page',1,type=int)
    # 如果page=-1，即有新评论提交，要重新计算评论总数
    if page == -1:
        # 这里通过反向外键，直接获取博客中的所有评论数量
        page = (post.comments.count()-1)//current_app.config['FLASKY_COMMENTS_PER_PAGE']+1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page,per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],error_out=False
    )
    comments = pagination.items

    # 写成[post]的原因是index.html和user.html都使用了_posts.html，都以列表的形式 循环for in 展示了许多博客，
    # post.html也使用了_posts.html，但只有 “一个” post,写成[post]方便在_posts.html调用
    return render_template('post.html',posts=[post],form=form,comments=comments,pagination=pagination)

@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE)
def moderate():
    page = request.args.get('page',1,type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page,per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],error_out=False
    )
    comments = pagination.items
    return render_template('moderate.html',comments=comments,pagination=pagination,page=page)

# 添加路由，用来切换评论的状态
@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate',page=request.args.get('page',1,type=int)))

@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate',page=request.args.get('page',1,type=int)))



# 博客文章编辑器路由
@main.route('/edit/<int:id>',methods=['GET','POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMIN):
        abort(404)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash("The post has been updated")
        return redirect(url_for('.post',id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html',form=form)

# 新建路由，添加关注和取消关注功能
@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid User')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('You are already following this user')
        return redirect(url_for('.user',username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are now following %s'%username)
    return redirect(url_for('.user',username=username))

@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid User')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('You are not following this user')
        return redirect(url_for('.user',username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are now not following %s anymore'%username)
    return redirect(url_for('.user',username=username))

# 有哪些人关注了我
@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid User')
        return redirect(url_for('.index'))
    page = request.args.get('page',1,type=int)
    # 这里的pagiantion是一个实例列表，为了渲染方便，将它转换为一个index列表follows
    pagination = user.followers.paginate(
        page,per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False
    )
    follows = [{'user':item.follower,'timestamp':item.timestamp} for item in pagination.items]
    return render_template('followers.html',user=user,title='Followers of ',endpoint='.followers',
                           pagination=pagination,follows=follows)

# 我关注了哪些人
@main.route('/followed_by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid User')
        return redirect(url_for('.index'))
    page = request.args.get('page',1,type=int)
    # 这里的pagiantion是一个实例列表，为了渲染方便，将它转换为一个index列表follows
    pagination = user.followed.paginate(
        page,per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False
    )
    follows = [{'user':item.followed,'timestamp':item.timestamp} for item in pagination.items]
    return render_template('followers.html',user=user,title='Followed by ',endpoint='.followed_by',
                           pagination=pagination,follows=follows)