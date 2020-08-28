# -*- coding: utf-8 -*-
# @Time    : 2020/8/28 20:48
# @Author  : SSK
# @FileName: email.py
# @Software: PyCharm
from . import mail
from flask_mail import Message
from flask import current_app,render_template
from threading import Thread
from config import config
import os

# 多线程发送
def send_async_email(app,msg):
    with app.app_context():
        mail.send(msg)

def send_email(to,subject,template,**kwargs):
    # 获取当前正在运行的应用实例
    app = current_app._get_current_object()
    msg = Message(config[os.getenv('FLASK_CONFIG') or 'default'].FLASK_MAIL_SUBJECT_PREFIX+subject,sender=config[os.getenv('FLASK_CONFIG') or 'default'].FLASK_MAIL_SENDER,recipients=[to])
    msg.body = render_template(template+'.txt',**kwargs)
    msg.html = render_template(template+'.html',**kwargs)
    thr = Thread(target=send_async_email,args=[app,msg])
    thr.start()
    return thr