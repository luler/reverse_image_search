# 控制请求频率
import time

from flask import request

from tool import common


def handle(minute=1, limit=60):
    def wrapper(func):
        def inside(*args, **kwargs):
            ############################
            # 中间件动作开始
            ############################
            key = 'throttle:' + common.get_client_ip() + ':' + request.path.lower()
            res = common.cache().get(key, [])
            now_time = int(time.time())
            start_time = now_time - minute * 60
            res = [e for e in res if e > start_time]
            res.append(now_time)
            if len(res) > limit:
                raise Exception('请求频率超出限制')
            common.cache().set(key, res, expire=minute * 60)
            ############################
            # 中间件动作结束
            ############################
            return func(*args, **kwargs)

        return inside

    return wrapper
