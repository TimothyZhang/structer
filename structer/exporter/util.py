# coding=utf-8
import re


def camel_case_to_underscore(name):
    words = re.findall('[A-Z][a-z0-9]*', name)
    assert ''.join(words) == name, 'invalid class/struct name: %s' % name
    return '_'.join(map(unicode.lower, words))
