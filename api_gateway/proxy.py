# -*- coding: utf-8 -*-
import json
import time
import logging

import requests
from flask import request, Response, g, Blueprint, abort
from flask.views import MethodView

from api_gateway.utils.redis_helper import RedisHelper
from api_gateway.utils.sign_request import ServerSignRequestHandler, SignRequestException
from api_gateway.utils.sqlite_utils import get_route as get_route_from_sqlite, get_user, get_user_route
from api_gateway.utils.utils import text_type
import settings


proxy_blueprint = Blueprint('proxy', __name__)


@proxy_blueprint.before_request
def check_signature():
    if 'X-Api-Access-Key' not in request.headers:
        abort(400, 'X-Api-Access-Key not found in headers')
    access_key = request.headers['X-Api-Access-Key']
    user = get_user(access_key)
    if not user:
        abort(400, 'Access key is invalid')
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


@proxy_blueprint.before_request
def get_route():
    if not request.view_args:
        abort(404)
    route = get_route_from_sqlite(request.path)
    if not route:
        abort(404)
    g.route = route


def get_user_record_name():
    return '_'.join(['user_request_record', str(g.user['id']), str(g.route['id'])])


def get_api_record_name():
    return '_'.join(['api_request_record', str(g.route['id'])])


@proxy_blueprint.before_request
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


@proxy_blueprint.after_request
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


class ProxyMethodView(MethodView):

    def get(self, path):
        url = g.route['url']
        headers = self._clean_request_headers()
        raw_response = requests.get(url, stream=True, params=request.args, headers=headers)
        return self._get_response(raw_response)

    def post(self, path):
        url = g.route['url']
        headers = self._clean_request_headers()
        raw_response = requests.post(url, stream=True, data=request.get_data(), headers=headers)
        return self._get_response(raw_response)

    def _get_response(self, raw_response):
        def generate():
            for chunk in raw_response.iter_content(settings.CHUNK_SIZE):
                yield chunk
        response = Response(generate())
        self._set_response_headers(response, raw_response.headers)
        return response

    def _clean_request_headers(self):
        """
        清理headers中不需要的部分，以及替换值
        :return:
        """
        headers = request.headers
        new_headers = {}
        # 如果 header 有的是 str，有的是 unicode
        # 会出现 422 错误
        for name, value in headers.items():
            # 过滤 x-api 开头的, 这些只是发给 api-gateway
            l_name = name.lower()
            # 这些 headers 需要传递给后端
            required_headers = ['x-api-user-json', 'x-api-access-key']
            if l_name.startswith('x-api-') and l_name not in required_headers:
                pass
            # 不需要提供 Content-Length, 自动计算
            # 如果 Content-Length 不正确, 请求后端网站会出错,
            # 太大会出现超时问题, 太小会出现内容被截断
            elif l_name == 'content-length':
                pass
            else:
                new_headers[text_type(name)] = text_type(value)

        # 更新host字段为后端访问网站的host
        new_headers['Host'] = g.route['netloc']
        return new_headers

    def _set_response_headers(self, response, raw_headers):
            for (k, v) in raw_headers.items():
                if k == 'Server' or k == 'X-Powered-By':
                    # 隐藏后端网站真实服务器名称
                    pass
                elif k == 'Transfer-Encoding' and v.lower() == 'chunked':
                    # 如果设置了分块传输编码，但是实际上代理这边已经完整接收数据
                    # 到了浏览器端会导致(failed)net::ERR_INVALID_CHUNKED_ENCODING
                    pass
                # elif k == 'Location':
                #     # API不存在301, 302跳转, 过滤Location
                #     pass
                elif k == 'Content-Length':
                    # 代理传输过程如果采用了压缩，会导致remote传递过来的content-length与实际大小不符
                    # 会导致后面self.write(response.body)出现错误
                    # 可以不设置remote headers的content-length
                    # "Tried to write more data than Content-Length")
                    # HTTPOutputError: Tried to write more data than Content-Length
                    pass
                elif k == 'Content-Encoding':
                    # 采用什么编码传给请求的客户端是由Server所在的HTTP服务器处理的
                    pass
                elif k == 'Set-Cookie':
                    # Set-Cookie是可以有多个，需要一个个添加，不能覆盖掉旧的
                    # 理论上不存在 Set-Cookie,可以过滤
                    response.headers.add(k, v)
                else:
                    response.headers.set(k, v)


proxy_blueprint.add_url_rule('/<path:path>', view_func=ProxyMethodView.as_view('proxy'), methods=['GET', 'POST'])
