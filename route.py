import os

from flask import request

import setting
from api import common_api, login_api, image_api
from tool import jwt_tool

# 接口路由，全部写在这里
import tool.common


def add_new_routes(app):
    # 全局异常捕获处理
    @app.errorhandler(Exception)
    def errorhandler(error):
        error = str(error)
        code = 400
        if error == '授权凭证无效':
            code = 401
        return tool.common.json_return(error, [], code)

    @app.before_first_request
    def before_first_request_instance():
        os.system('orator migrate -c orator_database.py -f')
        # orator组件sql日志驱动
        if setting.ENV == 'development':
            import logging
            logger = logging.getLogger('orator.connection.queries')
            logger.setLevel(logging.DEBUG)
            handler = logging.StreamHandler()
            logger.addHandler(handler)

    @app.before_request
    def before_request_instance():
        request.user_id = 0
        path = request.path.lower()
        if path.startswith('/api/auth'):
            token = request.headers.get('Authorization', '')
            if not token:
                token = tool.common.get_request_param(['token']).get('token', '')
            res = jwt_tool.jwt_decode(token)
            request.user_id = res['user_id']

    # 自定义路由
    app.add_url_rule('/api/test', view_func=common_api.test, methods=['POST', 'GET'])
    app.add_url_rule('/api/login', view_func=login_api.login, methods=['POST'])
    app.add_url_rule('/api/casLogin', view_func=login_api.casLogin, methods=['GET'])
    # 需要登录的接口
    app.add_url_rule('/api/auth/editPassword', view_func=login_api.editPassword, methods=['POST'])
    app.add_url_rule('/api/auth/getUserInfo', view_func=login_api.getUserInfo, methods=['POST'])
    # 图片相关
    app.add_url_rule('/api/image/upload', view_func=image_api.upload, methods=['POST'])
    app.add_url_rule('/api/image/search', view_func=image_api.search, methods=['POST'])
    app.add_url_rule('/api/image/list', view_func=image_api.list, methods=['GET'])
    app.add_url_rule('/api/image/delete', view_func=image_api.delete, methods=['POST'])
