# -*- coding: utf-8 -*-
import os

from api_gateway.gateway import app
from api_gateway.utils.sqlite_utils import get_db


def init_db():
    cur_dir = os.path.dirname(__name__)
    with app.app_context():
        db = get_db()
        with open(os.path.join(cur_dir, 'api_gateway', 'schema.sql'), 'r') as f:
            db.cursor().executescript(f.read())
        db.commit()

if __name__ == '__main__':
    init_db()
