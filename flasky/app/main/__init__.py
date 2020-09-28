# -*- coding: utf-8 -*-
# @Time    : 2020/8/28 20:48
# @Author  : SSK
# @FileName: __init__.py.py
# @Software: PyCharm
from flask import Blueprint


main = Blueprint('main', __name__)

from . import views, errors


from ..models import Permission
## 上下文处理器，为了让权限能在所有模板中访问，而且不需要在每次render_template，都添加一个权限参数，
# 这里使用一个上下文处理器的装饰器，在渲染时，这个装饰器能让所有模板都能访问到Permission变量
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
