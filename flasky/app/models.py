# -*- coding: utf-8 -*-
# @Time    : 2020/8/28 20:48
# @Author  : SSK
# @FileName: models.py
# @Software: PyCharm
from . import db
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from . import login_manager

class Role(db.Model):
    __tablename__='roles'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique=True)
    users = db.relationship('User',backref='role')

    def __repr__(self):
        return '<Role %r>' %self.name

class User(UserMixin,db.Model):
    __tablename__='users'
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(64),unique=True,index=True)
    username = db.Column(db.String(64),unique=True,index=True)
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))
    password_hash=db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self,password):
        self.password_hash=generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    def __repr__(self):
        return '<User %r>' %self.username

# 对于flask-login来说是必备的函数
# login_manager.user_loader 装饰器把这个函数注册给 Flask-Login，在这个扩展需要获取已 登录用户的信息时调用。
@login_manager.user_loader
def load_user(user_id):
    # get方法返回对应主键所对应的一行
    return User.query.get(int(user_id))

