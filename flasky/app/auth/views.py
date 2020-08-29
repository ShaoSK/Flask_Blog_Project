# -*- coding: utf-8 -*-
# @Time    : 2020/8/29 10:47
# @Author  : SSK
# @FileName: views.py
# @Software: PyCharm

from flask import render_template,redirect,request,url_for,flash
from flask_login import login_user
from flask_login import logout_user,login_required
from . import auth
from ..models import User
from .forms import LoginForm,RegisterationForm
from .. import db

# 登入
# 注意是methods而不是method，会报错TypeError: __init__() got an unexpected keyword argument 'method'
@auth.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswitch('/'):
                next = url_for('main.index')
            return redirect(next)
        flash('Invilid username or password')
    # 记住这里要写一个return 否则没有返回值
    return render_template('auth/login.html',form=form)

# 登出
@auth.route('/logout')
# 这里的login_required就是所说的受保护的页面，只有已经登录的用户才可以访问，
# 当匿名用户尝试访问时login_view会重定向到auth.login页面
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register',methods=['GET','POST'])
def register():
    form = RegisterationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,username=form.username.data,password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You can now login.')
        return redirect(url_for('.login'))
    return render_template('auth/register.html',form=form)
