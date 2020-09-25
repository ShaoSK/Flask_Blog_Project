# -*- coding: utf-8 -*-
# @Time    : 2020/8/28 20:54
# @Author  : SSK
# @FileName: forms.py
# @Software: PyCharm
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,TextAreaField,BooleanField,SelectField
from wtforms.validators import DataRequired,Length,Email,Regexp
from ..models import Role,User
from wtforms import ValidationError

class NameForm(FlaskForm):
    name = StringField('What is your name?',validators=[DataRequired()])
    submit = SubmitField('Submit')

# 普通用户资料编辑表单
class EditProfileForm(FlaskForm):
    name = StringField('Real name',validators=[Length(0,64)])
    location = StringField('Your location',validators=[Length(0,64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

# 管理员更新资料表单
class EditProfileAdminForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Length(1,64),Email()])
    # 正则表达式！！！！！！！
    username = StringField('Username',validators=[DataRequired(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,
                                                                                     'Username must have only letters,numbers,dots or '
                                                                                     'underscores')])
    confirmed = BooleanField('Confirmed')
    # 下拉列表
    role = SelectField('Role',coerce=int)
    name = StringField('Real name',validators=[Length(0,64)])
    location = StringField('Your Location',validators=[Length(0,64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self,user,*args,**kwargs):
        super(EditProfileAdminForm,self).__init__(*args,**kwargs)
        self.role.choices = [(role.id,role.name) for role in Role.query.order_by(Role.name).all()]
        # 接收用户对象，调用后面的验证函数时使用
        self.user = user

    # 检验字段的值是否发生变化，仅当发生变化时才要保证新值不与数据库中已存在的值发生冲突
    def validate_email(self,field):
        if field.data !=self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self,filed):
        if filed.data!=self.user.username and User.query.filter_by(username=filed.data).first():
            raise ValidationError('Username already in use')