# -*- coding: utf-8 -*-
from sqlite3 import dbapi2 as sqlite3

from flask import g
from api_gateway import settings


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(settings.DATABASE_PATH)
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def get_route(route_name):
    db = get_db()
    cur = db.execute("SELECT * FROM route WHERE name = ?", (route_name,))
    return cur.fetchone()


def get_user(access_key):
    db = get_db()
    cur = db.execute("SELECT * FROM user WHERE access_key = ?", (access_key,))
    return cur.fetchone()


def get_user_route(user_id, route_id):
    db = get_db()
    cur = db.execute("SELECT * FROM user_route WHERE user_id = ? AND route_id = ?",
                     (user_id, route_id))
    return cur.fetchone()
