# -*- coding: utf-8 -*-
# @Time    : 2020/9/26 11:34
# @Author  : SSK
# @FileName: fake.py
# @Software: PyCharm
# 为了测试分页，需要生成虚拟用户和文章

from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .models import User,Post

def users(count=100):
    fake = Faker()
    i = 0
    while i<count:
        u = User(email=fake.email(),username=fake.user_name(),password='password',confirmed=True,name=fake.name(),
                 location=fake.city(),about_me=fake.text(),member_since=fake.past_date()
                 )
        db.session.add(u)
        try:
            db.session.commit()
            i+=1
        except IntegrityError:
            db.session.rollback()

def posts(count=100):
    fake = Faker()
    user_cout = User.query.count()
    for i in range(count):
        # 为每一篇文章随机指定一个用户，使用offset查询过滤器
        u = User.query.offset(randint(0,user_cout-1)).first()
        p = Post(body=fake.text(),timestamp=fake.past_date(),author=u)
        db.session.add(p)
    db.session.commit()








