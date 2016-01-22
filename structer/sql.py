# Copyright 2014 Timothy Zhang(zt@live.cn).
#
# This file is part of Structer.
#
# Structer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Structer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Structer.  If not, see <http://www.gnu.org/licenses/>.


"""
SQL(Structer Query Language) is a string used to search objects in structer project. Basically it's a python
expression, with all the properties of object as variables, and some extra properties and predefined functions. built-in
functions are also available.

e.g.:
  keyword('abc')
  10<=id<=100
  level>10 and len(cost)>5 or id==1000
  tag='OK'
  modified_time<time.time()
  tag in ['OK', 'New Year']

specially, ":xxx" is a convenient way to write "keyword('xxx')"

extra properties:
  tag: str
  modify_time: float
  create_time: float

predefined functions:
  keyword(str): id or name matches the str
  ref(uuid): references another object, specified by its uuid
  refby(uuid): referenced by another object
  now(): current timestamp, in seconds.

"""
import copy

import functools
from structer.pinyin import get_pinyin
import time


def parse_sql(project, sql):
    """
    Parse a sql express, and returns a function which accepts an object.
    :param sql:
    :type sql: str
    :return: function(object) -> bool
    :rtype: function
    """
    assert sql and isinstance(sql, (str, unicode))
    if sql[0] == ':':
        sql = "keyword('%s')" % sql[1:]

    return functools.partial(test_object, project, sql)


def test_object(project, sql, obj):
    def keyword(kw):
        return test_object_with_keyword(obj, kw)

    def ref(uuid):
        return obj.uuid in project.ref_manager.get_referents(uuid)

    def refby(uuid):
        return obj.uuid in project.ref_manager.get_references(uuid)

    locals_ = {
        'now': time.time,
        'keyword': keyword,
        'ref': ref,
        'refby': refby
    }
    # print sql
    return eval(sql, copy.copy(obj.raw_data), locals_)


def test_object_with_keyword(obj, keyword):
    """Check whether the given object's name or id or uuid matches keyword
    If object name is a dict, each value will be checked.

    :type obj: Object
    :type keyword: str
    :return: whether the object matches the specified keyword
    :rtype: bool
    """
    # name
    if obj.struct.has_attr('name'):
        name = obj.get_attr_value('name')
        if type(name) is dict:
            for lang, n in name.iteritems():
                if test_str_with_keyword(n.lower(), keyword, lang):
                    return True
        else:
            if test_str_with_keyword(name.lower(), keyword, None):
                return True

    # id
    if obj.id:
        if keyword in unicode(obj.id):
            return True

    # keyword search failed
    return False


def test_str_with_keyword(str_, keyword, lang):
    """Check whether str_ matches keyword

    We say it match if:
        str_ contains keyword, or
        first letter of pinyin str_ contains keyword, if lang is "cn" or None(language not specified)

    :param str_: the str to be tested
    :type str_: unicode
    :type keyword: unicode
    :param lang: language code, could be None.
    :type lang: str|None
    :rtype: bool
    """
    if keyword in str_:
        return True

    if lang == 'cn' or lang is None:
        for pinyin in get_pinyin(str_):
            if keyword in pinyin:
                return True

    return False