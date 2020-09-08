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
from ..email import send_email
from flask_login import current_user

# 登入
# 注意是methods而不是method，会报错TypeError: __init__() got an unexpected keyword argument 'method'
@auth.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            # 当用户还没有登录，请求的所有url都会重定向到该路由函数，next里面就存储了登录之后的定向路由
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
        # 现在这个注册路由函数需要发送确认邮件，需要在发送确认邮件之前调用db.session.commit()因为只有提交之后才能获得用户id，确认令牌
        # 需要用到用户id
        token = user.generate_confirmation_token()
        # 给用户发送的email中包含的url里面有令牌token，打开url，即定位到下面confirm路由函数
        send_email(user.email,'Confirm Your Account','auth/email/confirm',user=user,token=token)
        flash('A confirmation email has been sent to you by email.')
        # flash('You can now login.')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html',form=form)

@auth.route('/confirm/<token>')
@login_required
#Flask-Login 提供的 login_required 装饰器会保护这个路由，因此，用户点击确认邮件中的链接后，要先登录，然后才能执行这个视图函数。
def confirm(token):
    # 先检查已登录的用户是否确认过，如果确认过，则重定向到首页
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    # 令牌完全在User模型中完成，所以只需要调用confirm方法即可，然后根据不同的确认结果闪现不同的消息即可。
    if current_user.confirm(token):
        # 确认成功之后，confirm方法里面已经add了，下面会commit提交新的confirmed的值。
        db.session.commit()
        flash('You have confirmed your account.Thanks')
    else:
        flash('The confirmation link is invalid or has expired')
    return redirect(url_for('main.index'))

@auth.before_app_request
def before_request():
    # 用户已经登录 请求的url不在auth蓝本中
    if current_user.is_authenticated \
        and not current_user.confirmed \
        and request.blueprint != 'auth' \
        and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email,'Confirm your Account','auth/email/confirm',user=current_user,token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))

