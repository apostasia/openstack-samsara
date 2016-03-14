# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from __future__ import division
from datetime import datetime
from datetime import timedelta

import collections

import json
import time


def usage_percent(used, total, _round=None):
    """Calculate percentage usage of 'used' against 'total'."""
    try:
        ret = (used / total) * 100
    except ZeroDivisionError:
        ret = 0.0 if isinstance(used, float) or isinstance(total, float) else 0
    if _round is not None:
        return round(ret, _round)
    else:
        return ret

def to_percentage(value, total):
    """ Calculate a percentual of value.
    Args:
        value (float): Value to percentual calculate
        total (float): Referencial max value
    Returns:
        percentage value between 0 and 1
    """
    try:
        if value >= total:
            value = total

        percentage = ((float(value*100) / float(total)) / 100)
        return float(percentage)

    except ZeroDivisionError:
        return None

def get_time_from_period(period=60):
    """ Get the time moment from period ago
    Args:
        period (int): Period value in seconds.
    Returns:
        timestamp in UTC format
    """
    time = datetime.utcnow() - timedelta(seconds=period)
    return time.isoformat()

def get_period_from_time(t0, t1):
    """ Get the period from  times
    Args:
        t0 (string ): string in ISO 8601 format
        t1 (string ): string in ISO 8601 format
    Returns:
        period in seconds
    """
    time_0 = datetime.strptime(t0,'%Y-%m-%dT%H:%M:%S.%f')
    time_1 = datetime.strptime(t1,'%Y-%m-%dT%H:%M:%S.%f')

    period = time_1 - time_0

    return (period).seconds



# def json_load_byteified(file_handle):
#     return _byteify(
#         json.load(file_handle, object_hook=_byteify),
#         ignore_dicts=True
#     )
#
# def json_loads_byteified(json_text):
#     return _byteify(
#         json.loads(json_text, object_hook=_byteify),
#         ignore_dicts=True
#     )
#
# def _byteify(data, ignore_dicts = False):
#     # if this is a unicode string, return its string representation
#     if isinstance(data, unicode):
#         return data.encode('utf-8')
#     # if this is a list of values, return list of byteified values
#     if isinstance(data, list):
#         return [ _byteify(item, ignore_dicts=True) for item in data ]
#     # if this is a dictionary, return dictionary of byteified keys and values
#     # but only if we haven't already byteified it
#     if isinstance(data, dict) and not ignore_dicts:
#         return {
#             _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
#             for key, value in data.iteritems()
#         }
#     # if it's anything else, return it in its original form
#     return data


# def decode_list(data):
#     rv = []
#     for item in data:
#         if isinstance(item, unicode):
#             item = item.encode('utf-8')
#         elif isinstance(item, list):
#             item = decode_list(item)
#         elif isinstance(item, dict):
#             item = decode_dict(item)
#         rv.append(item)
#     return rv
#
# def decode_dict(data):
#     rv = {}
#     for key, value in data.iteritems():
#         if isinstance(key, unicode):
#             key = key.encode('utf-8')
#         if isinstance(value, unicode):
#             value = value.encode('utf-8')
#         elif isinstance(value, list):
#             value = _decode_list(value)
#         elif isinstance(value, dict):
#             value = decode_dict(value)
#         rv[key] = value
#     return rv


def decode_unicode(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(decode_unicode, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(decode_unicode, data))
    else:
        return data
