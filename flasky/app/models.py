# -*- coding: utf-8 -*-
# @Time    : 2020/8/28 20:48
# @Author  : SSK
# @FileName: models.py
# @Software: PyCharm
from . import db
from werkzeug.security import generate_password_hash,check_password_hash
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app,request
from flask_login import UserMixin,AnonymousUserMixin
from datetime import datetime
import hashlib

class Role(db.Model):
    __tablename__='roles'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique=True)
    # index=True,设置索引，增加搜索速度
    default = db.Column(db.Boolean,default=False,index=True)
    # permissions二进制数的十进制表示的方式定义一组权限，SQLAlchemy默认将其设置为None
    permissions = db.Column(db.Integer)
    # 添加的这个字段，一对多关系中的一的视角，返回users属性返回与角色相关联的用户组成的列表
    users = db.relationship('User',backref='role',lazy='dynamic')

    def __init__(self,**kwargs):
        super(Role,self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0
    # 定义方法用于管理权限
    def add_permission(self,perm):
        if not self.has_permission(perm):
            self.permissions+=perm
    def remove_permission(self,perm):
        if self.has_permission(perm):
            self.permissions-=perm
    def reset_permission(self):
        self.permissions=0
    def has_permission(self,perm):
        # 按位与
        return self.permissions & perm ==perm

    # 使用静态方法在自动更新数据库中的角色列表
    @staticmethod
    def insert_role():
        roles = {
            'User':[Permission.FOLLOW,Permission.COMMENT,Permission.WRITE],
            'Moderator':[Permission.FOLLOW,Permission.COMMENT,Permission.WRITE,Permission.MODERATE],
            'Administrator':[Permission.FOLLOW,Permission.COMMENT,Permission.WRITE,Permission.MODERATE,Permission.ADMIN]
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role=Role(name=r)
            role.reset_permission()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default=(role.name==default_role)
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' %self.name

# 继承UserMixin，由Flask-login提供，is_authenticated，is_active，is_anonymous，get_id()都已经在这个类中实现了
class User(UserMixin,db.Model):
    __tablename__='users'
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(64),unique=True,index=True)
    # 定义外键，建立关系
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))

    username = db.Column(db.String(64), unique=True, index=True)
    password_hash=db.Column(db.String(128))
    # 增加账户确认字段
    confirmed = db.Column(db.Boolean,default=False)

    # 添加用户额外信息，让用户资料更加丰富
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    # default参数可以接收函数作为默认值，每次需要生成默认值时，SQLAlchemy就会调用函数
    member_since = db.Column(db.DateTime(),default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(),default=datetime.utcnow)

    # 用于记录每一个用户电子邮件的散列值，这样就不需要重复计算了
    avatar_hash = db.Column(db.String(32))

    # 重写init方法，在用户创建时，判断电子邮件是否是管理员，如果是，直接赋予管理员角色，而不是普通User角色
    def __init__(self,**kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASK_ADMIN']:
                self.role=Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role=Role.query.filter_by(default=True).first()
        # 在初始化用户实例时，就调用计算散列值的函数，给avatar_hash赋值，用于在数据库中存储散列值
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()

    # 如果用户更新了email，则重新计算散列值并存储进数据库
    def change_email(self,token):
        pass

    # 以下两个方法来检验用户是否具有某项权限
    # 便于后续编写自定义装饰器，检查用户是否具有某项权限，让视图函数对于特定的用户开放
    # 并且这里定义了匿名用户类，并且将他赋给了login_manager，用来对未登录的用户开放某些权限的视图函数
    def can(self,perm):
        # !!!在User类中调用Role中的方法# 从这里可以看到在Role模型中反向在User模型中定义的role属性在这里就派上了用场,role代表一个个的类实例
        return self.role is not None and self.role.has_permission(perm)
    def is_administrator(self):
        return self.can(Permission.ADMIN)

    # 添加方法，每次刷新用户的访问时间
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    # 定义计算散列值的函数
    def gravatar_hash(self):
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    # 添加方法，用于生成用户头像的url
    def gravatar(self,size=100,default='identicon',ratting='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.gravatar_hash() or self.avatar_hash
        return '{url}/{hash}?s={size}&d={default}&r={ratting}'.format(url=url,hash=hash,size=size,default=default,ratting=ratting)


    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self,password):
        self.password_hash=generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    ## 生成一个令牌，默认有效时间为expiration=3600,一小时
    def generate_confirmation_token(self,expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        # 将数据库用户中的id存储为一个加密令牌，用户id使用utf-8编码
        return s.dumps({'confirm':self.id}).decode('utf-8')

    ## 验证令牌，如果检验通过，就把用户模型中的confirmed属性设置为True
    def confirm(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data=s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm')!=self.id:
            return False
        self.confirmed=True
        # 仅仅add到数据库中，还没有commit提交
        db.session.add(self)
        return True

    def __repr__(self):
        return '<User %r>' %self.username

# 自定义的匿名用户类
class AnonymousUser(AnonymousUserMixin):
    def can(self,permissions):
        return False
    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser

# 对于flask-login来说是必备的函数
# login_manager.user_loader 装饰器把这个函数注册给 Flask-Login，在这个扩展需要获取已 登录用户的信息时调用。
@login_manager.user_loader
def load_user(user_id):
    # get方法返回对应主键所对应的一行
    return User.query.get(int(user_id))

# 定义权限常量
class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16

