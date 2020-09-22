# -*- coding: utf-8 -*-
# @Time    : 2020/8/28 20:48
# @Author  : SSK
# @FileName: __init__.py.py
# @Software: PyCharm
from flask import Blueprint


main = Blueprint('main', __name__)

from . import views, errors


from ..models import Permission
## !!!上下文处理器？
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
