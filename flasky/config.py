# -*- coding: utf-8 -*-
# @Time    : 2020/8/26 10:52
# @Author  : SSK
# @FileName: config.py
# @Software: PyCharm

import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    ## Flask-WTF无需在应用层初始化，但要求配置一个密钥，SECRET_KEY
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess'
    ## !!!!!!!!!这里写错过一次！，将MAIL_SERVER写成了MAILN_SERVER
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT','587'))
    MAIL_USE_TLS = os.environ.get('MAIN_USE_TLS','true').lower() in ['true','on','1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    # 分页配置，每一页展示多少博客数量
    FLASKY_POSTS_PER_PAGE = 20
    FLASKY_FOLLOWERS_PER_PAGE = 50
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASK_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASK_MAIL_SENDER = '1165850025@qq.com'
    FLASK_MAIL_ADMIN = os.environ.get('FLASK_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ADMIN = os.environ.get('FLASK_ADMIN')
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI') or 'sqlite:///'+os.path.join(basedir,'data.sqlite')

class TestingConfig(Config):
    TESTING =True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URI') or 'sqlite"//'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or 'sqlite:///'+os.path.join(basedir,'data-pro.sqlite')

config = {
    'development':DevelopmentConfig,
    'testing':TestingConfig,
    'production':ProductionConfig,
    'default':DevelopmentConfig
}