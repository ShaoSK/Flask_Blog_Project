# -*- coding: utf-8 -*-
# @Time    : 2020/8/28 20:51
# @Author  : SSK
# @FileName: views.py
# @Software: PyCharm

from datetime import datetime
from flask import render_template, session, redirect, url_for
from . import main
from .forms import NameForm
from .. import db
from app.models import User
from app.email import send_email
from config import config
import os
from flask import current_app

@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            if current_app.config['FLASK_MAIL_ADMIN']:
                send_email(current_app.config['FLASK_MAIL_ADMIN'], 'New User', 'mail/new_user', user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''

        return redirect(url_for('.index'))
    return render_template('index.html',form=form,known=session.get('known', False),current_time=datetime.utcnow())

