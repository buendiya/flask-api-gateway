#!/usr/bin/env python
# -*- coding: utf-8 -*-
# created by restran on 2015/12/19

from __future__ import unicode_literals, absolute_import

import logging.config
import os

# 当前目录所在路径
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
# 日志所在目录
LOG_PATH = os.path.join(BASE_PATH, 'logs')

DEBUG = True

# 未通过网关鉴权, 或者未能正确请求时返回的状态码
# 通过特殊的状态码, 区分后端 API Server 返回的状态码
GATEWAY_ERROR_STATUS_CODE = 600

# 可以给日志对象设置日志级别，低于该级别的日志消息将会被忽略
# CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
LOGGING_LEVEL = 'DEBUG' if DEBUG else 'INFO'
LOGGING_HANDLERS = ['console'] if DEBUG else ['file']


# 访问签名的有效时间,秒
SIGNATURE_EXPIRE_SECONDS = 3600


CHUNK_SIZE = 1024

if not os.path.exists(LOG_PATH):
    # 创建日志文件夹
    os.makedirs(LOG_PATH)

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': True,
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
        '': {
            'handlers': LOGGING_HANDLERS,
            'level': LOGGING_LEVEL,
        },
    }
})

if os.path.exists(os.path.join(BASE_PATH, 'CONFIGS.py')):
    from api_gateway.CONFIGS import *
