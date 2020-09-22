# -*- coding: utf-8 -*-
# @Time    : 2020/8/28 20:48
# @Author  : SSK
# @FileName: models.py
# @Software: PyCharm
from . import db
from werkzeug.security import generate_password_hash,check_password_hash
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin,AnonymousUserMixin

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

    # 重写init方法，在用户创建时，判断电子邮件是否是管理员，如果是，直接赋予管理员角色，而不是普通User角色
    def __init__(self,**kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASK_ADMIN']:
                self.role=Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role=Role.query.filter_by(default=True).first()
    # 以下两个方法来检验用户是否具有某项权限
    def can(self,perm):
        # !!!在User类中调用Role中的方法# 从这里可以看到在Role模型中反向在User模型中定义的role属性在这里就派上了用场,role代表一个个的类实例
        return self.role is not None and self.role.has_permission(perm)
    def is_administrator(self):
        return self.can(Permission.ADMIN)

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

