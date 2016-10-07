#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import json

import redis

from api_gateway import settings

__all__ = ['RedisHelper']


class RedisHelper(object):
    """
    redis 连接助手
    """
    _client = None

    def __init__(self):
        if RedisHelper._client is None:
            self._create_redis_client()

    @classmethod
    def get_client(cls):
        if RedisHelper._client is None:
            cls._create_redis_client()
        return RedisHelper._client

    @classmethod
    def ping_redis(cls):
        """
        测试redis能否连通
        :return:
        """
        cls.get_client().ping()

    @classmethod
    def _create_redis_client(cls):
        """
        创建连接
        :return:
        """
        RedisHelper._client = redis.StrictRedis(
            host=settings.REDIS_HOST, port=settings.REDIS_PORT,
            db=settings.REDIS_DB, password=settings.REDIS_PASSWORD)

    @classmethod
    def get_route(cls, path):
        redis_client = cls.get_client()
        routes = json.loads(redis_client.get('routes'))
        for route in routes:
            if route['path'] == path:
                return route

    @classmethod
    def get_user(cls, access_key):
        users = json.loads(cls.get_client().get('users'))
        for user in users:
            if user['access_key'] == access_key:
                return user
