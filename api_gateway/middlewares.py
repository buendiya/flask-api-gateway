# -*- coding: utf-8 -*-
import json
import time

from flask import request, g, abort

from api_gateway.utils.redis_helper import RedisHelper
from api_gateway.utils.sign_request import ServerSignRequestHandler, SignRequestException
from api_gateway.utils.sqlite_utils import get_route as get_route_from_sqlite, get_user, get_user_route
import settings


def check_signature():
    if 'X-Api-Access-Key' not in request.headers:
        abort(400, 'X-Api-Access-Key not found in headers')
    access_key = request.headers['X-Api-Access-Key']
    user = get_user(access_key)
    if not user:
        abort(400, 'Access Key not exist')
    g.user = user
    sign_request_handler = ServerSignRequestHandler(user['secret_key'],
                                                    settings.SIGNATURE_EXPIRE_SECONDS,
                                                    request.headers,
                                                    request.method,
                                                    request.full_path.strip('?'),
                                                    request.get_data())
    try:
        sign_request_handler.check_signature()
    except SignRequestException, e:
        return abort(400, e.message)


def get_route():
    route = get_route_from_sqlite(request.path)
    if not route:
        abort(404)
    g.route = route


def get_user_record_name():
    return '_'.join(['user_request_record', str(g.user['id']), str(g.route['id'])])


def get_api_record_name():
    return '_'.join(['api_request_record', str(g.route['id'])])


def check_request_limit():
    redis_client = RedisHelper.get_client()

    user_route = get_user_route(g.user['id'], g.route['id'])
    user_record_name = get_user_record_name()
    if user_route and user_route['limits'] and user_route['seconds'] and redis_client.get(user_record_name):
        user_record = json.loads(redis_client.get(user_record_name))
        if len(user_record) == user_route['limits'] and int(time.time()) - user_record[-1] < user_route['seconds']:
            abort(400, 'Limit Exceeded Exception for access_key %s, api %s' % (g.user['access_key'], g.route['path']))

    api_record_name = get_api_record_name()
    if g.route['limits'] and g.route['seconds'] and redis_client.get(api_record_name):
        api_record = json.loads(redis_client.get(api_record_name))
        if len(api_record) == g.route['limits'] and int(time.time()) - api_record[-1] < g.route['seconds']:
            abort(400, 'Limit Exceeded Exception for api %s' % g.route['path'])


def record_request(response):
    if response.status_code >= 400:
        return response
    redis_client = RedisHelper.get_client()

    user_record_name = get_user_record_name()
    user_record = json.loads(redis_client.get(user_record_name)) if redis_client.get(user_record_name) else []
    user_record.insert(0, int(time.time()))
    user_route = get_user_route(g.user['id'], g.route['id'])
    if user_route and user_route['limits'] and len(user_record) > user_route['limits']:
        user_record = user_record[:user_route['limits']]
    redis_client.set(user_record_name, json.dumps(user_record))

    api_record_name = get_api_record_name()
    api_record = json.loads(redis_client.get(api_record_name)) if redis_client.get(api_record_name) else []
    api_record.insert(0, int(time.time()))
    if g.route['limits'] and len(api_record) > g.route['limits']:
        api_record = api_record[:g.route['limits']]
    redis_client.set(api_record_name, json.dumps(api_record))

    return response
