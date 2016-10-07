# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import logging.config
import os

# 当前目录所在路径
BASE_PATH = os.path.abspath(os.path.dirname(__file__))

DEBUG = True

# 访问签名的有效时间,秒
SIGNATURE_EXPIRE_SECONDS = 3600


CHUNK_SIZE = 1024

FLASK_CONFIG = {'DEBUG': DEBUG,
                }

DATABASE_PATH = os.path.join(BASE_PATH, 'api_gateway.db')

# Redis 配置
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = ''


# 可以给日志对象设置日志级别，低于该级别的日志消息将会被忽略
# CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
LOGGING_LEVEL = 'DEBUG' if DEBUG else 'INFO'


LOG_PATH = os.path.join(BASE_PATH, 'logs')
if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH)


def update_configuration():
    try:
        from . import CONFIGS as _configs
    except ImportError:
        return
    global_variables = globals()
    for setting in dir(_configs):
        if setting == setting.upper():
            setting_value = getattr(_configs, setting)
            global_variables[setting] = setting_value

update_configuration()


logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%Y-%m-%d %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            # 当达到10MB时分割日志
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 50,
            # If delay is true,
            # then file opening is deferred until the first call to emit().
            'delay': True,
            'filename': os.path.join(LOG_PATH, 'server.log'),
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'common.logger': {
            'handlers': ['console', 'file'],
            'level': LOGGING_LEVEL,
        },
    }
})
