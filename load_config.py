# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import json

import redis

import settings


app_keys = [{"access_key": "public",
             "secret_key": "a5f45165bc1db7b4b32d98705f114a43247a63e0",
             },
            ]

routes = [{"name": "classify_color",
           "url": "http://www.bing.com/search",
           "netloc": "www.bing.com",
           },
          {"name": "post_test",
           "url": "http://127.0.0.1:8020/demo/car/",
           "netloc": "127.0.0.1",
           },
          {"name": "get_test",
           "url": "http://127.0.0.1:8020/demo/car/",
           "netloc": "127.0.0.1",
           },
          ]


def update_config():
    client = redis.StrictRedis(
        host=settings.REDIS_HOST, port=settings.REDIS_PORT,
        db=settings.REDIS_DB, password=settings.REDIS_PASSWORD
    )

    client.set('app_keys', json.dumps(app_keys))
    client.set('routes', json.dumps(routes))


if __name__ == '__main__':
    update_config()
