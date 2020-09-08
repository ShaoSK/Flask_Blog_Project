# -*- coding: utf-8 -*-
# @Time    : 2020/8/29 11:15
# @Author  : SSK
# @FileName: forms.py
# @Software: PyCharm
from flask_wtf import FlaskForm
from wtforms import SubmitField,StringField,PasswordField,BooleanField
from wtforms.validators import DataRequired,Length,Email,Regexp,EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Length(1,64),Email()])

    password = PasswordField('Password',validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Login in')

class RegisterationForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Length(1,64),Email()])

    username = StringField('Username',validators=[
        DataRequired(),Length(1,64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,'Usernames must have only letters,numbers,dots or underscores')])
    password = PasswordField('Password',validators=[DataRequired(),EqualTo('password2',message='Password must match.')])
    password2 = PasswordField('Confirm password',validators=[DataRequired()])
    submit = SubmitField('Register')

    ## 自定义的验证函数
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email has already registered.')

    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username has already in use.')
