# -*- coding: utf-8 -*-
from flask import Flask, g

from api_gateway import settings
from api_gateway.proxy import proxy_blueprint

app = Flask(__name__)
app.config.update(settings.FLASK_CONFIG)
app.register_blueprint(proxy_blueprint)


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

if __name__ == '__main__':
    app.run()
