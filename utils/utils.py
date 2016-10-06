# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement

import sys

from future.utils import iteritems


# Aliases for types that are spelled differently in different Python
# versions. bytes_type is deprecated and no longer used in Tornado
# itself but is left in case anyone outside Tornado is using it.
PY3 = sys.version_info >= (3,)
bytes_type = bytes
if PY3:
    unicode_type = str
    basestring_type = str
    text_type = str
else:
    # The names unicode and basestring don't exist in py3 so silence flake8.
    unicode_type = unicode  # noqa
    basestring_type = basestring  # noqa
    text_type = unicode


_UTF8_TYPES = (bytes, type(None))


def utf8(value):
    # type: (typing.Union[bytes,unicode_type,None])->typing.Union[bytes,None]
    """Converts a string argument to a byte string.

    If the argument is already a byte string or None, it is returned unchanged.
    Otherwise it must be a unicode string and is encoded as utf8.
    """
    if isinstance(value, _UTF8_TYPES):
        return value
    if not isinstance(value, unicode_type):
        raise TypeError(
            "Expected bytes, unicode, or None; got %r" % type(value)
        )
    return value.encode("utf-8")


_TO_UNICODE_TYPES = (unicode_type, type(None))


def unicode_encoded_dict(in_dict):
    """
    使用 unicode 重新编码字典
    :param in_dict:
    :return:
    """
    out_dict = {}
    for k, v in in_dict.items():
        out_dict[to_unicode(k)] = to_unicode(v)
    return out_dict


_TO_UNICODE_TYPES = (unicode_type, type(None))


def to_unicode(value):
    """Converts a string argument to a unicode string.

    If the argument is already a unicode string or None, it is returned
    unchanged.  Otherwise it must be a byte string and is decoded as utf8.
    """
    if isinstance(value, _TO_UNICODE_TYPES):
        return value
    if not isinstance(value, bytes):
        raise TypeError(
            "Expected bytes, unicode, or None; got %r" % type(value)
        )
    return value.decode("utf-8")


def utf8_encoded_dict(in_dict):
    """
    使用 utf-8 重新编码字典
    :param in_dict:
    :return:
    """
    out_dict = {}
    for k, v in iteritems(in_dict):
        out_dict[utf8(k)] = utf8(v)
    return out_dict
