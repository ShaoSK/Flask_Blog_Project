# -*- coding: utf-8 -*-
# @Time    : 2020/8/29 11:15
# @Author  : SSK
# @FileName: forms.py
# @Software: PyCharm
from flask_wtf import FlaskForm
from wtforms import SubmitField,StringField,PasswordField,BooleanField
from wtforms.validators import DataRequired,Length,Email


class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Length(1,64),Email()])

    password = PasswordField('Password',validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Login in')
