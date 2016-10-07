# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import os
import json as json_util
import logging

import requests
from future.moves.urllib.parse import urlparse, urlunparse, urlencode

from api_gateway.utils.utils import utf8
from api_gateway.utils.sign_request import ClientSignRequestHandler

logger = logging.getLogger(__name__)


class RequestData(object):
    """
    请求的数据对象的封装
    """

    def __init__(self, method=None, path=None, headers=None, body=None, host=None):
        self.method = method
        self.path = path
        self.headers = headers
        self.body = body
        self.host = host


class APIRequest(object):
    def __init__(self, access_key, secret_key, api_gateway, encrypt_type='raw'):
        self.access_key = access_key
        self.secret_key = secret_key
        self.api_gateway = api_gateway
        self.encrypt_type = encrypt_type
        self.request_data = RequestData()

    def get_merged_path(self, path, params):
        path_parsed = urlparse(path)
        enc_params = urlencode(params) if params else None
        if path_parsed.query == '' or path_parsed.query is None:
            query = enc_params
        elif enc_params == '' or enc_params is None:
            query = path_parsed.query
        else:
            query = '%s&%s' % (path_parsed.query, enc_params)
        return urlunparse(('', '', path_parsed.path, path_parsed.params,
                           query, path_parsed.fragment))

    def prepare_request(self, method, path, params=None, headers=None, data=None, json=None):
        method = method.upper()

        self.request_data.host = urlparse(self.api_gateway).netloc
        self.request_data.path = self.get_merged_path(path, params)
        self.request_data.method = method
        self.request_data.headers = {
            'Accept': 'application/json; charset=utf-8'
        }
        if headers is not None:
            # headers 是字典
            self.request_data.headers.update(headers)

        if method == 'GET':
            self.request_data.body = ''
        else:
            if json is not None:
                self.request_data.headers['Content-Type'] = 'application/json; charset=utf-8'
                self.request_data.body = json_util.dumps(json, ensure_ascii=False)
            else:
                self.request_data.body = data

    def get(self, path, params=None, headers=None, **kwargs):
        self.prepare_request('GET', path, params=params, headers=headers)

        client_sign_request_handler = ClientSignRequestHandler(self.access_key,
                                                               self.secret_key,
                                                               self.encrypt_type,
                                                               self.request_data.host,
                                                               self.request_data.headers,
                                                               self.request_data.method,
                                                               self.request_data.path,
                                                               self.request_data.body)
        signature = client_sign_request_handler.get_signature()
        self.request_data.headers['X-Api-Signature'] = signature

        r = requests.get(self.api_gateway + path, params=params, headers=self.request_data.headers, **kwargs)
        logger.debug(r.status_code)

        return r

    def post(self, path, data=None, json=None, params=None, headers=None, **kwargs):
        self.prepare_request('POST', path, params=params, data=data, json=json, headers=headers)

        client_sign_request_handler = ClientSignRequestHandler(self.access_key,
                                                               self.secret_key,
                                                               self.encrypt_type,
                                                               self.request_data.host,
                                                               self.request_data.headers,
                                                               self.request_data.method,
                                                               self.request_data.path,
                                                               self.request_data.body)
        signature = client_sign_request_handler.get_signature()
        self.request_data.headers['X-Api-Signature'] = signature

        r = requests.post(self.api_gateway + path, headers=self.request_data.headers,
                          data=utf8(self.request_data.body), **kwargs)
        return r


if __name__ == '__main__':
    access_key = 'public'
    secret_key = 'a5f45165bc1db7b4b32d98705f114a43247a63e0'
    api_gateway = 'http://127.0.0.1:5000'
    request = APIRequest(access_key, secret_key, api_gateway)

    def test1():
        r = request.get('/classify/color/?q=hello', params={'first': 20})
        home_directory = os.path.expanduser('~')
        with open(os.path.join(home_directory, 'test.html'), 'w') as f:
            f.write(r.content)
        print r.status_code
        if r.status_code != 200:
            print r.content

    def test2():
        r = request.get('/get/test/', params={'pk': 1})
        print(r.content)

    def test3():
        r = request.post('/post/test/',
                         data=json_util.dumps({'name': 'from_api_gateway_post', 'price': 200}),
                         headers={'Content-Type': 'application/json'})
        print(r.content)

    test1()
