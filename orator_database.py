# orator数据迁移配置文件
DATABASES = {
    'default': 'sqlite',
    'mysql': {
        'driver': 'mysql',
        'host': '10.10.11.99',
        'database': 'test',
        'user': 'root',
        'password': 'root',
        'prefix': '',
        'log_queries': False,
    },
    'sqlite': {
        'driver': 'sqlite',
        'database': 'reverse_image_search.sqlite',
        'prefix': '',
        'log_queries': True,
    }
}
