# flask变量
# ENV = 'production'
import orator_database

ENV = 'development'

HOST = '0.0.0.0'
PORT = 5000
THREADED = True
PROCESSES = 1

# 数据库配置
DATABASES = orator_database.DATABASES

# jwt配置
JWT_SECRET = 'vIu#wJ%8'
JWT_EXPIRE = 7200

# 初始化账号密码
ADMIN_NAME = 'admin'
ADMIN_PASSWORD = 'admin'

# CAS配置
CAS_CONFIG = {
    'host': '',
    'appid': '',
    'appsecret': '',
}

# milvus配置
MILVUS = {
    'host': 'standalone',
    'port': 19530,
    'collection_name': 'reverse_image_search',
}
