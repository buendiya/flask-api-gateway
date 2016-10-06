# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import json

import redis

from api_gateway import settings
from api_gateway.gateway import app
from api_gateway.utils.sqlite_utils import get_db


users = [{"access_key": "public",
          "secret_key": "a5f45165bc1db7b4b32d98705f114a43247a63e0",
          },
         ]

routes = [{"name": "classify_color",
           "url": "http://www.bing.com/search",
           "netloc": "www.bing.com",
           "seconds": 60,
           "limits": 1
           },
          {"name": "post_test",
           "url": "http://127.0.0.1:8020/demo/car/",
           "netloc": "127.0.0.1",
           "seconds": 60,
           "limits": 1
           },
          {"name": "get_test",
           "url": "http://127.0.0.1:8020/demo/car/",
           "netloc": "127.0.0.1",
           "seconds": 60,
           "limits": 1
           },
          ]


user_routes = [{"route_name": "classify_color",
                "user_access_key": "public",
                "seconds": 60,
                "limits": 1
                },
               {"route_name": "post_test",
                "user_access_key": "public",
                "seconds": 60,
                "limits": 1
                },
               {"route_name": "get_test",
                "user_access_key": "public",
                "seconds": 60,
                "limits": 1
                },
               ]


def update_redis_config():
    client = redis.StrictRedis(
        host=settings.REDIS_HOST, port=settings.REDIS_PORT,
        db=settings.REDIS_DB, password=settings.REDIS_PASSWORD
    )

    client.set('users', json.dumps(users))
    client.set('routes', json.dumps(routes))


def init_db():
    cur_dir = os.path.dirname(__name__)
    with app.app_context():
        db = get_db()
        with open(os.path.join(cur_dir, 'api_gateway', 'schema.sql'), 'r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def update_user_table():
    with app.app_context():
        db = get_db()
        for user in users:
            cur = db.execute("SELECT * FROM user WHERE access_key = ?", (user['access_key'],))
            data = cur.fetchone()
            if data is None:
                db.execute('insert into user (access_key, secret_key) values (?, ?)',
                           [user['access_key'], user['secret_key']])
        db.commit()


def update_route_table():
    with app.app_context():
        db = get_db()
        for route in routes:
            cur = db.execute("SELECT * FROM route WHERE name = ?", (route['name'],))
            data = cur.fetchone()
            if data is None:
                db.execute('insert into route (name, url, netloc, seconds, limits) values (?, ?, ?, ?, ?)',
                           [route['name'], route['url'], route['netloc'], route['seconds'], route['limits']])
        db.commit()


def update_user_route_table():
    with app.app_context():
        db = get_db()
        for user_route in user_routes:
            cur = db.execute("SELECT * FROM user WHERE access_key = ?", (user_route['user_access_key'],))
            user = cur.fetchone()
            if user is None:
                continue

            cur = db.execute("SELECT * FROM route WHERE name = ?", (user_route['route_name'],))
            route = cur.fetchone()
            if route is None:
                continue

            cur = db.execute("SELECT * FROM user_route WHERE user_id = ? AND route_id = ?",
                             (user['id'], route['id']))
            data = cur.fetchone()
            if data is None:
                db.execute('insert into user_route (user_id, route_id, seconds, limits) values (?, ?, ?, ?)',
                           [user['id'], route['id'], user_route['seconds'], user_route['limits']])
        db.commit()


def update_sqlite_table():
    update_user_table()
    update_route_table()
    update_user_route_table()


if __name__ == '__main__':
    update_user_route_table()
