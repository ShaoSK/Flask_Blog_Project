# -*- coding: utf-8 -*-
# @Time    : 2020/8/28 20:54
# @Author  : SSK
# @FileName: forms.py
# @Software: PyCharm
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired

class NameForm(FlaskForm):
    name = StringField('What is your name?',validators=[DataRequired()])
    submit = SubmitField('Submit')