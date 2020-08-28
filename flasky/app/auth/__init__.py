# -*- coding: utf-8 -*-
# @Time    : 2020/8/29 10:45
# @Author  : SSK
# @FileName: __init__.py.py
# @Software: PyCharm
from flask import Blueprint

auth = Blueprint('auth',__name__)

from . import views
