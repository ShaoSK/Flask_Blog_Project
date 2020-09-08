# -*- coding: utf-8 -*-
# @Time    : 2020/8/28 20:47
# @Author  : SSK
# @FileName: __init__.py.py
# @Software: PyCharm
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager
from flask_migrate import Migrate

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
# 当还没有登录的用户，也就是匿名用户尝试访问受保护的页面时，比如auth/logout，flask_login就会重定向到login登录页面
login_manager.login_view = 'auth.login'

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app,db)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint,url_prefix='/auth')

    return app