# -*- coding: utf-8 -*-
# @Time    : 2020/8/28 20:48
# @Author  : SSK
# @FileName: __init__.py.py
# @Software: PyCharm
from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors
