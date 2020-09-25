# -*- coding: utf-8 -*-
# @Time    : 2020/8/28 21:13
# @Author  : SSK
# @FileName: Blog.py
# @Software: PyCharm

import os
from app import create_app, db
from app.models import User, Role

# 创建应用实例
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# 使用flask shell时，不用再设置导入数据库
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)

if __name__ == '__main__':
    app.run()
