# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import hmac
import random
import time
from base64 import b64encode
from hashlib import sha256, sha1

from .utils import utf8, text_type, unicode_encoded_dict, to_unicode


class SignRequestException(Exception):
    """
    签名错误
    """


class BaseSignRequestHandler(object):
    def __init__(self, secret_key, host, headers, method, uri, body):
        """
        headers: dict
        """
        self.secret_key = secret_key
        self.host = host
        self.headers = headers
        self.method = method
        self.uri = uri
        self.body = body

    def get_signature(self):
        string_to_sign = self.string_to_sign()
        hash_value = sha1(utf8(string_to_sign)).hexdigest()
        return self.sign_string(hash_value)

    def sign_string(self, string_to_sign):
        new_hmac = hmac.new(utf8(self.secret_key), digestmod=sha256)
        new_hmac.update(utf8(string_to_sign))
        return to_unicode(b64encode(new_hmac.digest()).rstrip(b'\n'))

    def string_to_sign(self):
        """
        Return the canonical StringToSign as well as a dict
        containing the original version of all headers that
        were included in the StringToSign.
        """
        headers_to_sign = self.headers_to_sign()
        canonical_headers = self.canonical_headers(headers_to_sign)
        string_to_sign = b'\n'.join([utf8(self.method.upper()),
                                     utf8(self.uri),
                                     utf8(canonical_headers),
                                     utf8(self.body)])
        return string_to_sign

    def headers_to_sign(self):
        """
        Select the headers from the request that need to be included
        in the StringToSign.
        """
        headers_to_sign = {'Host': self.host}
        for name, value in self.headers.items():
            l_name = name.lower()
            # 计算签名的时候, 不能包含 x-api-signature
            if l_name.startswith('x-api-') and l_name != 'x-api-signature':
                headers_to_sign[name] = value
        return headers_to_sign

    def canonical_headers(self, headers_to_sign):
        """
        Return the headers that need to be included in the StringToSign
        in their canonical form by converting all header keys to lower
        case, sorting them in alphabetical order and then joining
        them into a string, separated by newlines.
        """
        headers_to_sign = unicode_encoded_dict(headers_to_sign)
        l = sorted(['%s: %s' % (n.lower().strip(),
                                headers_to_sign[n].strip()) for n in headers_to_sign])
        return '\n'.join(l)


class ClientSignRequestHandler(BaseSignRequestHandler):
    def __init__(self, access_key, secret_key, encrypt_type, host, headers, method, uri, body):
        """
        headers: dict
        """
        self.access_key = access_key
        self.encrypt_type = encrypt_type
        headers.update(self.get_auth_headers())
        super(ClientSignRequestHandler, self).__init__(secret_key, host, headers, method, uri, body)

    def get_auth_headers(self):
        headers = {
            'X-Api-Timestamp': text_type(int(time.time())),
            'X-Api-Nonce': text_type(random.random()),
            'X-Api-Access-Key': text_type(self.access_key),
            'X-Api-Encrypt-Type': text_type(self.encrypt_type)
        }
        return headers


class ServerSignRequestHandler(BaseSignRequestHandler):
    def __init__(self, secret_key, signature_expire_seconds, headers, method, uri, body):
        self.signature_expire_seconds = signature_expire_seconds
        host = headers.get('Host')
        super(ServerSignRequestHandler, self).__init__(secret_key, host, headers, method, uri, body)

    def check_signature(self):
        try:
            timestamp = int(self.headers.get('X-Api-Timestamp'))
        except ValueError:
            raise SignRequestException('Invalid X-Api-Timestamp Header')

        now_ts = int(time.time())
        if abs(timestamp - now_ts) > self.signature_expire_seconds:
            raise SignRequestException('Expired Signature')

        signature = to_unicode(self.headers.get('X-Api-Signature'))
        if not signature:
            raise SignRequestException('No Signature Provided')

        real_signature = self.get_signature()
        if signature != real_signature:
            raise SignRequestException('Invalid Signature')
