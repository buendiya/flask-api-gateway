# -*- coding: utf-8 -*-
from __future__ import absolute_import

from api_gateway.gateway import app
from api_gateway.utils.sqlite_utils import get_db


users = [{"access_key": "public",
          "secret_key": "a5f45165bc1db7b4b32d98705f114a43247a63e0",
          },
         ]

routes = [{"path": "/classify/color/",
           "url": "http://www.bing.com/search",
           "netloc": "www.bing.com",
           "seconds": 60,
           "limits": 1
           },
          {"path": "/post/test/",
           "url": "http://127.0.0.1:8020/demo/car/",
           "netloc": "127.0.0.1",
           "seconds": 60,
           "limits": 1
           },
          {"path": "/get/test/",
           "url": "http://127.0.0.1:8020/demo/car/",
           "netloc": "127.0.0.1",
           "seconds": 60,
           "limits": 1
           },
          ]


user_routes = [{"route_path": "/classify/color/",
                "user_access_key": "public",
                "seconds": 60,
                "limits": 1
                },
               {"route_path": "/post/test/",
                "user_access_key": "public",
                "seconds": 60,
                "limits": 1
                },
               {"route_path": "/get/test/",
                "user_access_key": "public",
                "seconds": 60,
                "limits": 1
                },
               ]


def load_user_table():
    with app.app_context():
        db = get_db()
        for user in users:
            cur = db.execute("SELECT * FROM user WHERE access_key = ?", (user['access_key'],))
            data = cur.fetchone()
            if data is None:
                db.execute('insert into user (access_key, secret_key) values (?, ?)',
                           [user['access_key'], user['secret_key']])
        db.commit()


def load_route_table():
    with app.app_context():
        db = get_db()
        for route in routes:
            cur = db.execute("SELECT * FROM route WHERE path = ?", (route['path'],))
            data = cur.fetchone()
            if data is None:
                db.execute('insert into route (path, url, netloc, seconds, limits) values (?, ?, ?, ?, ?)',
                           [route['path'], route['url'], route['netloc'], route['seconds'], route['limits']])
        db.commit()


def load_user_route_table():
    with app.app_context():
        db = get_db()
        for user_route in user_routes:
            cur = db.execute("SELECT * FROM user WHERE access_key = ?", (user_route['user_access_key'],))
            user = cur.fetchone()
            if user is None:
                continue

            cur = db.execute("SELECT * FROM route WHERE path = ?", (user_route['route_path'],))
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


def load_sqlite_table():
    load_user_table()
    load_route_table()
    load_user_route_table()


if __name__ == '__main__':
    load_sqlite_table()()
