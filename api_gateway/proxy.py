# -*- coding: utf-8 -*-
import logging

import requests
from flask import request, Response, g, Blueprint
from flask.views import MethodView

from api_gateway.utils.utils import text_type
from api_gateway.middlewares import check_signature, get_route, check_request_limit, record_request
import settings


proxy_blueprint = Blueprint('proxy', __name__)


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
proxy_blueprint.before_request(check_signature)
proxy_blueprint.before_request(get_route)
proxy_blueprint.before_request(check_request_limit)
proxy_blueprint.after_request(record_request)
