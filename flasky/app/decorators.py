# -*- coding: utf-8 -*-
# @Time    : 2020/9/20 21:06
# @Author  : SSK
# @FileName: decorators.py
# @Software: PyCharm
# 自定义装饰器，让视图函数只对具有特定权限的用户开放

from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission

# 自定义可以传参的装饰器，permission为传递的参数
def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args,**kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args,**kwargs)
        return decorated_function
    # 返回一个已经包裹好的装饰器
    return decorator

def admin_required(f):
    return permission_required(Permission.ADMIN)(f)
